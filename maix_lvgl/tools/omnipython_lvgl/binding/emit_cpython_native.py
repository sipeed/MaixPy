# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""CPython body codegen (phases 3–7): funcs, objects, structs, and callbacks."""

from __future__ import print_function

import re
import collections
import copy
from contextvars import ContextVar

from pycparser import c_ast

from . import runtime
from .emit_backend import (
    callback_return_conversion_available,
    conversion_available,
    function_reuse_allowed,
)
from .helpers import (
    is_global_callback,
    is_method_of,
    is_struct,
    is_widget_scoped_only_enum,
    method_name_from_func_name,
    sanitize as helper_sanitize,
    simplify_identifier,
)
from .parse import add_default_declname, convert_array_to_ptr, function_prototype, get_name, get_type


# This module owns no mirrored emitter globals; generated output is routed
# through the active run context explicitly.
print = runtime.emit


_EMIT_HELPERS = ContextVar("lvgl_cpython_emit_helpers", default=None)


def begin_emit_helpers():
    """Start an isolated helper scope and return its restoration token."""
    return _EMIT_HELPERS.set(None)


def bind_emit_helpers(local_ns):
    """Bind AST-emitter helpers to the active CPython backend run."""
    from . import analyze as analyze_mod

    analyze_fns = (
        "get_methods",
        "has_ctor",
        "get_ctor",
        "get_struct_functions",
        "noncommon_part",
        "get_enum_members",
        "get_enum_value",
        "get_enum_member_name",
        "is_static_member",
        "is_struct_function",
    )
    bound = {k: getattr(analyze_mod, k) for k in analyze_fns}
    bound["sanitize"] = helper_sanitize
    bound["simplify_identifier"] = simplify_identifier
    bound["method_name_from_func_name"] = method_name_from_func_name
    bound["is_struct"] = is_struct
    bound["is_global_callback"] = is_global_callback
    bound["get_type"] = get_type
    bound["function_prototype"] = function_prototype
    bound["MissingConversionException"] = analyze_mod.MissingConversionException
    keys = (
        "gen",
        "parser",
        "get_name",
        "is_struct",
        "structs",
        "structs_without_typedef",
        "decl_to_callback",
        "flatten_struct",
        "get_user_data",
        "is_global_callback",
        "get_arg_name",
        "lv_base_obj_pattern",
        "gen_func_error",
        "try_generate_type",
        "lv_to_mp_funcptr",
        "function_prototype",
        "is_static_member",
        "is_struct_function",
        "build_mp_func_arg",
        "method_name_from_func_name",
        "parent_obj_names",
        "base_obj_type",
        "lv_func_returns_array",
        "try_generate_array_type",
        "func_prototypes",
        "func_metadata",
        "obj_metadata",
        "generated_funcs",
        "generated_callbacks",
        "callback_metadata",
        "lv_to_mp",
        "mp_to_lv",
        "lv_to_mp_byref",
        "lv_mp_type",
        "generated_structs",
        "generated_struct_functions",
        "generated_struct_method_funcs",
        "callbacks_used_on_structs",
        "enum_referenced",
        "enums",
    )
    for k in keys:
        if k in local_ns:
            bound[k] = local_ns[k]
        elif k in _STATE_KEYS:
            value = runtime.get(k, None)
            if value is not None:
                bound[k] = value
    _EMIT_HELPERS.set(bound)
    return bound


_STATE_KEYS = (
    "generated_structs",
    "generated_struct_functions",
    "struct_aliases",
    "callbacks_used_on_structs",
    "generated_funcs",
    "generated_callbacks",
    "mp_to_lv",
    "lv_to_mp",
    "lv_to_mp_byref",
    "lv_mp_type",
    "func_prototypes",
    "func_metadata",
    "obj_metadata",
    "enum_referenced",
    "enums",
)


def _h(name):
    helpers = _EMIT_HELPERS.get()
    if helpers is None:
        raise RuntimeError("CPython native emitter helpers are not bound")
    if name in helpers:
        return helpers[name]
    if name in _STATE_KEYS:
        return runtime.get(name)
    try:
        return runtime.get(name)
    except NameError:
        raise KeyError("Missing emit helper: %s" % name)


def bound_helper(name, default=None):
    """Return a value from the active CPython native emitter binding."""
    helpers = _EMIT_HELPERS.get()
    if helpers is None:
        return default
    return helpers.get(name, default)


def reset_emit_helpers(token=None):
    """Release helper state, restoring an enclosing emitter when supplied."""
    if token is None:
        _EMIT_HELPERS.set(None)
    else:
        _EMIT_HELPERS.reset(token)


def _emit_max_phase():
    return runtime.get("emit_options", {}).get("max_phase")


def emit_helper_struct_cpython():
    from pycparser import c_parser

    parser = c_parser.CParser()
    ast = parser.parse(
        """
typedef union {
    void*           ptr_val;
    const char*     str_val;
    int             int_val;
    unsigned int    uint_val;
} C_Pointer;
"""
    )
    try_generate_struct_cpython("C_Pointer", ast.ext[0].type.type)


def _struct_value_writer(struct_name, san, struct_tag, complete):
    """C for ``mp_write_<san>``: a Python value to a struct by value.

    The value form is dereferenced where it is used (``data->header =
    mp_write_...(value)``), so it must never yield NULL. A dict builds the
    struct the way the type's own constructor does, as MicroPython accepts;
    anything else sets ``TypeError`` and yields a zeroed scratch copy, which
    the caller discards when it sees the error (lvgl-bindings#21).
    """
    ctype = "{tag}{name}".format(tag=struct_tag, name=struct_name)
    if not complete:
        return "#define mp_write_{san}(struct_obj) (*(({ctype}*)mp_write_ptr_{san}(struct_obj)))".format(
            san=san, ctype=ctype
        )
    return """static {ctype} mp_write_scratch_{san};

static inline void* mp_write_value_ptr_{san}(PyObject *value)
{{
    if (value != NULL && PyDict_Check(value)) {{
        PyObject *tmp = PyObject_CallOneArg((PyObject *)&py_{san}_type, value);
        if (tmp != NULL) {{
            memcpy(&mp_write_scratch_{san}, ((py_lv_struct_t *)tmp)->data, sizeof({ctype}));
            Py_DECREF(tmp);
            return &mp_write_scratch_{san};
        }}
    }} else if (value != NULL && value != Py_None) {{
        void *p = mp_write_ptr_{san}(value);
        if (p != NULL) return p;
    }} else {{
        PyErr_SetString(PyExc_TypeError, "Expected lvgl.{san} or dict, got None");
    }}
    memset(&mp_write_scratch_{san}, 0, sizeof({ctype}));
    return &mp_write_scratch_{san};
}}

#define mp_write_{san}(struct_obj) (*(({ctype}*)mp_write_value_ptr_{san}(struct_obj)))""".format(
        san=san, ctype=ctype
    )


