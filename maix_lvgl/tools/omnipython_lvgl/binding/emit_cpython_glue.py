# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""CPython bookends: phase-2 enum types and PyInit_lvgl / module registration."""
from __future__ import print_function

import collections

from . import runtime
from .util import guarded
from .emit_backend import enum_namespace_plan, module_registration_plan, public_enum_module_names, public_struct_c_names


# This module owns no mirrored emitter globals; generated output is routed
# through the active run context explicitly.
print = runtime.emit
from .analyze import get_enum_member_name, get_enum_members, get_enum_value
from .emit_cpython_native import _resolved_py_func_name
from .helpers import export_name, get_enum_name, is_method_of, is_widget_scoped_only_enum, method_name_from_func_name, sanitize, simplify_identifier


def _member_c_value(value):
    if value.startswith("MP_ROM_INT(") and value.endswith(")"):
        return value[len("MP_ROM_INT(") : -1]
    if value.startswith("&mp_"):
        return value[len("&mp_") :]
    return value


def emit_phase2_enums_cpython():
    """Emit read-only enum namespace types (native CPython API)."""
    if runtime.get("_py_enums_emitted", False):
        return
    runtime.set_("_py_enums_emitted", True)
    enums = runtime.get("enums", {})
    obj_metadata = runtime.get("obj_metadata")
    enum_referenced = collections.OrderedDict()
    module_name = runtime.get("module_name", "lvgl")

    print(
        """
/*
 * CPython phase-2 enum namespace types
 *
 * Members resolve through each type's tp_getattro. __dir__ lists them from a
 * static name table, so dir(), help() and REPL completion can find them.
 */

static PyObject *lvpy_enum_dir(PyObject *self, const char *const *members)
{
    PyObject *base = PyObject_CallMethod((PyObject *)&PyBaseObject_Type, "__dir__", "O", self);
    if (base == NULL) {
        return NULL;
    }
    PyObject *names = PySequence_List(base);
    Py_DECREF(base);
    if (names == NULL) {
        return NULL;
    }
    for (const char *const *m = members; *m != NULL; m++) {
        PyObject *s = PyUnicode_FromString(*m);
        if (s == NULL || PyList_Append(names, s) < 0) {
            Py_XDECREF(s);
            Py_DECREF(names);
            return NULL;
        }
        Py_DECREF(s);
    }
    return names;
}
"""
    )

    for enum_plan in enum_namespace_plan(
        enums=enums,
        get_enum_members=get_enum_members,
        is_method_of=is_method_of,
        is_widget_scoped=is_widget_scoped_only_enum,
    ):
        enum_name = enum_plan.name
        members = enums[enum_name]
        if not members:
            continue
        obj_metadata[enum_name] = {"members": collections.OrderedDict()}
        obj_metadata[enum_name]["members"].update(
            {
                get_enum_member_name(enum_member_name): {"type": "enum_member"}
                for enum_member_name in enum_plan.members
            }
        )
        obj_enums = enum_plan.nested_names
        obj_metadata[enum_name]["members"].update(
            {
                method_name_from_func_name(other): {"type": "enum_type"}
                for other in obj_enums
            }
        )
        for other in obj_enums:
            if other in obj_metadata:
                obj_metadata[enum_name]["members"][
                    method_name_from_func_name(other)
                ].update(obj_metadata[other])
            if other in enum_plan.widget_scoped_nested_names:
                enum_referenced[other] = True
        safe = sanitize(enum_name)
        py_name = export_name(enum_name, "enum")

        print(
            """
static PyObject *py_lv_{safe}_getattro(PyObject *self, PyObject *name)
{{
    (void)self;
    if (!PyUnicode_Check(name)) {{
        PyErr_SetString(PyExc_TypeError, "attribute name must be string");
        return NULL;
    }}
    const char *attr = PyUnicode_AsUTF8(name);
    if (attr == NULL) {{
        return NULL;
    }}
""".format(safe=safe)
        )

        py_members = []
        for member_name, member_value in members.items():
            cval = _member_c_value(member_value)
            py_member = export_name(member_name, "enum_member")
            py_members.append(py_member)
            if cval.startswith("LV_SYMBOL_"):
                print(
                    '    if (strcmp(attr, "{member}") == 0) return PyUnicode_FromString({cval});'.format(
                        member=py_member, cval=cval
                    )
                )
            else:
                print(
                    '    if (strcmp(attr, "{member}") == 0) return PyLong_FromLong({cval});'.format(
                        member=py_member, cval=cval
                    )
                )

        print(
            """
    return PyObject_GenericGetAttr(self, name);
}}

static const char *const py_lv_{safe}_members[] = {{
{member_list}    NULL
}};

static PyObject *py_lv_{safe}_dir(PyObject *self, PyObject *Py_UNUSED(ignored))
{{
    return lvpy_enum_dir(self, py_lv_{safe}_members);
}}

static PyMethodDef py_lv_{safe}_methods[] = {{
    {{"__dir__", py_lv_{safe}_dir, METH_NOARGS, NULL}},
    {{NULL, NULL, 0, NULL}}
}};

static PyTypeObject py_lv_{safe}_type = {{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "{module}.{py_name}",
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_getattro = py_lv_{safe}_getattro,
    .tp_methods = py_lv_{safe}_methods,
    .tp_doc = "LVGL {py_name} enum namespace",
}};
""".format(
                module=module_name,
                py_name=py_name,
                safe=safe,
                member_list="".join('    "{}",\n'.format(m) for m in py_members),
            )
        )

    runtime.set_("obj_metadata", obj_metadata)
    runtime.set_("enum_referenced", enum_referenced)


