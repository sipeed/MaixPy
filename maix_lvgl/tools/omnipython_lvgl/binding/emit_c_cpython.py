# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Main CPython emit loop (PyObject* API); calls cpython_glue and cpython_native."""
from __future__ import print_function

import collections
import copy
import re
from os.path import commonprefix

from pycparser import c_ast, c_generator, c_parser

from .analyze import (
    MissingConversionException,
    get_base_struct_name,
    get_ctor,
    get_enum_member_name,
    get_enum_members,
    get_enum_value,
    get_first_arg_type,
    get_methods,
    get_struct_functions,
    has_ctor,
    is_static_member,
    is_struct_function,
    noncommon_part,
)
from .helpers import (
    collect_enum_referenced,
    ctor_name_from_obj_name,
    get_enum_name,
    is_global_callback,
    is_method_of,
    is_obj_ctor,
    is_struct,
    is_widget_scoped_only_enum,
    method_name_from_func_name,
    obj_name_from_ext_name,
    obj_name_from_func_name,
    sanitize,
    simplify_identifier,
    str_enum_to_str,
)
from .parse import (
    add_default_declname,
    convert_array_to_ptr,
    function_prototype,
    get_name,
    get_type,
    remove_arg_names,
    remove_declname,
    remove_explicit_struct,
    remove_quals,
)
from . import runtime
from .emit_backend import (
    TypeDiscovery,
    callback_return_conversion_available,
    callback_return_lowering,
    function_return_lowering,
    failed_generation,
    object_generation_order,
    require_target_lowering,
    resolve_emitter_headers,
    struct_pointer_helpers_source,
    target_banner,
)
from .runtime_exports import filter_module_funcs_for_target, filter_registration_module_funcs
from .util import eprint, memoize
from .context import EmitterResult