def try_generate_struct_cpython(struct_name, struct):
    gen = _h("gen")
    sanitize = _h("sanitize")
    get_type_fn = _h("get_type")
    mp_to_lv = _h("mp_to_lv")
    lv_to_mp = _h("lv_to_mp")
    lv_to_mp_byref = _h("lv_to_mp_byref")
    lv_mp_type = _h("lv_mp_type")
    generated_structs = _h("generated_structs")
    structs_without_typedef = _h("structs_without_typedef")
    flatten_struct = _h("flatten_struct")
    try_generate_type = _h("try_generate_type")
    decl_to_callback = _h("decl_to_callback")
    get_user_data = _h("get_user_data")
    callbacks_used_on_structs = _h("callbacks_used_on_structs")
    MissingConversionException = _h("MissingConversionException")
    gen_func_error = _h("gen_func_error")
    max_phase = _emit_max_phase()

    if struct_name in generated_structs:
        return None
    sanitized_struct_name = sanitize(struct_name)
    generated_structs[struct_name] = False

    if struct_name in mp_to_lv:
        return mp_to_lv[struct_name]

    if struct.decls is None:
        structs = _h("structs")
        if struct_name == struct.name:
            return None
        if struct.name not in structs:
            return None
        return try_generate_type(structs[struct.name])

    flatten_struct_decls = flatten_struct(struct.decls)
    struct_tag = "struct " if struct_name in structs_without_typedef.keys() else ""
    read_cases = []
    write_cases = []
    struct_has_fields = bool(flatten_struct_decls)
    elem_size_expr = (
        "sizeof({struct_tag}{struct_name})".format(
            struct_tag=struct_tag, struct_name=struct_name
        )
        if struct_has_fields
        else "0"
    )

    for decl in flatten_struct_decls:
        converted = try_generate_type(decl.type)
        type_name = get_type_fn(decl.type, remove_quals=True)
        if (
            not converted
            and ("\n" in type_name or "{" in type_name)
            and isinstance(decl.type, c_ast.TypeDecl)
            and is_struct(decl.type.type)
        ):
            # An anonymous struct or union member (lv_grad_dsc_t.params):
            # name its type and bind it as a struct, as MicroPython does
            # (lvgl-bindings#39).
            type_name = "%s_%s_t" % (struct_name[:-2], decl.type.declname)
            print(
                "typedef __typeof__( (({tag}{parent}*)(0))->{child} ) {new};".format(
                    tag=struct_tag,
                    parent=struct_name,
                    child=decl.type.declname,
                    new=type_name,
                )
            )
            try_generate_struct_cpython(type_name, decl.type.type)
        if "\n" in type_name or "{" in type_name:
            continue
        if not is_struct(decl.type.type):
            if (type_name not in mp_to_lv or not mp_to_lv[type_name]) or (
                type_name not in lv_to_mp or not lv_to_mp[type_name]
            ):
                if type_name in generated_structs:
                    continue
                raise MissingConversionException(
                    "Missing conversion to %s when generating struct %s.%s"
                    % (type_name, struct_name, decl.name)
                )

        mp_to_lv_convertor = mp_to_lv[type_name]
        lv_to_mp_convertor = (
            lv_to_mp_byref[type_name]
            if type_name in lv_to_mp_byref
            else lv_to_mp[type_name]
        )
        cast = "(void*)" if isinstance(decl.type, c_ast.PtrDecl) else ""
        callback = decl_to_callback(decl)

        if callback:
            if max_phase is not None and max_phase < 7:
                continue
            func_name, arg_type = callback
            user_data, _, _ = get_user_data(
                arg_type,
                func_name=func_name,
                containing_struct=struct,
                containing_struct_name=struct_name,
            )
            if callback not in callbacks_used_on_structs:
                callbacks_used_on_structs.append(callback + (struct_name,))
            if user_data in [d.name for d in flatten_struct_decls]:
                full_user_data = "data->%s" % user_data
                full_user_data_ptr = "&%s" % full_user_data
                lv_callback = "%s_%s_callback" % (struct_name, func_name)
                print(
                    "static %s %s_%s_callback(%s);"
                    % (
                        get_type_fn(arg_type.type, remove_quals=False),
                        struct_name,
                        func_name,
                        gen.visit(arg_type.args),
                    )
                )
            else:
                full_user_data = "NULL"
                full_user_data_ptr = full_user_data
                lv_callback = "NULL"
                if not user_data:
                    gen_func_error(
                        decl,
                        "Missing 'user_data' field for callback '%s_%s'"
                        % (struct_name, func_name),
                    )
                else:
                    gen_func_error(
                        decl, "Missing 'user_data' member in struct '%s'" % struct_name
                    )
            write_cases.append(
                'if (strcmp(attr, "{field}") == 0) {{ data->{decl_name} = {cast}mp_lv_callback(value, {lv_callback}, "{struct_name}_{field}", {user_data}, {holder}, NULL, NULL); result = 0; }}'.format(
                    struct_name=struct_name,
                    field=sanitize(decl.name),
                    decl_name=decl.name,
                    lv_callback=lv_callback,
                    user_data=full_user_data_ptr,
                    holder="data" if full_user_data_ptr.startswith("&data->") else "NULL",
                    cast=cast,
                )
            )
            read_cases.append(
                'if (strcmp(attr, "{field}") == 0) return mp_lv_funcptr(NULL, {cast}data->{decl_name}, {lv_callback}, "{struct_name}_{field}", {user_data});'.format(
                    struct_name=struct_name,
                    field=sanitize(decl.name),
                    decl_name=decl.name,
                    lv_callback=lv_callback,
                    user_data=full_user_data,
                    cast=cast,
                )
            )
        else:
            is_writeable = (not hasattr(decl.type, "quals")) or "const" not in decl.type.quals
            elem = (
                _struct_array_elem(decl, get_type_fn, lv_to_mp)
                if isinstance(decl.type, c_ast.ArrayDecl)
                else None
            )
            if elem:
                # A view, not a raw Blob, and a checked whole-array write
                # instead of a memcpy from whatever mp_to_ptr returned
                # (lvgl-bindings#38).
                shape = "data->{decl_name}, {dim}, sizeof({ctype})".format(
                    decl_name=decl.name,
                    dim=gen.visit(decl.type.dim),
                    ctype=gen.visit(decl.type.type),
                )
                san = sanitize(elem)
                if is_writeable:
                    write_cases.append(
                        'if (strcmp(attr, "{field}") == 0) {{ lvpy_struct_array_assign({shape}, mp_write_value_ptr_{san}, value); result = 0; }}'.format(
                            field=sanitize(decl.name), shape=shape, san=san
                        )
                    )
                read_cases.append(
                    'if (strcmp(attr, "{field}") == 0) return lvpy_struct_array_new(self, {shape}, mp_read_ptr_{san}, mp_write_value_ptr_{san});'.format(
                        field=sanitize(decl.name), shape=shape, san=san
                    )
                )
            elif isinstance(decl.type, c_ast.ArrayDecl):
                memcpy_size = "sizeof(%s)*%s" % (
                    gen.visit(decl.type.type),
                    gen.visit(decl.type.dim),
                )
                if is_writeable:
                    write_cases.append(
                        'if (strcmp(attr, "{field}") == 0) {{ memcpy((void*)&data->{decl_name}, {cast}{convertor}(value), {size}); result = 0; }}'.format(
                            field=sanitize(decl.name),
                            decl_name=decl.name,
                            convertor=mp_to_lv_convertor,
                            cast=cast,
                            size=memcpy_size,
                        )
                    )
                read_cases.append(
                    'if (strcmp(attr, "{field}") == 0) return {convertor}({cast}data->{decl_name});'.format(
                        field=sanitize(decl.name),
                        decl_name=decl.name,
                        convertor=lv_to_mp_convertor,
                        cast=cast,
                    )
                )
            else:
                if is_writeable:
                    write_cases.append(
                        'if (strcmp(attr, "{field}") == 0) {{ data->{decl_name} = {cast}{convertor}(value); result = 0; }}'.format(
                            field=sanitize(decl.name),
                            decl_name=decl.name,
                            convertor=mp_to_lv_convertor,
                            cast=cast,
                        )
                    )
                read_cases.append(
                    'if (strcmp(attr, "{field}") == 0) return {convertor}({cast}data->{decl_name});'.format(
                        field=sanitize(decl.name),
                        decl_name=decl.name,
                        convertor=lv_to_mp_convertor,
                        cast=cast,
                    )
                )

    print(
        """
/*
 * Struct {struct_name} (CPython)
 */

extern PyMethodDef py_{san}_methods[];

static PyObject *py_{san}_getattro(PyObject *self, PyObject *name)
{{
    py_lv_struct_t *inst = (py_lv_struct_t *)self;
    {struct_tag}{struct_name} *data = ({struct_tag}{struct_name}*)inst->data;
    if (data == NULL) {{
        PyErr_SetString(PyLvReferenceError, "struct data is NULL");
        return NULL;
    }}
    const char *attr = PyUnicode_AsUTF8(name);
    if (attr == NULL) return NULL;
    {read_cases}
    for (PyMethodDef *m = py_{san}_methods; m->ml_name != NULL; m++) {{
        if (strcmp(attr, m->ml_name) == 0)
            return PyCFunction_NewEx(m, self, NULL);
    }}
    return PyObject_GenericGetAttr((PyObject *)self, name);
}}

static const char *const py_{san}_field_names[] = {{{field_names}NULL}};

static PyObject *py_{san}_dir(PyObject *self, PyObject *unused)
{{
    (void)unused;
    return lvpy_struct_dir(self, py_{san}_field_names, py_{san}_methods);
}}

static PyMethodDef py_{san}_type_methods[] = {{
    {{"__dir__", py_{san}_dir, METH_NOARGS, NULL}},
    {{NULL}}
}};

static int py_{san}_setattro(PyObject *self, PyObject *name, PyObject *value)
{{
    if (value == NULL) {{
        PyErr_SetString(PyExc_AttributeError, "cannot delete struct fields");
        return -1;
    }}
    py_lv_struct_t *inst = (py_lv_struct_t *)self;
    {struct_tag}{struct_name} *data = ({struct_tag}{struct_name}*)inst->data;
    if (data == NULL) {{
        PyErr_SetString(PyLvReferenceError, "struct data is NULL");
        return -1;
    }}
    const char *attr = PyUnicode_AsUTF8(name);
    if (attr == NULL) return -1;
    int result = -1;
    {save_fields}
    {write_cases}
    if (PyErr_Occurred()) {{
        {restore_fields}
        return -1;
    }}
    if (result < 0) {{
        PyErr_Format(PyExc_AttributeError, "'{struct_name}' object has no attribute '%s'", attr);
    }}
    return result;
}}

static PyObject *py_{san}_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{{
    return make_new_lv_struct(type, args, kwds, {elem_size});
}}

static void py_{san}_dealloc(py_lv_struct_t *self)
{{
    py_lv_struct_dealloc(self);
}}

PyTypeObject py_{san}_type = {{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "lvgl.{san}",
    .tp_basicsize = sizeof(py_lv_struct_t),
    .tp_dealloc = (destructor)py_{san}_dealloc,
    .tp_getattro = (getter)py_{san}_getattro,
    .tp_setattro = (setter)py_{san}_setattro,
    .tp_new = py_{san}_new,
    .tp_methods = py_{san}_type_methods,
    .tp_base = &py_lv_base_struct_type,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
}};

static inline void* mp_write_ptr_{san}(PyObject *self_in)
{{
    if (!self_in || self_in == Py_None) return NULL;
    if (!PyObject_TypeCheck(self_in, &py_{san}_type)) {{
        PyErr_Format(PyExc_TypeError, "Expected lvgl.{san}, got '%s'", Py_TYPE(self_in)->tp_name);
        return NULL;
    }}
    py_lv_struct_t *self = (py_lv_struct_t *)self_in;
    return ({struct_tag}{struct_name}*)self->data;
}}

{write_value}

static inline PyObject *mp_read_ptr_{san}(void *field)
{{
    return lv_to_mp_struct(&py_{san}_type, field);
}}

#define mp_read_{san}(field) lv_to_mp_struct_own(&py_{san}_type, copy_buffer(&field, sizeof({struct_tag}{struct_name})))
#define mp_read_byref_{san}(field) mp_read_ptr_{san}(&field)
""".format(
            struct_name=struct_name,
            san=sanitized_struct_name,
            struct_tag=struct_tag,
            read_cases="\n    ".join(read_cases) if read_cases else "(void)attr;",
            field_names="".join(
                '"%s", ' % name
                for name in dict.fromkeys(
                    re.findall(r'strcmp\(attr, "([^"]+)"\)', "".join(read_cases))
                )
            ),
            write_cases="\n    ".join(write_cases) if write_cases else "(void)value;",
            elem_size=elem_size_expr,
            # A conversion that fails has already stored its placeholder, so
            # the field is put back as it was (lvgl-bindings#21).
            save_fields=(
                "{t}{n} saved;\n    memcpy(&saved, data, sizeof(saved));".format(
                    t=struct_tag, n=struct_name
                )
                if struct_has_fields and write_cases
                else ""
            ),
            restore_fields=(
                "memcpy(data, &saved, sizeof(saved));"
                if struct_has_fields and write_cases
                else ""
            ),
            write_value=_struct_value_writer(
                struct_name, sanitized_struct_name, struct_tag, struct_has_fields
            ),
        )
    )

    if struct_has_fields:
        cpython_struct_sizes = runtime.get("cpython_struct_sizes", {})
        cpython_struct_sizes[struct_name] = True
        runtime.set_("cpython_struct_sizes", cpython_struct_sizes)

    lv_to_mp[struct_name] = "mp_read_%s" % sanitized_struct_name
    lv_to_mp_byref[struct_name] = "mp_read_byref_%s" % sanitized_struct_name
    mp_to_lv[struct_name] = "mp_write_%s" % sanitized_struct_name
    lv_to_mp["%s *" % struct_name] = "mp_read_ptr_%s" % sanitized_struct_name
    mp_to_lv["%s *" % struct_name] = "mp_write_ptr_%s" % sanitized_struct_name
    lv_to_mp["const %s *" % struct_name] = "mp_read_ptr_%s" % sanitized_struct_name
    mp_to_lv["const %s *" % struct_name] = "mp_write_ptr_%s" % sanitized_struct_name
    lv_mp_type[struct_name] = simplify_identifier(sanitized_struct_name)
    lv_mp_type["%s *" % struct_name] = simplify_identifier(sanitized_struct_name)
    lv_mp_type["const %s *" % struct_name] = simplify_identifier(sanitized_struct_name)
    generated_structs[struct_name] = True
    return struct_name