def finish_py_module(max_phase):
    """Emit PyInit_lvgl and module-level registration (native CPython API)."""
    int_constants = runtime.get("int_constants", [])
    generated_globals = runtime.get("generated_globals", [])
    cpython_global_types = runtime.get("cpython_global_types", {})
    enums = runtime.get("enums", {})
    enum_referenced = runtime.get("enum_referenced", collections.OrderedDict())
    generated_structs = runtime.get("generated_structs", {})
    struct_aliases = runtime.get("struct_aliases", collections.OrderedDict())
    cpython_struct_sizes = runtime.get("cpython_struct_sizes", {})
    obj_names = runtime.get("obj_names", [])
    module_funcs = runtime.get("module_funcs", [])
    canonical_enum_names = public_enum_module_names(
        runtime.get("api_model"), "cpython"
    )
    registration = module_registration_plan(
        max_phase=max_phase,
        int_constants=int_constants,
        generated_globals=generated_globals,
        enums=enums,
        enum_referenced=enum_referenced,
        generated_structs=generated_structs,
        struct_aliases=struct_aliases,
        obj_names=obj_names,
        module_funcs=module_funcs,
        public_struct_names=public_struct_c_names(runtime.get("api_model"), "cpython"),
        public_enum_names=(
            frozenset(
                name
                for name in enums
                if export_name(name, "enum") in canonical_enum_names
            )
            if canonical_enum_names is not None
            else None
        ),
    )

    print(
        """
/*
 * CPython module definition
 */

static int lvgl_mod_initialized = 0;

/* A build of this module can run its own setup right after lv_init() by
 * defining LVPY_AFTER_LV_INIT as the name of a void(void) function: lvgl-python
 * registers jpegio's JPEG decoder there. A macro rather than a weak symbol, so
 * it works with every compiler a wheel is built with. */
#ifdef LVPY_AFTER_LV_INIT
extern void LVPY_AFTER_LV_INIT(void);
#endif

static PyObject *py_lvgl_init(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;
    lvpy_lock();
    if (!lvgl_mod_initialized) {
        lv_init();
#ifdef LVPY_AFTER_LV_INIT
        LVPY_AFTER_LV_INIT();
#endif
        lvgl_mod_initialized = 1;
    }
    lvpy_unlock();
    Py_RETURN_NONE;
}

static PyObject *py_lvgl_deinit(PyObject *self, PyObject *args)
{
    (void)self;
    (void)args;
    lvpy_lock();
    if (lvgl_mod_initialized) {
        lv_deinit();
        lvgl_mod_initialized = 0;
    }
    lvpy_unlock();
    Py_RETURN_NONE;
}

static PyMethodDef lvgl_methods[] = {
    {"init", py_lvgl_init, METH_NOARGS, "Initialize LVGL"},
    {"deinit", py_lvgl_deinit, METH_NOARGS, "Deinitialize LVGL"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef lvgl_module_def = {
    PyModuleDef_HEAD_INIT,
    "lvgl",
    "LVGL bindings for CPython (generated)",
    -1,
    lvgl_methods
};
"""
    )

    print("PyMODINIT_FUNC PyInit_lvgl(void)")
    print("{")
    print("    PyObject *m = PyModule_Create(&lvgl_module_def);")
    print("    if (m == NULL) {")
    print("        return NULL;")
    print("    }")
    # Free-threaded builds re-enable the GIL on import unless the module
    # says it doesn't need it. LVGL itself isn't thread-safe; the rule that
    # makes this safe is one thread for every LVGL call and every LVGL
    # object's release, which lvgl-python documents.
    print("#ifdef Py_GIL_DISABLED")
    print("    if (PyUnstable_Module_SetGIL(m, Py_MOD_GIL_NOT_USED) < 0) {")
    print("        Py_DECREF(m);")
    print("        return NULL;")
    print("    }")
    print("#endif")

    if registration.int_constants or registration.generated_globals:
        for int_constant in registration.int_constants:
            name = export_name(int_constant, "constant")
            print(
                '    if (PyModule_AddIntConstant(m, "{name}", {value}) < 0) return NULL;'.format(
                    name=name, value=int_constant
                )
            )
        for global_name in registration.generated_globals:
            if not global_name.startswith("LV_"):
                continue
            if global_name.startswith("LV_SYMBOL_"):
                continue
            py_name = simplify_identifier(global_name)
            if py_name.startswith("LV_"):
                py_name = py_name[3:]
            print(
                '    if (PyModule_AddStringConstant(m, "{name}", {value}) < 0) return NULL;'.format(
                    name=py_name, value=global_name
                )
            )

    if registration.enum_names:
        for enum_name in registration.enum_names:
            safe = sanitize(enum_name)
            py_name = export_name(enum_name, "enum")
            print(
                '    if (PyType_Ready(&py_lv_{safe}_type) < 0) return NULL;'.format(
                    safe=safe
                )
            )
            print(
                '    {{ PyObject *ns = PyType_GenericNew(&py_lv_{safe}_type, NULL, NULL); if (ns == NULL) return NULL; if (PyModule_AddObject(m, "{name}", ns) < 0) return NULL; }}'.format(
                    name=py_name, safe=safe
                )
            )

    if max_phase >= 3:
        print("    py_lv_runtime_init_types();")
        print("    if (PyType_Ready(&py_blob_type) < 0) return NULL;")
        print("    if (PyType_Ready(&py_lv_base_struct_type) < 0) return NULL;")
        print("    if (PyType_Ready(&py_C_Pointer_type) < 0) return NULL;")
        print("    Py_INCREF((PyObject *)&py_C_Pointer_type);")
        print('    if (PyModule_AddObject(m, "C_Pointer", (PyObject *)&py_C_Pointer_type) < 0) return NULL;')
        print("    if (PyLvReferenceError) {")
        print("        Py_INCREF(PyLvReferenceError);")
        print('        if (PyModule_AddObject(m, "LvReferenceError", PyLvReferenceError) < 0) return NULL;')
        print("    }")
        if registration.struct_names:
            for struct_name in registration.struct_names:
                san = sanitize(struct_name)
                struct_tag = (
                    "struct "
                    if struct_name in runtime.get("structs_without_typedef", {})
                    else ""
                )
                py_name = export_name(struct_name, "struct")
                print(
                    '    if (PyType_Ready(&py_{san}_type) < 0) return NULL;'.format(
                        san=san
                    )
                )
                if struct_name in cpython_struct_sizes:
                    print(
                        '    lv_struct_register_size(&py_{san}_type, sizeof({tag}{name}));'.format(
                            san=san, tag=struct_tag, name=struct_name
                        )
                    )
                    print(
                        '    lv_struct_expose_size(&py_{san}_type);'.format(san=san)
                    )
                print(
                    '    Py_INCREF((PyObject *)&py_{san}_type);'.format(san=san)
                )
                print(
                    '    if (PyModule_AddObject(m, "{name}", (PyObject *)&py_{san}_type) < 0) return NULL;'.format(
                        name=py_name, san=san
                    )
                )
        if registration.struct_alias_names:
            for struct_name in registration.struct_alias_names:
                san = sanitize(struct_name)
                struct_tag = (
                    "struct "
                    if struct_name in runtime.get("structs_without_typedef", {})
                    else ""
                )
                py_name = export_name(struct_aliases[struct_name], "struct")
                print(
                    '    if (PyType_Ready(&py_{san}_type) < 0) return NULL;'.format(
                        san=san
                    )
                )
                if struct_name in cpython_struct_sizes:
                    print(
                        '    lv_struct_register_size(&py_{san}_type, sizeof({tag}{name}));'.format(
                            san=san, tag=struct_tag, name=struct_name
                        )
                    )
                    print(
                        '    lv_struct_expose_size(&py_{san}_type);'.format(san=san)
                    )
                print(
                    '    Py_INCREF((PyObject *)&py_{san}_type);'.format(san=san)
                )
                print(
                    '    if (PyModule_AddObject(m, "{name}", (PyObject *)&py_{san}_type) < 0) return NULL;'.format(
                        name=py_name, san=san
                    )
                )
        if registration.struct_names:
            # Structs that aren't exported, such as the type of an anonymous
            # union field, are still returned by field reads, so their types
            # must be ready (lvgl-bindings#39).
            for struct_name, generated in generated_structs.items():
                if generated and struct_name not in registration.struct_names:
                    print(
                        '    if (PyType_Ready(&py_{san}_type) < 0) return NULL;'.format(
                            san=sanitize(struct_name)
                        )
                    )

        for global_name in cpython_global_types:
            global_type = cpython_global_types.get(global_name)
            type_object = (
                "&py_{san}_type".format(san=sanitize(global_type))
                if global_type
                else "&py_blob_type"
            )
            py_name = simplify_identifier(global_name)
            print(
                guarded(
                    '    {{ PyObject *obj = lv_to_mp_struct({type_object}, (void *)&{global_name});'
                    ' if (obj == NULL) return NULL;'
                    ' if (PyModule_AddObject(m, "{py_name}", obj) < 0) {{ Py_DECREF(obj); return NULL; }} }}'.format(
                        type_object=type_object,
                        global_name=global_name,
                        py_name=py_name,
                    ),
                    global_name,
                )
            )

    if registration.object_names:
        enums = runtime.get("enums", {})
        for obj_name in registration.object_names:
            san = sanitize(obj_name)
            print(
                '    if (PyType_Ready(&py_lv_{san}_type) < 0) return NULL;'.format(
                    san=san
                )
            )
            obj_enums = [
                enum_name
                for enum_name in enums.keys()
                if is_method_of(enum_name, obj_name)
            ]
            for enum_name in obj_enums:
                enum_safe = sanitize(enum_name)
                attr_name = export_name(method_name_from_func_name(enum_name), "enum")
                print(
                    '    {{ if (PyType_Ready(&py_lv_{enum_safe}_type) < 0) return NULL;'
                    ' PyObject *_enum_ns = (PyObject *)PyType_GenericNew(&py_lv_{enum_safe}_type, NULL, NULL);'
                    ' if (_enum_ns == NULL) return NULL;'
                    ' if (((PyTypeObject *)&py_lv_{san}_type)->tp_dict &&'
                    ' PyDict_SetItemString(((PyTypeObject *)&py_lv_{san}_type)->tp_dict, "{attr_name}", _enum_ns) < 0) {{ Py_DECREF(_enum_ns); return NULL; }}'
                    ' Py_DECREF(_enum_ns); }}'.format(
                        enum_safe=enum_safe,
                        san=san,
                        attr_name=attr_name,
                    )
                )
            print(
                '    Py_INCREF((PyObject *)&py_lv_{san}_type);'.format(san=san)
            )
            print(
                '    if (PyModule_AddObject(m, "{name}", (PyObject *)&py_lv_{san}_type) < 0) return NULL;'.format(
                    name=export_name(obj_name, "object"), san=san
                )
            )

    if registration.module_functions:
        generated_funcs = runtime.get("generated_funcs", {})
        for func in registration.module_functions:
            py_func = _resolved_py_func_name(func.name, generated_funcs)
            if not py_func:
                continue
            fname = sanitize(py_func)
            py_name = export_name(func.name, "function")
            print(
                '    {{ PyObject *fn = PyCFunction_New(&py_{fname}_def, NULL); if (fn == NULL) return NULL; if (PyModule_AddObject(m, "{py_name}", fn) < 0) return NULL; }}'.format(
                    fname=fname, py_name=py_name
                )
            )

    print("    return m;")
    print("}")