def emit_c(ctx):
    """Emit CPython C from one context without module-level run state."""
    print = ctx.emit_print
    args = ctx.args
    blobs = ctx.blobs
    cmd_line = ctx.cmd_line
    enum_defs = ctx.enum_defs
    func_typedefs = ctx.func_typedefs
    funcs = ctx.funcs
    gen = ctx.gen
    int_constants = ctx.int_constants
    lv_mp_type = ctx.lv_mp_type
    lv_str_enum_pattern = ctx.lv_str_enum_pattern
    lv_to_mp = ctx.lv_to_mp
    lv_to_mp_byref = ctx.lv_to_mp_byref
    lv_to_mp_funcptr = ctx.lv_to_mp_funcptr
    lvgl_json = ctx.lvgl_json
    module_name = ctx.module_name
    mp_to_lv = ctx.mp_to_lv
    obj_names = ctx.obj_names
    parent_obj_names = ctx.parent_obj_names
    pp_cmd = ctx.pp_cmd
    structs = ctx.structs
    synonym = ctx.synonym
    typedefs = ctx.typedefs

    generated_structs = getattr(ctx, "generated_structs", collections.OrderedDict())
    generated_struct_functions = ctx.generated_struct_functions
    struct_aliases = ctx.struct_aliases
    callbacks_used_on_structs = ctx.callbacks_used_on_structs
    generated_callbacks = ctx.generated_callbacks
    generated_funcs = ctx.generated_funcs
    enum_referenced = ctx.enum_referenced
    generated_obj_names = ctx.generated_obj_names
    generated_globals = ctx.generated_globals
    module_funcs = ctx.module_funcs
    functions_not_generated = ctx.functions_not_generated
    enums = getattr(ctx, "enums", collections.OrderedDict())

    headers = resolve_emitter_headers(args.input)

    _emit_target = "cpython"
    _emit_max_phase = require_target_lowering(_emit_target)
    _target_banner = target_banner(_emit_target, include=True)

    print(
        """
/*
 * Auto-Generated file, DO NOT EDIT!
 *
{target_banner} * Command line:
 * {cmd_line}
 *
 * Preprocessing command:
 * {pp_cmd}
 *
 * Generating Objects: {objs}
 */

/*
 * CPython includes
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdlib.h>
#include <string.h>
#include "lvpy_runtime.h"

/*
 * {module_name} includes
 */

{lv_headers}
""".format(
        module_name=module_name,
        target_banner=_target_banner,
        cmd_line=cmd_line,
            pp_cmd=pp_cmd,
            objs=", ".join(
                ["%s(%s)" % (objname, parent_obj_names[objname]) for objname in obj_names]
            ),
            lv_headers="\n".join('#include "%s"' % header for header in headers),
        )
    )

    #
    # Enable objects, if supported
    #

    if len(obj_names) > 0 and (_emit_max_phase is None or _emit_max_phase >= 5):
        print(
            """
#define LV_OBJ_T lv_obj_t
"""
        )

    # Helper functions live in lvpy_runtime.c — except the string-array
    # argument converter, which is emitted here so the generated file and
    # the runtime need not be versioned together for it.
    print(
        """
/*
 * String-array arguments (const char * const map[] and friends).
 *
 * LVGL stores these pointers (lv_buttonmatrix_set_map keeps map_p; it never
 * copies), so the array and its strings must outlive the call. A Python
 * sequence of str converts to a NULL-terminated char*[] whose array (via a
 * capsule) and string objects are retained on the widget's callback dict
 * under a per-function key: the pointers live exactly as long as the widget,
 * and a repeat call for the same function releases the previous retention.
 * Non-sequence inputs fall through to mp_to_ptr (blob passthrough / the
 * usual TypeError).
 */

static void lvpy_str_arr_capsule_free(PyObject *capsule)
{
    PyMem_Free(PyCapsule_GetPointer(capsule, NULL));
}

static void *lvpy_str_arr_arg(PyObject *self, PyObject *arg, const char *key)
{
    if (!arg || arg == Py_None) return NULL;
    if (PyUnicode_Check(arg) || PyBytes_Check(arg) || !PySequence_Check(arg))
        return mp_to_ptr(arg);
    PyObject *items = PySequence_Tuple(arg);
    if (!items) return NULL;
    Py_ssize_t n = PyTuple_GET_SIZE(items);
    const char **arr = (const char **)PyMem_Malloc(((size_t)n + 1) * sizeof(char *));
    if (!arr) { Py_DECREF(items); PyErr_NoMemory(); return NULL; }
    for (Py_ssize_t i = 0; i < n; i++) {
        PyObject *item = PyTuple_GET_ITEM(items, i);
        const char *s = PyUnicode_Check(item) ? PyUnicode_AsUTF8(item) : NULL;
        if (!s) {
            PyMem_Free(arr);
            Py_DECREF(items);
            if (!PyErr_Occurred())
                PyErr_Format(PyExc_TypeError,
                             "sequence of str expected; item %zd is '%s'",
                             i, Py_TYPE(item)->tp_name);
            return NULL;
        }
        arr[i] = s;
    }
    arr[n] = NULL;
    PyObject *capsule = PyCapsule_New((void *)arr, NULL, lvpy_str_arr_capsule_free);
    if (!capsule) { PyMem_Free(arr); Py_DECREF(items); return NULL; }
    PyObject *pair = PyTuple_Pack(2, items, capsule);
    Py_DECREF(items);
    Py_DECREF(capsule);
    if (!pair) return NULL;
    PyObject *callbacks = mp_get_callbacks(self);
    int rc = callbacks ? PyDict_SetItemString(callbacks, key, pair) : -1;
    Py_DECREF(pair);
    if (rc != 0) return NULL;
    return (void *)arr;
}

/*
 * Struct-array arguments (const lv_point_precise_t points[] and friends).
 *
 * A list or tuple of structs (or dicts, as for a struct argument) converts to
 * a C array, the way MicroPython converts it; anything else goes through
 * mp_to_ptr, so a packed buffer still works. LVGL may keep the pointer
 * (lv_line_set_points does), so the array or buffer is retained under a
 * per-function key: on the widget's callback dict when self is a widget,
 * else in a module dict keyed by self's address. A repeat call for the same
 * function releases the previous one.
 */

typedef void *(*lvpy_struct_writer_t)(PyObject *);

static PyObject *lvpy_struct_arr_keep;

static int lvpy_struct_arr_retain(PyObject *self, const char *key, PyObject *keep)
{
#ifdef LV_OBJ_T
    if (self && PyObject_TypeCheck(self, &py_lv_obj_type)) {
        PyObject *callbacks = mp_get_callbacks(self);
        return callbacks ? PyDict_SetItemString(callbacks, key, keep) : -1;
    }
#endif
    if (!lvpy_struct_arr_keep && !(lvpy_struct_arr_keep = PyDict_New())) return -1;
    PyObject *k = PyUnicode_FromFormat("%p:%s", (void *)self, key);
    if (!k) return -1;
    int rc = PyDict_SetItem(lvpy_struct_arr_keep, k, keep);
    Py_DECREF(k);
    return rc;
}

static void *lvpy_struct_arr_arg(PyObject *self, PyObject *arg, const char *key,
                                 size_t elem_size, lvpy_struct_writer_t write)
{
    if (!arg || arg == Py_None) return NULL;
    void *arr;
    PyObject *keep;
    if (PyList_Check(arg) || PyTuple_Check(arg)) {
        PyObject *items = PySequence_Tuple(arg);
        if (!items) return NULL;
        Py_ssize_t n = PyTuple_GET_SIZE(items);
        arr = PyMem_Malloc(n ? (size_t)n * elem_size : 1);
        if (!arr) { Py_DECREF(items); PyErr_NoMemory(); return NULL; }
        for (Py_ssize_t i = 0; i < n; i++) {
            void *p = write(PyTuple_GET_ITEM(items, i));
            if (PyErr_Occurred()) { PyMem_Free(arr); Py_DECREF(items); return NULL; }
            memcpy((char *)arr + (size_t)i * elem_size, p, elem_size);
        }
        Py_DECREF(items);
        keep = PyCapsule_New(arr, NULL, lvpy_str_arr_capsule_free);
        if (!keep) { PyMem_Free(arr); return NULL; }
    } else {
        arr = mp_to_ptr(arg);
        if (PyErr_Occurred()) return NULL;
        Py_INCREF(arg);
        keep = arg;
    }
    int rc = lvpy_struct_arr_retain(self, key, keep);
    Py_DECREF(keep);
    if (rc != 0) return NULL;
    return arr;
}

/*
 * Fixed-size struct arrays inside a struct (lv_point_precise_t p[3]).
 *
 * Reading the field gives a view over the parent struct's memory, so
 * d.p[1].x = 7 and d.p[1] = point write through, and len(d.p) works. The view
 * holds the parent so the memory stays alive. Assigning the field takes a
 * sequence of exactly that many structs (or dicts), or a packed buffer of the
 * array's size; anything else raises and leaves the field unchanged
 * (lvgl-bindings#38).
 */

typedef PyObject *(*lvpy_struct_reader_t)(void *);

typedef struct {
    PyObject_HEAD
    PyObject *owner;
    char *data;
    Py_ssize_t len;
    size_t elem_size;
    lvpy_struct_reader_t read;
    lvpy_struct_writer_t write;
} lvpy_struct_array_t;

static void lvpy_struct_array_dealloc(PyObject *self)
{
    Py_XDECREF(((lvpy_struct_array_t *)self)->owner);
    Py_TYPE(self)->tp_free(self);
}

static Py_ssize_t lvpy_struct_array_len(PyObject *self)
{
    return ((lvpy_struct_array_t *)self)->len;
}

static PyObject *lvpy_struct_array_item(PyObject *self_in, Py_ssize_t i)
{
    lvpy_struct_array_t *self = (lvpy_struct_array_t *)self_in;
    if (i < 0 || i >= self->len) {
        PyErr_SetString(PyExc_IndexError, "struct array index out of range");
        return NULL;
    }
    return self->read(self->data + (size_t)i * self->elem_size);
}

static int lvpy_struct_array_ass_item(PyObject *self_in, Py_ssize_t i, PyObject *value)
{
    lvpy_struct_array_t *self = (lvpy_struct_array_t *)self_in;
    if (value == NULL) {
        PyErr_SetString(PyExc_TypeError, "can't delete struct array items");
        return -1;
    }
    if (i < 0 || i >= self->len) {
        PyErr_SetString(PyExc_IndexError, "struct array assignment index out of range");
        return -1;
    }
    void *p = self->write(value);
    if (PyErr_Occurred()) return -1;
    memcpy(self->data + (size_t)i * self->elem_size, p, self->elem_size);
    return 0;
}

static PySequenceMethods lvpy_struct_array_as_sequence = {
    .sq_length = lvpy_struct_array_len,
    .sq_item = lvpy_struct_array_item,
    .sq_ass_item = lvpy_struct_array_ass_item,
};

/* dir() on a struct instance: what object.__dir__ finds, plus the fields and
 * methods the struct's getattro resolves by name (lvgl-bindings#40). */
static inline PyObject *lvpy_struct_dir(PyObject *self, const char *const *fields,
    PyMethodDef *methods)
{
    PyObject *names = PyObject_CallMethod((PyObject *)&PyBaseObject_Type, "__dir__", "O", self);
    if (names == NULL) return NULL;
    PyObject *list = PySequence_List(names);
    Py_DECREF(names);
    if (list == NULL) return NULL;
    for (; *fields != NULL; fields++) {
        PyObject *s = PyUnicode_FromString(*fields);
        if (s == NULL || PyList_Append(list, s) < 0) { Py_XDECREF(s); Py_DECREF(list); return NULL; }
        Py_DECREF(s);
    }
    for (; methods->ml_name != NULL; methods++) {
        PyObject *s = PyUnicode_FromString(methods->ml_name);
        if (s == NULL || PyList_Append(list, s) < 0) { Py_XDECREF(s); Py_DECREF(list); return NULL; }
        Py_DECREF(s);
    }
    return list;
}

static PyTypeObject lvpy_struct_array_type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "lvgl.StructArray",
    .tp_basicsize = sizeof(lvpy_struct_array_t),
    .tp_dealloc = lvpy_struct_array_dealloc,
    .tp_as_sequence = &lvpy_struct_array_as_sequence,
    .tp_flags = Py_TPFLAGS_DEFAULT,
};

static inline PyObject *lvpy_struct_array_new(PyObject *owner, void *data,
    Py_ssize_t len, size_t elem_size, lvpy_struct_reader_t read, lvpy_struct_writer_t write)
{
    if (!(lvpy_struct_array_type.tp_flags & Py_TPFLAGS_READY) &&
        PyType_Ready(&lvpy_struct_array_type) < 0)
        return NULL;
    lvpy_struct_array_t *self = PyObject_New(lvpy_struct_array_t, &lvpy_struct_array_type);
    if (!self) return NULL;
    Py_XINCREF(owner);
    self->owner = owner;
    self->data = (char *)data;
    self->len = len;
    self->elem_size = elem_size;
    self->read = read;
    self->write = write;
    return (PyObject *)self;
}

/* Sets an exception and leaves data unchanged on any mismatch. */
static inline void lvpy_struct_array_assign(void *data, Py_ssize_t len,
    size_t elem_size, lvpy_struct_writer_t write, PyObject *value)
{
    size_t total = (size_t)len * elem_size;
    if (PyBytes_Check(value) || PyByteArray_Check(value) || PyMemoryView_Check(value)) {
        Py_buffer view;
        if (PyObject_GetBuffer(value, &view, PyBUF_C_CONTIGUOUS) < 0) return;
        if ((size_t)view.len != total)
            PyErr_Format(PyExc_ValueError, "expected a buffer of %zu bytes, got %zd",
                         total, view.len);
        else
            memcpy(data, view.buf, total);
        PyBuffer_Release(&view);
        return;
    }
    if (!PySequence_Check(value) || PyUnicode_Check(value)) {
        PyErr_Format(PyExc_TypeError, "expected a sequence of %zd structs, got '%s'",
                     len, Py_TYPE(value)->tp_name);
        return;
    }
    PyObject *items = PySequence_Tuple(value);
    if (!items) return;
    if (PyTuple_GET_SIZE(items) != len) {
        PyErr_Format(PyExc_ValueError, "expected %zd items, got %zd",
                     len, PyTuple_GET_SIZE(items));
        Py_DECREF(items);
        return;
    }
    /* Convert every item before writing any, so a bad item changes nothing. */
    char *tmp = (char *)PyMem_Malloc(total ? total : 1);
    if (!tmp) { Py_DECREF(items); PyErr_NoMemory(); return; }
    for (Py_ssize_t i = 0; i < len; i++) {
        void *p = write(PyTuple_GET_ITEM(items, i));
        if (PyErr_Occurred()) { PyMem_Free(tmp); Py_DECREF(items); return; }
        memcpy(tmp + (size_t)i * elem_size, p, elem_size);
    }
    memcpy(data, tmp, total);
    PyMem_Free(tmp);
    Py_DECREF(items);
}
"""
    )

    #
    # Add regular enums with integer values
    #

    enums = collections.OrderedDict()
    for enum_def in enum_defs:
        # Skip stdatomic.h memory_order, no bindings needed.
        if isinstance(enum_def, c_ast.TypeDecl) and enum_def.declname == "memory_order":
            continue

        # eprint("--> %s" % enum_def)
        while hasattr(enum_def.type, "name") and not enum_def.type.values:
            enum_def = next(
                e
                for e in enum_defs
                if hasattr(e.type, "name")
                and e.type.name == enum_def.type.name
                and e.type.values
            )
        member_names = [
            member.name
            for member in enum_def.type.values.enumerators
            if not member.name.startswith("_")
        ]
        enum_name = commonprefix(member_names)
        enum_name = "_".join(enum_name.split("_")[:-1])  # remove suffix
        enum = collections.OrderedDict()
        for member in enum_def.type.values.enumerators:
            if member.name.startswith("_"):
                continue
            member_name = (
                member.name[len(enum_name) + 1 :] if len(enum_name) > 0 else member.name
            )
            if member_name[0].isdigit():
                member_name = "_" + member_name
            if len(enum_name) > 0 and get_enum_name(enum_name) != "ENUM":
                enum[member_name] = "MP_ROM_INT(%s)" % member.name
            else:
                int_constants.append(member.name)
        if len(enum) > 0:
            if len(get_enum_name(enum_name)) > 0:
                prev_enum = enums.get(enum_name)
                if prev_enum:
                    prev_enum.update(enum)
                else:
                    enums[enum_name] = enum

    for enum in [
        enum for enum in enums if len(enums[enum]) == 1 and enum.startswith("ENUM")
    ]:
        int_constants.append("%s_%s" % (enum, next(iter(enums[enum]))))
        del enums[enum]

    # Add special string enums

    generated_globals = []

    print(
        """
/*
 * LVGL string constants
 */
"""
    )

    for enum_def in enum_defs:
        if not enum_def.type.values:
            continue
        member_names = [
            str_enum_to_str(member.name)
            for member in enum_def.type.values.enumerators
            if lv_str_enum_pattern.match(member.name)
        ]
        enum_name = commonprefix(member_names)
        enum_name = "_".join(enum_name.split("_")[:-1])  # remove suffix
        enum = collections.OrderedDict()
        if enum_name:
            for member in enum_def.type.values.enumerators:
                full_name = str_enum_to_str(member.name)
                member_name = full_name[len(enum_name) + 1 :]
                generated_globals.append(full_name)
                enum[member_name] = full_name
            if len(enum) > 0:
                if enum_name in enums:
                    enums[enum_name].update(enum)
                else:
                    enums[enum_name] = enum


    # eprint('--> enums: \n%s' % enums)

    runtime.set_("enums", enums)

    # eprint(',\n'.join(sorted('%s : %s' % (name, get_type(blobs[name])) for name in blobs)))

    #
    # Callbacks helper functions
    #


    def decl_to_callback(decl):
        # print('/* decl_to_callback %s */' % decl)
        if not hasattr(decl, "type"):
            return None
        if isinstance(decl.type, c_ast.PtrDecl) and isinstance(
            decl.type.type, c_ast.FuncDecl
        ):
            return (decl.name, decl.type.type)
            # print('/* callback: ADDED CALLBACK: %s\n%s */' % (gen.visit(decl.type.type), decl.type.type))
        elif isinstance(decl.type, c_ast.FuncDecl):
            return (decl.name, decl.type)
            # print('/* callback: ADDED CALLBACK: %s\n%s */' % (gen.visit(decl.type.type), decl.type.type))
        elif isinstance(decl.type, c_ast.TypeDecl) and hasattr(decl.type.type, "names"):
            func_typedef_name = decl.type.type.names[0]
            while func_typedef_name in synonym:
                # eprint('decl_to_callback: %s --> %s' % (func_typedef_name, synonym[func_typedef_name]))
                func_typedef_name = synonym[func_typedef_name]
            # print('/* --> callback: TYPEDEF CALLBACK: %s: %s */' % (decl.name if hasattr(decl, 'name') else None, func_typedef_name))
            if func_typedef_name in func_typedefs:
                return (decl.name, func_typedefs[func_typedef_name].type.type)
                # print('/* callback: ADDED CALLBACK: %s\n%s */' % (func_typedef_name, func_typedefs[func_typedef_name]))
        else:
            return None


    def get_user_data_accessors(containing_struct, containing_struct_name=None):
        if not containing_struct_name and containing_struct and containing_struct.name:
            containing_struct_name = containing_struct.name
        if not containing_struct_name:
            return None, None
        base_struct_name = get_base_struct_name(containing_struct_name)
        getter_name = base_struct_name + "_get_user_data"
        setter_name = base_struct_name + "_set_user_data"
        # print('/* struct functions = %s */' % [s.name + ':' + str(len(s.type.args.params)) for s in get_struct_functions(containing_struct_name)])
        # print('/* getter_name = %s */' % getter_name)
        struct_functions = get_struct_functions(containing_struct_name)
        getters = [
            s
            for s in struct_functions
            if s.name == getter_name and len(s.type.args.params) == 1
        ]
        setters = [
            s
            for s in struct_functions
            if s.name == setter_name and len(s.type.args.params) == 2
        ]
        if getters and setters:
            return getters[0], setters[0]
        else:
            return None, None


    def get_user_data(
        func, func_name=None, containing_struct=None, containing_struct_name=None
    ):
        args = func.args.params
        if not func_name:
            func_name = get_arg_name(func.type)
        # print('/* --> callback: func_name = %s, args = %s */' % (func_name, repr(args)))
        user_data_found = False
        user_data = "None"
        if len(args) > 0 and isinstance(args[0].type, c_ast.PtrDecl):
            # if isinstance(args[0].type.type.type, c_ast.Struct):
            #     struct_arg_type_name = args[0].type.type.type.name # PtrDecl.TypeDecl.Struct. Needed to omit 'struct' keyword.
            # else:
            #     struct_arg_type_name = get_type(args[0].type.type, remove_quals = True)
            struct_arg_type_name = get_type(args[0].type.type, remove_quals=True)
            # print('/* --> get_user_data: containing_struct_name = %s, struct_arg_type_name = %s */' % (containing_struct_name, struct_arg_type_name))
            if containing_struct_name and struct_arg_type_name != containing_struct_name:
                return None, None, None
            if not containing_struct:
                try_generate_type(args[0].type)
                if struct_arg_type_name in structs:
                    containing_struct = structs[struct_arg_type_name]
                    # print('/* --> containing_struct = %s */' % containing_struct)
                # if struct_arg_type_name in mp_to_lv:
                #     print('/* --> callback: %s First argument is %s */' % (gen.visit(func), struct_arg_type_name))
            if containing_struct:
                flatten_struct_decls = flatten_struct(containing_struct.decls)
                user_data = "user_data"
                user_data_found = user_data in [decl.name for decl in flatten_struct_decls]
                # print('/* --> callback: user_data=%s user_data_found=%s containing_struct=%s */' % (user_data, user_data_found, containing_struct))
                if not user_data_found and lvgl_json is not None:
                    containing_struct_j = next(
                        (
                            struct
                            for struct in lvgl_json["structures"]
                            if struct["name"] == struct_arg_type_name
                        ),
                        None,
                    )
                    if (
                        containing_struct_j is None
                        and struct_arg_type_name.startswith("lv_")
                        and None
                        is not next(
                            (
                                fwd_decl
                                for fwd_decl in lvgl_json["forward_decls"]
                                if fwd_decl["name"] == struct_arg_type_name
                            ),
                            None,
                        )
                    ):
                        struct_arg_type_name_with_underscore = "_" + struct_arg_type_name
                        containing_struct_j = next(
                            (
                                struct
                                for struct in lvgl_json["structures"]
                                if struct["name"] == struct_arg_type_name_with_underscore
                            ),
                            None,
                        )
                    if containing_struct_j is not None:
                        user_data_found = any(
                            user_data == field["name"]
                            for field in containing_struct_j["fields"]
                        )
        return (user_data if user_data_found else None), *get_user_data_accessors(
            containing_struct, containing_struct_name
        )


    #
    # Generate structs when needed
    #

    generated_structs = collections.OrderedDict()
    generated_struct_functions = collections.OrderedDict()
    generated_struct_method_funcs = collections.OrderedDict()
    struct_aliases = collections.OrderedDict()
    callbacks_used_on_structs = []
    runtime.set_("generated_structs", generated_structs)
    runtime.set_("generated_struct_functions", generated_struct_functions)
    runtime.set_("generated_struct_method_funcs", generated_struct_method_funcs)
    runtime.set_("struct_aliases", struct_aliases)
    runtime.set_("callbacks_used_on_structs", callbacks_used_on_structs)


    def flatten_struct(struct_decls):
        result = []
        if not struct_decls:
            return result
        for decl in struct_decls:
            if is_struct(decl.type):
                result.extend(flatten_struct(decl.type.decls))
            else:
                result.append(decl)
        return result


    def try_generate_struct(struct_name, struct):
        from .emit_cpython_native import try_generate_struct_cpython

        return try_generate_struct_cpython(struct_name, struct)


    def try_generate_array_type(type_ast):
        return None


    generated_funcptr_helpers = collections.OrderedDict()


    def emit_function_pointer(helper_name, func):
        print("#define %s NULL\n" % helper_name)
        print(
            "static inline PyObject *mp_lv_{f}(void *func){{ return "
            "mp_lv_funcptr(NULL, func, NULL, \"\", NULL); }}\n".format(
                f=helper_name
            )
        )
        return True


    type_discovery = TypeDiscovery(
        get_name=get_name,
        get_type=get_type,
        structs=structs,
        typedefs=typedefs,
        struct_aliases=struct_aliases,
        mp_to_lv=mp_to_lv,
        lv_to_mp=lv_to_mp,
        lv_mp_type=lv_mp_type,
        lv_to_mp_byref=lv_to_mp_byref,
        lv_to_mp_funcptr=lv_to_mp_funcptr,
        generated_funcptr_helpers=generated_funcptr_helpers,
        try_generate_struct=try_generate_struct,
        try_generate_array=try_generate_array_type,
        emit_function_pointer=emit_function_pointer,
        missing_conversion=MissingConversionException,
        report_error=lambda func, exp: gen_func_error(func, exp),
    )
    get_arg_name = type_discovery.typedef_name


    def try_generate_type(type_ast):
        return type_discovery.generate(type_ast)


    #
    # Emit C callback functions
    #

    generated_callbacks = collections.OrderedDict()
    generated_funcs = collections.OrderedDict()

    if _emit_max_phase is None or _emit_max_phase > 1:

        if _emit_max_phase is not None and _emit_max_phase >= 2:
            from .emit_cpython_glue import emit_phase2_enums_cpython

            emit_phase2_enums_cpython()

        if _emit_max_phase is None or _emit_max_phase >= 4:

            def gen_callback_func(func, func_name=None, user_data_argument=False):
                from .emit_cpython_native import gen_callback_func_cpython

                return gen_callback_func_cpython(func, func_name, user_data_argument)


            generated_funcs = collections.OrderedDict()


            def gen_mp_func(func, obj_name):
                from .emit_cpython_native import gen_py_func

                return gen_py_func(func, obj_name)


            def gen_func_error(method, exp):
                diagnostic, funcs = failed_generation(
                    method=method,
                    problem=exp,
                    funcs=runtime.get("funcs"),
                    render_method=lambda value: (
                        gen.visit(value) if isinstance(value, c_ast.Node) else value
                    ),
                    api_model=runtime.get("api_model"),
                    target=_emit_target,
                )
                print(diagnostic)
                runtime.set_("funcs", funcs)


        #
        # Emit Mpy objects definitions
        #

        enum_referenced = collections.OrderedDict()


        def gen_obj(obj_name):
            from .emit_cpython_native import gen_py_obj

            return gen_py_obj(obj_name)


        #
        # Generate Enum objects
        #

        if _emit_max_phase is None:
            for enum_name in list(enums.keys()):
                gen_obj(enum_name)

        #
        # Generate all other objects. Generate parent objects first
        #

        if _emit_max_phase is None or _emit_max_phase >= 5:

            from .emit_cpython_native import bind_emit_helpers

            bind_emit_helpers(locals())

            generated_obj_names = collections.OrderedDict()
            for obj_name in object_generation_order(obj_names, parent_obj_names):
                gen_obj(obj_name)
                generated_obj_names[obj_name] = True

            from .emit_cpython_native import bound_helper

            _gf = bound_helper("generated_funcs")
            if _gf is not None:
                generated_funcs = _gf
            runtime.set_("generated_funcs", generated_funcs)

    #
    # Generate structs which contain function members
    # First argument of a function could be it's parent struct
    # Need to make sure these structs are generated *before* struct-functions are
    # Otherwise we will not know of all the structs when generating struct-functions
    #


    def try_generate_structs_from_first_argument():
        for func in funcs:
            if func.name in generated_funcs:
                continue
            args = func.type.args.params if func.type.args else []
            if len(args) < 1:
                continue
            arg_type = get_type(args[0].type, remove_quals=True)
            if arg_type not in mp_to_lv or not mp_to_lv[arg_type]:
                try:
                    try_generate_type(args[0].type)
                except MissingConversionException as e:
                    print(
                        """
/*
 * {struct} not generated: {err}
 */
                """.format(struct=arg_type, err=e)
                    )


    #
    # Generate globals
    #

    # eprint("/* Generating globals */")


    def gen_func_error(method, exp):
        diagnostic, funcs = failed_generation(
            method=method,
            problem=exp,
            funcs=runtime.get("funcs"),
            render_method=lambda value: (
                gen.visit(value) if isinstance(value, c_ast.Node) else value
            ),
            api_model=runtime.get("api_model"),
            target=_emit_target,
        )
        print(diagnostic)
        runtime.set_("funcs", funcs)

    def _emit_cpython_struct_methods(struct_list=None):
        from .emit_cpython_native import (
            emit_struct_methods_cpython,
            gen_py_func,
            _resolved_struct_method_py_func_name,
        )

        if struct_list is None:
            struct_names = list(generated_structs.keys())
        else:
            struct_names = struct_list
        for struct_name in struct_names:
            if not generated_structs.get(struct_name):
                continue
            if generated_struct_functions.get(struct_name):
                continue
            struct_funcs = list(get_struct_functions(struct_name))
            method_entries = []
            seen_method_names = set()
            for struct_func in struct_funcs:
                try:
                    emit_name = struct_func.name + "_struct_method"
                    if generated_struct_method_funcs.get(emit_name) is not True:
                        gen_py_func(struct_func, struct_name)
                    resolved = _resolved_struct_method_py_func_name(
                        struct_func.name, generated_struct_method_funcs
                    )
                    if not resolved:
                        continue
                    method_name = sanitize(
                        noncommon_part(struct_func.name, struct_name)
                    )
                    if method_name in seen_method_names:
                        continue
                    seen_method_names.add(method_name)
                    method_entries.append((resolved, method_name))
                except MissingConversionException as exp:
                    gen_func_error(struct_func, exp)
            emit_struct_methods_cpython(struct_name, method_entries)
            generated_struct_functions[struct_name] = True


    def _emit_struct_locals_dicts(include_methods=False, struct_list=None):
        return None


    def gen_global(global_name, global_type_ast):
        global_type = get_type(global_type_ast, remove_quals=True)
        if global_name == "_nesting":
            return
        try_generate_type(global_type_ast)
        cpython_global_types = runtime.get(
            "cpython_global_types", collections.OrderedDict()
        )
        cpython_global_types[global_name] = (
            global_type if generated_structs.get(global_type, False) else None
        )
        runtime.set_("cpython_global_types", cpython_global_types)
        generated_globals.append(global_name)


    for global_name in blobs:
        try:
            gen_global(global_name, blobs[global_name])
        except MissingConversionException as exp:
            gen_func_error(global_name, exp)

    if _emit_max_phase is None or _emit_max_phase >= 4:
        from .emit_cpython_native import bind_emit_helpers, bound_helper

        _gf = bound_helper("generated_funcs")
        if _gf is not None:
            generated_funcs = _gf
        bind_emit_helpers(locals())
        try_generate_structs_from_first_argument()
        _emit_struct_locals_dicts(include_methods=True)

    if _emit_max_phase is None or _emit_max_phase >= 6:
        #
        # Generate all module functions (not including method functions which were already generated)
        #

        print(
            """
/*
 *
 * Global Module Functions
 *
 */
"""
        )

        # eprint("/* Generating global module functions /*")
        from .emit_cpython_native import bound_helper

        _candidates = [
            generated_funcs,
            runtime.get("generated_funcs", {}),
            bound_helper("generated_funcs", {}),
        ]
        generated_funcs = max(_candidates, key=len)
        module_funcs = [func for func in funcs if func.name not in generated_funcs]
        module_funcs = filter_module_funcs_for_target(
            module_funcs, _emit_target, runtime.get("api_model")
        )
        runtime.set_("_cpython_module_exports", list(module_funcs))
        for module_func in module_funcs[
            :
        ]:  # clone list because we are changing it in the loop.
            if module_func.name in generated_funcs:
                continue  # generated_funcs could change inside the loop so need to recheck.
            try:
                gen_mp_func(module_func, None)
                # A new function can create new struct with new function structs
                new_structs = [
                    s
                    for s in generated_structs
                    if generated_structs[s] and not generated_struct_functions.get(s)
                ]
                if new_structs:
                    _emit_struct_locals_dicts(include_methods=True, struct_list=new_structs)
            except MissingConversionException as exp:
                gen_func_error(module_func, exp)
                module_funcs.remove(module_func)

        _emit_cpython_struct_methods()
        module_funcs = filter_registration_module_funcs(module_funcs)

        functions_not_generated = [
            func.name for func in funcs if func.name not in generated_funcs
        ]
        if len(functions_not_generated) > 0:
            print(
                """
/*
 * Functions not generated:
 * {funcs}
 *
 */

""".format(funcs="\n * ".join(functions_not_generated))
            )

    if _emit_max_phase is None or _emit_max_phase >= 7:
        #
        # Generate callback functions (struct field callbacks)
        #

        # eprint("/* Generating callback functions */")
        for func_name, func, struct_name in callbacks_used_on_structs:
            try:
                # print('/* --> gen_callback_func %s */' % func_name)
                gen_callback_func(func, func_name="%s_%s" % (struct_name, func_name))
            except MissingConversionException as exp:
                gen_func_error(func, exp)

        # Callback lowering can discover additional concrete structs after
        # phase 6.  Every generated CPython struct type references a method
        # table, including structs with no methods, so close that discovery
        # set before module initialization is emitted.
        while True:
            pending_struct_methods = [
                name
                for name, generated in generated_structs.items()
                if generated and not generated_struct_functions.get(name)
            ]
            if not pending_struct_methods:
                break
            _emit_cpython_struct_methods(pending_struct_methods)

    # Emit the CPython module definition.
        from .emit_cpython_glue import finish_py_module
        runtime.set_("generated_funcs", generated_funcs)
        runtime.set_("module_funcs", module_funcs)
        runtime.set_("generated_structs", generated_structs)
        runtime.set_("struct_aliases", struct_aliases)
        runtime.set_("generated_globals", generated_globals)
        runtime.set_("int_constants", int_constants)
        runtime.set_("obj_names", obj_names)
        runtime.set_(
            "enum_referenced",
            collect_enum_referenced(runtime.get("enums", {}), obj_names),
        )
        print(
            """
py_lv_obj_type_t *py_lv_obj_types[] = {{
    {obj_types}NULL
}};
""".format(
                obj_types=",\n    ".join(
                    ["&py_lv_%s_mapping" % sanitize(o) for o in obj_names]
                )
                + (",\n    " if obj_names and (_emit_max_phase is None or _emit_max_phase >= 5) else "")
                if len(obj_names) > 0 and (_emit_max_phase is None or _emit_max_phase >= 5)
                else "",
            )
        )
        finish_py_module(_emit_max_phase or 7)
        EmitterResult.capture(locals()).apply(ctx)