def emit_struct_methods_cpython(struct_name, method_entries):
    sanitize = _h("sanitize")
    if not method_entries:
        print(
            "PyMethodDef py_{san}_methods[] = {{{{NULL}}}};".format(
                san=sanitize(struct_name)
            )
        )
        return
    lines = []
    for func_name, method_name in method_entries:
        lines.append(
            '    {{"{method}", (PyCFunction)py_{func}, METH_VARARGS | METH_KEYWORDS, NULL}}'.format(
                method=method_name,
                func=func_name,
            )
        )
    print(
        """
PyMethodDef py_{san}_methods[] = {{
{entries},
    {{NULL}}
}};
""".format(
            san=sanitize(struct_name),
            entries=",\n".join(lines),
        )
    )


PY_INT_TYPES = frozenset(
    {
        "int",
        "int8_t",
        "int16_t",
        "int32_t",
        "int64_t",
        "char",
        "short",
        "long",
        "unsigned",
        "unsigned int",
        "unsigned char",
        "unsigned short",
        "unsigned long",
        "uint8_t",
        "uint16_t",
        "uint32_t",
        "uint64_t",
        "size_t",
        "long long",
        "unsigned long long",
        "unsigned long long int",
        "long long int",
        "long int",
        "bool",
        "lv_coord_t",
        "lv_opa_t",
    }
)
PY_FLOAT_TYPES = frozenset({"float", "double"})


def _skip_func_arg(arg, get_type_fn):
    if isinstance(arg, c_ast.EllipsisParam):
        return True
    if isinstance(arg.type, c_ast.TypeDecl) and isinstance(
        arg.type.type, c_ast.IdentifierType
    ):
        if "void" in arg.type.type.names:
            return True
    return False


def _c_param_name(arg, index):
    if hasattr(arg, "name") and arg.name:
        return arg.name
    return "arg%d" % index


def _c_param_type(arg, gen):
    full = gen.visit(arg)
    name = _c_param_name(arg, 0)
    if full.endswith(" " + name):
        return full[: -len(name) - 1]
    return full.rsplit(" ", 1)[0]


def _callback_c_args(func):
    gen = _h("gen")
    args = func.args.params
    enumerated_args = []
    for i, arg in enumerate(args):
        arg_name = "arg%d" % i
        new_arg = c_ast.Decl(
            name=arg_name,
            quals=arg.quals,
            align=[],
            storage=[],
            funcspec=[],
            type=copy.deepcopy(arg.type),
            init=None,
            bitsize=None,
        )
        t = new_arg
        while hasattr(t, "type"):
            if hasattr(t.type, "declname"):
                t.type.declname = arg_name
            t = t.type
        enumerated_args.append(new_arg)
    return args, enumerated_args, ", ".join(gen.visit(a) for a in enumerated_args)


def gen_callback_func_cpython(func, func_name=None, user_data_argument=False):
    gen = _h("gen")
    sanitize = _h("sanitize")
    get_type_fn = _h("get_type")
    lv_to_mp = _h("lv_to_mp")
    mp_to_lv = _h("mp_to_lv")
    lv_mp_type = _h("lv_mp_type")
    get_user_data = _h("get_user_data")
    lv_base_obj_pattern = _h("lv_base_obj_pattern")
    generated_callbacks = _h("generated_callbacks")
    callback_metadata = _h("callback_metadata")
    try_generate_type = _h("try_generate_type")
    MissingConversionException = _h("MissingConversionException")
    get_arg_name = _h("get_arg_name")

    if func_name in generated_callbacks:
        return
    callback_metadata[func_name] = {"args": []}
    args, enumerated_args, func_args = _callback_c_args(func)
    if not func_name:
        func_name = get_arg_name(func.type)

    if is_global_callback(func):
        full_user_data = "(void *)mp_lv_global_user_data"
    else:
        user_data, user_data_getter, _ = get_user_data(func, func_name)
        if (
            user_data_argument
            and len(args) > 0
            and gen.visit(args[-1].type) == "void *"
        ):
            full_user_data = "arg%d" % (len(args) - 1)
        elif user_data:
            full_user_data = "arg0->%s" % user_data
            if len(args) < 1 or (
                hasattr(args[0].type.type, "names")
                and lv_base_obj_pattern.match(args[0].type.type.names[0])
            ):
                raise MissingConversionException(
                    "Callback: first argument must be lv_obj_t"
                )
        elif user_data_getter:
            full_user_data = "%s(arg0)" % user_data_getter.name
        else:
            raise MissingConversionException(
                "Callback: user_data NOT FOUND! %s" % gen.visit(func)
            )

    return_type = get_type_fn(func.type, remove_quals=False)
    if not callback_return_conversion_available(
        return_type=return_type,
        mp_to_lv=mp_to_lv,
        generate_type=lambda: try_generate_type(func.type),
    ):
        raise MissingConversionException(
            "Callback return value: Missing conversion to %s" % return_type
        )

    callback_metadata[func_name]["return_type"] = lv_mp_type[return_type]
    build_arg_lines = []
    tuple_items = []
    for i, arg in enumerate(args):
        arg_type = get_type_fn(arg.type, remove_quals=True)
        cast = "(void*)" if isinstance(arg.type, c_ast.PtrDecl) else ""
        if not conversion_available(
            conversions=lv_to_mp,
            type_name=arg_type,
            generate_type=lambda: try_generate_type(arg.type),
        ):
            raise MissingConversionException(
                "Callback: Missing conversion to %s" % arg_type
            )
        convertor = lv_to_mp[arg_type]
        build_arg_lines.append(
            "PyObject *py_arg%d = %s(%sarg%d);"
            % (i, convertor, cast, i)
        )
        tuple_items.append("py_arg%d" % i)
        callback_metadata[func_name]["args"].append({"type": lv_mp_type[arg_type]})

    safe_name = sanitize(func_name)
    if return_type == "void":
        void_default = ""
    elif "*" in return_type:
        void_default = " NULL"
    else:
        void_default = " (%s){0}" % return_type

    if return_type == "void":
        tail = (
            "    lvpy_release_lock_for_python();\n"
            "    lvpy_nesting_inc();\n"
            "    PyObject *result = PyObject_CallObject(py_cb, py_args);\n"
            "    Py_DECREF(py_args);\n"
            "    Py_DECREF(py_cb);\n"
            "    lvpy_nesting_dec();\n"
            "    lvpy_reacquire_lock_after_python();\n"
            "    if (result) Py_DECREF(result);\n"
            "    else PyErr_Clear();\n"
            "    PyGILState_Release(gstate);"
        )
    else:
        tail = (
            "    lvpy_release_lock_for_python();\n"
            "    lvpy_nesting_inc();\n"
            "    PyObject *result = PyObject_CallObject(py_cb, py_args);\n"
            "    Py_DECREF(py_args);\n"
            "    Py_DECREF(py_cb);\n"
            "    lvpy_nesting_dec();\n"
            "    lvpy_reacquire_lock_after_python();\n"
            "    if (!result) { PyErr_Clear(); PyGILState_Release(gstate); return%s; }\n"
            "    %s _c_res = %s(result);\n"
            "    Py_DECREF(result);\n"
            "    PyGILState_Release(gstate);\n"
            "    return _c_res;"
            % (void_default, return_type, mp_to_lv[return_type])
        )

    print(
        """
/*
 * Callback function {func_name} (CPython)
 * {func_prototype}
 */
static {return_type} {safe_name}_callback({func_args})
{{
    PyGILState_STATE gstate = PyGILState_Ensure();
    PyObject *callbacks = get_callback_dict_from_user_data({user_data});
    if (!callbacks) {{ PyGILState_Release(gstate); return{void_default}; }}
    PyObject *py_cb = PyDict_GetItemString(callbacks, "{func_name}");
    if (!py_cb || !PyCallable_Check(py_cb)) {{ PyGILState_Release(gstate); return{void_default}; }}
    /* Hold the callback for the whole call: it may replace or remove its
     * own registration while it runs. */
    Py_INCREF(py_cb);
    {build_args}
    PyObject *py_args = ({args_ok}) ? PyTuple_Pack({num_args}{tuple_args}) : NULL;
    {release_args}
    if (!py_args) {{ PyErr_Clear(); Py_DECREF(py_cb); PyGILState_Release(gstate); return{void_default}; }}
{tail}
}}
""".format(
            func_name=func_name,
            func_prototype=gen.visit(func),
            safe_name=safe_name,
            return_type=return_type,
            func_args=func_args,
            user_data=full_user_data,
            build_args="\n    ".join(build_arg_lines),
            num_args=len(args),
            tuple_args="".join(", " + item for item in tuple_items),
            args_ok=" && ".join(tuple_items) if tuple_items else "1",
            release_args="\n    ".join(
                "Py_XDECREF(%s);" % item for item in tuple_items
            ),
            tail=tail,
            void_default=void_default,
        )
    )
    generated_callbacks[func_name] = True


def build_py_callback_arg(arg, index, func, py_var):
    gen = _h("gen")
    decl_to_callback = _h("decl_to_callback")
    get_user_data = _h("get_user_data")
    sanitize = _h("sanitize")
    func_metadata = _h("func_metadata")
    callback_metadata = _h("callback_metadata")
    gen_func_error = _h("gen_func_error")
    MissingConversionException = _h("MissingConversionException")

    fixed_arg = copy.deepcopy(arg)
    convert_array_to_ptr(fixed_arg)
    if not fixed_arg.name:
        fixed_arg.name = _c_param_name(arg, index)
        add_default_declname(fixed_arg, fixed_arg.name)

    callback = decl_to_callback(arg)
    if not callback:
        raise MissingConversionException("Not a callback argument")

    callback_name, arg_type = callback
    args = func.type.args.params if func.type.args else []
    try:
        user_data_argument = False
        full_user_data = "NULL"
        user_data_getter = "NULL"
        user_data_setter = "NULL"
        containing_struct = "NULL"
        if (
            len(args) > 0
            and gen.visit(args[-1].type) == "void *"
            and args[-1].name == "user_data"
        ):
            callback_name = "%s_%s" % (func.name, callback_name)
            full_user_data = "&user_data"
            user_data_argument = True
        else:
            first_arg = args[0]
            struct_name = get_name(
                first_arg.type.type.type
                if hasattr(first_arg.type.type, "type")
                else first_arg.type.type
            )
            callback_name = "%s_%s" % (struct_name, callback_name)
            user_data, user_data_getter_fn, user_data_setter_fn = get_user_data(
                arg_type, callback_name
            )
            if is_global_callback(arg_type):
                full_user_data = "&mp_lv_global_user_data"
            else:
                if user_data:
                    full_user_data = "&%s->%s" % (first_arg.name, user_data)
                    # The struct holds the dict: every callback set on it
                    # shares one reference, released with the struct.
                    containing_struct = first_arg.name
                elif user_data_getter_fn and user_data_setter_fn:
                    full_user_data = "NULL"
                    containing_struct = first_arg.name
                    user_data_getter = user_data_getter_fn.name
                    user_data_setter = user_data_setter_fn.name
                if index == 0:
                    raise MissingConversionException(
                        "Callback cannot be the first argument"
                    )
                if not full_user_data and not user_data_getter_fn:
                    raise MissingConversionException(
                        "Callback needs user_data on struct"
                    )

        gen_callback_func_cpython(arg_type, callback_name, user_data_argument)
        safe_cb = sanitize(callback_name)
        arg_metadata = {
            "type": "callback",
            "function": callback_metadata[callback_name],
        }
        if fixed_arg.name:
            arg_metadata["name"] = fixed_arg.name
        func_metadata[func.name]["args"].append(arg_metadata)
        return (
            "void *{arg_name} = mp_lv_callback({py_var}, &{safe_cb}_callback, "
            '"{callback_name}", {full_user_data}, {containing_struct}, '
            "({user_data_getter}), ({user_data_setter}));"
        ).format(
            arg_name=fixed_arg.name,
            py_var=py_var,
            safe_cb=safe_cb,
            callback_name=callback_name,
            full_user_data=full_user_data,
            containing_struct=containing_struct,
            user_data_getter=user_data_getter,
            user_data_setter=user_data_setter,
        )
    except MissingConversionException as exp:
        gen_func_error(arg, exp)
        return "void *%s = NULL;" % fixed_arg.name


def _is_char_ptr_array_arg(arg):
    """True for a parameter declared as an array of char pointers."""
    t = getattr(arg, "type", None)
    if not isinstance(t, c_ast.ArrayDecl) or not isinstance(t.type, c_ast.PtrDecl):
        return False
    inner = t.type.type
    return (
        isinstance(inner, c_ast.TypeDecl)
        and isinstance(inner.type, c_ast.IdentifierType)
        and inner.type.names == ["char"]
    )


def _struct_array_elem(decl, get_type_fn, lv_to_mp):
    """Element struct name for a fixed-size struct array field, else None.

    Only complete structs qualify: their mp_write_value_ptr_* writer and
    mp_read_ptr_* reader exist.
    """
    elem_ast = decl.type.type
    if not isinstance(elem_ast, c_ast.TypeDecl):
        return None
    elem = get_type_fn(elem_ast, remove_quals=True)
    if not runtime.get("cpython_struct_sizes", {}).get(elem):
        return None
    if elem in (_h("structs_without_typedef") or {}):
        return None
    if not (lv_to_mp.get("%s *" % elem) or "").startswith("mp_read_ptr_"):
        return None
    return elem


def _const_struct_array_elem(arg, get_type_fn):
    """Element struct name for a ``const T name[]`` parameter, else None.

    Only const arrays qualify: LVGL reads them, so a list copied into a C
    array means the same thing as the caller's buffer. A non-const array may
    be written by LVGL (lv_obj_transform_point_array), and a copy would drop
    those writes, so it keeps the buffer-only lowering.
    """
    t = getattr(arg, "type", None)
    if not isinstance(t, c_ast.ArrayDecl) or not isinstance(t.type, c_ast.TypeDecl):
        return None
    if "const" not in (t.type.quals or []):
        return None
    elem = get_type_fn(t.type, remove_quals=True)
    if not runtime.get("cpython_struct_sizes", {}).get(elem):
        return None
    if elem in (_h("structs_without_typedef") or {}):
        return None
    return elem


def build_py_func_arg_line(arg, index, func, py_var):
    gen = _h("gen")
    get_type_fn = _h("get_type")
    mp_to_lv = _h("mp_to_lv")
    lv_mp_type = _h("lv_mp_type")
    func_metadata = _h("func_metadata")
    try_generate_type = _h("try_generate_type")
    decl_to_callback = _h("decl_to_callback")
    MissingConversionException = _h("MissingConversionException")
    max_phase = _emit_max_phase()

    if decl_to_callback(arg):
        if max_phase is not None and max_phase < 7:
            raise MissingConversionException(
                "Callbacks require emit phase 7 (function %s)" % func.name
            )
        return build_py_callback_arg(arg, index, func, py_var)

    if _is_char_ptr_array_arg(arg):
        # const char * const map[] and friends: LVGL stores the pointer, so
        # the generic mp_to_ptr lowering both rejected str sequences and,
        # had it worked, would have dangled. lvpy_str_arr_arg (emitted in
        # the file preamble) converts a sequence of str and retains the
        # array + strings on the widget under a per-function key.
        fixed_arg = copy.deepcopy(arg)
        convert_array_to_ptr(fixed_arg)
        cname = _c_param_name(arg, index)
        if not fixed_arg.name:
            fixed_arg.name = cname
            add_default_declname(fixed_arg, cname)
        arg_type = get_type_fn(arg.type, remove_quals=True)
        # Same lazy registration as the generic path: populates lv_mp_type
        # (and the conversion tables) for this array type on first sight.
        conversion_available(
            conversions=mp_to_lv,
            type_name=arg_type,
            generate_type=lambda: try_generate_type(arg.type),
        )
        arg_metadata = {"type": lv_mp_type[arg_type]}
        if cname:
            arg_metadata["name"] = cname
        func_metadata[func.name]["args"].append(arg_metadata)
        return '{var} = ({cast})lvpy_str_arr_arg(self, {py_var}, "{key}");'.format(
            var=gen.visit(fixed_arg),
            cast=gen.visit(fixed_arg.type),
            py_var=py_var,
            key="%s:%s" % (func.name, cname or index),
        )

    fixed_arg = copy.deepcopy(arg)
    convert_array_to_ptr(fixed_arg)
    cname = _c_param_name(arg, index)
    if not fixed_arg.name:
        fixed_arg.name = cname
        add_default_declname(fixed_arg, cname)

    arg_type = get_type_fn(arg.type, remove_quals=True)
    elem = _const_struct_array_elem(arg, get_type_fn)
    if elem is not None and conversion_available(
        conversions=mp_to_lv,
        type_name=arg_type,
        generate_type=lambda: try_generate_type(arg.type),
    ):
        # const lv_point_precise_t points[] and friends: a list of structs
        # (or dicts) becomes a C array, as on MicroPython; a buffer passes
        # through. Either way it is retained on the widget, because LVGL
        # keeps the pointer (lv_line_set_points never copies;
        # lvgl-bindings#37).
        arg_metadata = {"type": lv_mp_type[arg_type]}
        if cname:
            arg_metadata["name"] = cname
        func_metadata[func.name]["args"].append(arg_metadata)
        return (
            '{var} = ({cast})lvpy_struct_arr_arg(self, {py_var}, "{key}", '
            "sizeof({elem}), mp_write_value_ptr_{san});"
        ).format(
            var=gen.visit(fixed_arg),
            cast=gen.visit(fixed_arg.type),
            py_var=py_var,
            key="%s:%s" % (func.name, cname or index),
            elem=elem,
            san=_h("sanitize")(elem),
        )

    if not conversion_available(
        conversions=mp_to_lv,
        type_name=arg_type,
        generate_type=lambda: try_generate_type(arg.type),
    ):
        raise MissingConversionException("Missing conversion to %s" % arg_type)

    convertor = mp_to_lv[arg_type]
    cast = ""
    if hasattr(arg, "quals") and "const" in arg.quals:
        # const pointer: cast the converted pointer. const struct by value: the
        # lhs is already const; mp_write_* returns an lvalue — do not cast to struct.
        if isinstance(fixed_arg.type, c_ast.PtrDecl):
            cast = "(%s)" % gen.visit(fixed_arg.type)
    arg_metadata = {"type": lv_mp_type[arg_type]}
    if cname:
        arg_metadata["name"] = cname
    func_metadata[func.name]["args"].append(arg_metadata)
    return "{var} = {cast}{convertor}({py_var});".format(
        var=gen.visit(fixed_arg),
        cast=cast,
        convertor=convertor,
        py_var=py_var,
    )


def _struct_receiver_kind(func, obj_name, get_type_fn):
    """How a struct method takes its struct: "ptr", "array" (``T name[]``),
    "value", or None when the first argument isn't the struct. MicroPython
    binds all three as methods (lvgl-bindings#46)."""
    generated_structs = _h("generated_structs")
    if not obj_name or obj_name not in generated_structs:
        return None
    args = func.type.args.params if func.type.args else []
    if not args:
        return None
    first = args[0].type
    first_type = get_type_fn(first, remove_quals=True)
    if first_type in (obj_name + " *", "const " + obj_name + " *"):
        return "array" if isinstance(first, c_ast.ArrayDecl) else "ptr"
    if isinstance(first, c_ast.ArrayDecl):
        return "array" if get_type_fn(first.type, remove_quals=True) == obj_name else None
    if isinstance(first, c_ast.TypeDecl) and first_type == obj_name:
        return "value"
    return None


def _is_struct_method(func, obj_name, get_type_fn):
    return _struct_receiver_kind(func, obj_name, get_type_fn) is not None


def gen_py_func(func, obj_name):
    gen = _h("gen")
    sanitize = _h("sanitize")
    get_type_fn = _h("get_type")
    lv_to_mp = _h("lv_to_mp")
    generated_funcs = _h("generated_funcs")
    generated_struct_method_funcs = _h("generated_struct_method_funcs")
    func_prototypes = _h("func_prototypes")
    func_metadata = _h("func_metadata")
    function_prototype = _h("function_prototype")
    is_static_member = _h("is_static_member")
    is_struct_function = _h("is_struct_function")
    base_obj_type = _h("base_obj_type")
    module_name = _h("module_name")
    try_generate_type = _h("try_generate_type")
    lv_func_returns_array = _h("lv_func_returns_array")
    try_generate_array_type = _h("try_generate_array_type")

    args = func.type.args.params if func.type.args else []
    if len(args) == 1 and get_type_fn(args[0].type, remove_quals=True) == "void":
        args = []

    struct_method = bool(obj_name and _is_struct_method(func, obj_name, get_type_fn))
    emit_name = func.name + "_struct_method" if struct_method else func.name

    if struct_method:
        if generated_struct_method_funcs.get(emit_name) is True:
            return
        generated_struct_method_funcs[emit_name] = False
    else:
        if func.name in generated_funcs:
            return
        generated_funcs[func.name] = False
    func_metadata[func.name] = {"type": "function", "args": []}

    prototype_str = gen.visit(function_prototype(func))
    if not struct_method:
        if prototype_str in func_prototypes:
            original = func_prototypes[prototype_str]
            if function_reuse_allowed(
                function_name=func.name,
                original_name=original.name,
                original_generated=generated_funcs.get(original.name) is True,
                supports_dynamic_function_pointer=runtime.get(
                    "target_lowering_profile"
                ).supports_dynamic_function_pointer,
            ):
                generated_funcs[func.name] = original.name
                return
        func_prototypes[prototype_str] = func

    return_type = get_type_fn(func.type.type, remove_quals=False)
    if isinstance(func.type.type, c_ast.PtrDecl) and lv_func_returns_array.match(func.name):
        try_generate_array_type(func.type.type)

    if return_type == "void":
        result_decl = ""
        c_call = "(({func_ptr}){c_func})({send_args});"
        build_return = "Py_RETURN_NONE;"
        allow_threads = func.name in ("lv_task_handler", "lv_tick_inc")
    else:
        if not conversion_available(
            conversions=lv_to_mp,
            type_name=return_type,
            generate_type=lambda: try_generate_type(func.type.type),
        ):
            raise _h("MissingConversionException")(
                "Missing conversion from %s" % return_type
            )
        result_decl = "%s _res;\n    " % gen.visit(func.type.type)
        c_call = "_res = (({func_ptr}){c_func})({send_args});"
        cast = "(void*)" if isinstance(func.type.type, c_ast.PtrDecl) else ""
        build_return = "return %s(%s_res);" % (lv_to_mp[return_type], cast)
        allow_threads = func.name in ("lv_task_handler", "lv_tick_inc")

    is_method = (
        obj_name
        and not is_static_member(func, base_obj_type)
        and (
            is_method_of(func.name, obj_name)
            or _is_struct_method(func, obj_name, get_type_fn)
        )
    )
    struct_method = _is_struct_method(func, obj_name, get_type_fn)

    is_factory = obj_name is None and func.name.endswith("_create")
    decl_to_callback = _h("decl_to_callback")

    parse_fmt = []
    parse_decls = []
    parse_names = []
    body_items = []
    send_args = []
    decl_to_callback = _h("decl_to_callback")

    def _arg_sort_key(index, param):
        if (
            hasattr(param, "name")
            and param.name == "user_data"
            and gen.visit(param.type) == "void *"
        ):
            return 0
        if decl_to_callback(param):
            return 2
        return 1

    indexed_args = [
        (i, arg)
        for i, arg in enumerate(args)
        if not _skip_func_arg(arg, get_type_fn)
    ]

    for i, arg in indexed_args:
        send_args.append(_c_param_name(arg, i))

    for i, arg in indexed_args:
        cname = _c_param_name(arg, i)
        if is_method and i == 0:
            if struct_method:
                san = sanitize(obj_name)
                kind = _struct_receiver_kind(func, obj_name, get_type_fn)
                if kind == "value":
                    # A wrong type leaves the zeroed value and an exception set,
                    # which the PyErr_Occurred check after the arguments reports.
                    line = (
                        "%s %s = {0}; { %s *p_ = (%s *)mp_write_ptr_%s(self);"
                        " if (p_) %s = *p_; }"
                        % (obj_name, cname, obj_name, obj_name, san, cname)
                    )
                elif kind == "array":
                    line = "%s *%s = (%s *)mp_write_ptr_%s(self);" % (
                        obj_name, cname, obj_name, san)
                else:
                    line = "%s = (%s *)mp_write_ptr_%s(self);" % (
                        gen.visit(arg), obj_name, san)
                body_items.append((0, line))
            else:
                body_items.append(
                    (0, "lv_obj_t *%s = mp_to_lv(self);" % (cname or "obj"))
                )
            if not cname and not struct_method:
                send_args[0] = "obj"
            continue

        arg_type = get_type_fn(arg.type, remove_quals=True)
        if is_factory and i == 0 and arg_type == ("%s *" % base_obj_type):
            py_var = "parent_py"
            parse_fmt.append("|O")
            parse_decls.append("PyObject *%s" % py_var)
            parse_names.append(py_var)
            body_items.append(
                (
                    1,
                    "lv_obj_t *%s = NULL;\n"
                    "    if (%s && %s != Py_None) {\n"
                    "        %s = mp_to_lv(%s);\n"
                    "        if (!%s) {{ PyGILState_Release(gstate); return NULL; }}\n"
                    "    }"
                    % (cname, py_var, py_var, cname, py_var, cname),
                )
            )
            continue

        c_type = _c_param_type(arg, gen)
        full_decl = gen.visit(arg)
        if arg_type in PY_INT_TYPES:
            pvar = "%s_val" % cname
            parse_fmt.append("l")
            parse_decls.append("long %s" % pvar)
            parse_names.append(pvar)
            if arg_type == "bool":
                line = "bool %s = (%s != 0);" % (cname, pvar)
            else:
                line = "%s = (%s)%s;" % (full_decl, c_type, pvar)
            body_items.append((_arg_sort_key(i, arg), line))
        elif arg_type in PY_FLOAT_TYPES:
            pvar = "%s_val" % cname
            parse_fmt.append("d")
            parse_decls.append("double %s" % pvar)
            parse_names.append(pvar)
            body_items.append(
                (_arg_sort_key(i, arg), "%s = (%s)%s;" % (full_decl, c_type, pvar))
            )
        else:
            py_var = "%s_py" % cname
            parse_fmt.append("O")
            parse_decls.append("PyObject *%s" % py_var)
            parse_names.append(py_var)
            body_items.append(
                (
                    _arg_sort_key(i, arg),
                    build_py_func_arg_line(arg, i, func, py_var),
                )
            )

    # NOTE: do not point a NULL user_data at the wrapper object (self/obj).
    # Functions like lv_obj_add_event_cb register multiple callbacks on the same
    # object, distinguished only by their event filter and per-registration
    # user_data.  Reusing the object as user_data makes every registration share
    # one callback dict under a single fixed key, so each call clobbers the
    # previous and only the last-registered callback ever fires.  Leaving
    # user_data NULL matches the MicroPython/CircuitPython emitters: mp_lv_callback
    # then allocates a fresh dict per registration, which LVGL stores as that
    # event descriptor's user_data and the trampoline reads back correctly.

    body_lines = [line for _, line in sorted(body_items, key=lambda t: t[0])]

    parse_block = ""
    if parse_fmt:
        parse_block = (
            '    {decls};\n    if (!PyArg_ParseTuple(py_args, "{fmt}", {names})) {{ PyGILState_Release(gstate); return NULL; }}'
        ).format(
            decls="; ".join(parse_decls),
            fmt="".join(parse_fmt),
            names=", ".join("&" + n for n in parse_names),
        )

    void_self = "" if is_method else "    (void)self;\n"

    pre_lv_call = ""
    post_lv_call = ""
    fname = func.name
    # A timer or a started animation holds its callback dict through LVGL's
    # ext_data free_cb (lvpy_runtime.c): LVGL releases it on every path that
    # frees the timer or the animation copy.
    if fname == "lv_timer_create":
        post_lv_call = "    lvpy_timer_bind(_res);"
    elif fname == "lv_timer_set_cb":
        post_lv_call = "    lvpy_timer_bind(timer);"
    elif fname == "lv_anim_start":
        post_lv_call = "    lvpy_anim_bind(_res);"
    elif fname.endswith("_remove_event_cb_with_user_data"):
        post_lv_call = "    if (_res > 0) lvpy_release_callback_user_data(user_data);"
    elif fname == "lv_obj_remove_event_cb":
        pre_lv_call = (
            "    void *_lvpy_release_ud = lvpy_peek_obj_event_cb_user_data(obj, event_cb, NULL);"
        )
        post_lv_call = "    if (_res) lvpy_release_callback_user_data(_lvpy_release_ud);"
    elif fname == "lv_obj_remove_event_dsc":
        pre_lv_call = "    void *_lvpy_release_ud = lv_event_dsc_get_user_data(dsc);"
        post_lv_call = "    if (_res) lvpy_release_callback_user_data(_lvpy_release_ud);"
    elif fname == "lv_obj_remove_event":
        pre_lv_call = (
            "    lv_event_dsc_t *_lvpy_release_dsc = lv_obj_get_event_dsc(obj, index);\n"
            "    void *_lvpy_release_ud = _lvpy_release_dsc ? lv_event_dsc_get_user_data(_lvpy_release_dsc) : NULL;"
        )
        post_lv_call = "    if (_res) lvpy_release_callback_user_data(_lvpy_release_ud);"
    elif fname == "lv_indev_remove_event":
        pre_lv_call = (
            "    lv_event_dsc_t *_lvpy_release_dsc = lv_indev_get_event_dsc(indev, index);\n"
            "    void *_lvpy_release_ud = _lvpy_release_dsc ? lv_event_dsc_get_user_data(_lvpy_release_dsc) : NULL;"
        )
        post_lv_call = "    if (_res) lvpy_release_callback_user_data(_lvpy_release_ud);"

    if allow_threads:
        lv_call_block = """    {result_decl}lvpy_lock();
    Py_BEGIN_ALLOW_THREADS
    {c_call}
    Py_END_ALLOW_THREADS
    lvpy_unlock();"""
    else:
        lv_call_block = """    {result_decl}lvpy_lock();
    {c_call}
    lvpy_unlock();"""

    print(
        """
/*
 * {module_name} extension definition for:
 * {print_func}
 */
static PyObject *py_{func}(PyObject *self, PyObject *py_args, PyObject *py_kwds)
{{
    PyGILState_STATE gstate = PyGILState_Ensure();
{void_self}    (void)py_kwds;
{parse}
    {body}
    if (PyErr_Occurred()) {{ PyGILState_Release(gstate); return NULL; }}
    {pre_lv_call}
{lv_call_block}
    {post_lv_call}
    PyGILState_Release(gstate);
    {build_return}
}}

static PyMethodDef py_{func}_def = {{
    "{py_name}",
    (PyCFunction)py_{func},
    METH_VARARGS | METH_KEYWORDS,
    NULL
}};
""".format(
            module_name=module_name,
            func=emit_name,
            c_func=func.name,
            py_name=sanitize(func.name),
            print_func=gen.visit(func),
            void_self=void_self,
            parse=parse_block,
            body="\n    ".join(body_lines),
            pre_lv_call=pre_lv_call,
            post_lv_call=post_lv_call,
            result_decl=result_decl,
            lv_call_block=lv_call_block.format(
                result_decl=result_decl,
                c_call=c_call.format(
                    func_ptr=prototype_str,
                    c_func=func.name,
                    send_args=", ".join(send_args),
                ),
            ),
            build_return=build_return,
        )
    )
    if struct_method:
        generated_struct_method_funcs[emit_name] = True
        generated_struct_method_funcs[func.name] = emit_name
    else:
        generated_funcs[func.name] = True


def _resolved_struct_method_py_func_name(func_name, generated_struct_method_funcs):
    emit_name = func_name + "_struct_method"
    target = generated_struct_method_funcs.get(emit_name)
    if target is True:
        return emit_name
    if isinstance(target, str):
        return target
    target = generated_struct_method_funcs.get(func_name)
    if target is True:
        return emit_name
    if isinstance(target, str):
        return target
    return None


def _resolved_py_func_name(func_name, generated_funcs):
    target = generated_funcs.get(func_name)
    if target is True:
        return func_name
    if isinstance(target, str):
        return target
    return None


def gen_py_obj(obj_name):
    sanitize = _h("sanitize")
    module_name = _h("module_name")
    get_methods = _h("get_methods")
    has_ctor = _h("has_ctor")
    get_ctor = _h("get_ctor")
    parent_obj_names = _h("parent_obj_names")
    generated_funcs = _h("generated_funcs")
    method_name_from_func_name = _h("method_name_from_func_name")
    obj_metadata = _h("obj_metadata")
    func_metadata = _h("func_metadata")
    get_enum_members = _h("get_enum_members")
    get_enum_member_name = _h("get_enum_member_name")
    enums = _h("enums")
    enum_referenced = _h("enum_referenced")

    obj_metadata[obj_name] = {"members": collections.OrderedDict()}

    for method in get_methods(obj_name):
        try:
            gen_py_func(method, obj_name)
        except Exception as exp:
            _h("gen_func_error")(method, exp)

    obj_metadata[obj_name]["members"].update(
        {
            method_name_from_func_name(method.name): func_metadata[method.name]
            for method in get_methods(obj_name)
            if method.name in func_metadata
        }
    )
    parent = parent_obj_names.get(obj_name)
    if parent and parent in obj_metadata:
        obj_metadata[obj_name]["members"].update(obj_metadata[parent]["members"])
    obj_metadata[obj_name]["members"].update(
        {
            get_enum_member_name(enum_member_name): {"type": "enum_member"}
            for enum_member_name in get_enum_members(obj_name)
        }
    )
    for enum_name in enums.keys():
        if not is_method_of(enum_name, obj_name):
            continue
        member_name = method_name_from_func_name(enum_name)
        obj_metadata[obj_name]["members"][member_name] = {"type": "enum_type"}
        if enum_name in obj_metadata:
            obj_metadata[obj_name]["members"][member_name].update(obj_metadata[enum_name])
        if is_widget_scoped_only_enum(enum_name):
            enum_referenced[enum_name] = True

    ctor_name = "lv_obj_create"
    if has_ctor(obj_name):
        ctor = get_ctor(obj_name)
        ctor_name = ctor.name
        try:
            gen_py_func(ctor, None)
        except Exception as exp:
            _h("gen_func_error")(ctor, exp)

    ctor_py = _resolved_py_func_name(ctor_name, generated_funcs) or ctor_name

    method_defs = []
    for method in get_methods(obj_name):
        py_func = _resolved_py_func_name(method.name, generated_funcs)
        if py_func:
            method_defs.append(
                '    {{"{name}", (PyCFunction)py_{func}, METH_VARARGS | METH_KEYWORDS, NULL}},'.format(
                    name=sanitize(method_name_from_func_name(method.name)),
                    func=py_func,
                )
            )

    parent = parent_obj_names.get(obj_name)
    if parent:
        parent_base = "&py_lv_%s_type" % sanitize(parent)
    elif sanitize(obj_name) == "obj":
        parent_base = "NULL"
    else:
        parent_base = "&py_lv_obj_type"

    print(
        """
/*
 * {module_name} {obj} object definitions (CPython)
 */
static PyObject *py_lv_{obj}_call(PyObject *type, PyObject *py_args, PyObject *py_kwds)
{{
    (void)type;
    return py_{ctor}(type, py_args, py_kwds);
}}

static PyObject *py_lv_{obj}_new(PyTypeObject *type, PyObject *py_args, PyObject *py_kwds)
{{
    return py_{ctor}((PyObject *)type, py_args, py_kwds);
}}

static void py_lv_{obj}_dealloc(py_lv_obj_t *self)
{{
    lvpy_dealloc_obj(self);
}}

static PyMethodDef py_lv_{obj}_methods[] = {{
{methods}
    {{NULL, NULL, 0, NULL}}
}};

PyTypeObject py_lv_{obj}_type = {{
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "lvgl.{obj}",
    .tp_basicsize = sizeof(py_lv_obj_t),
    .tp_dealloc = (destructor)py_lv_{obj}_dealloc,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_base = {parent_base},
    .tp_new = (newfunc)py_lv_{obj}_new,
    .tp_methods = py_lv_{obj}_methods,
    .tp_call = (ternaryfunc)py_lv_{obj}_call,
}};

static py_lv_obj_type_t py_lv_{obj}_mapping = {{
    .lv_obj_class = &lv_{obj}_class,
    .py_type = &py_lv_{obj}_type,
}};
""".format(
            module_name=module_name,
            obj=sanitize(obj_name),
            ctor=ctor_py,
            methods="\n".join(method_defs) if method_defs else "",
            parent_base=parent_base,
        )
    )
