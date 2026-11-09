# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Main MP-style C emitter (mp_obj_t API); used by MicroPython and CircuitPython."""
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
    ctor_name_from_obj_name,
    export_name,
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
    conversion_available,
    function_reuse_allowed,
    function_return_lowering,
    failed_generation,
    mp_obj_get_ull_to_bytes_source,
    object_generation_order,
    public_struct_c_names,
    public_enum_module_names,
    require_one_of_target_lowerings,
    resolve_emitter_headers,
    struct_pointer_helpers_source,
    target_banner,
)
from .runtime_exports import filter_module_funcs_for_target, filter_registration_module_funcs
from .util import eprint, guarded, memoize
from .context import EmitterResult


def emit_c(ctx):
    """Emit MP-style C from one context without module-level run state."""
    print = ctx.emit_print
    args = ctx.args
    base_obj_name = ctx.base_obj_name
    base_obj_type = ctx.base_obj_type
    blobs = ctx.blobs
    callback_metadata = ctx.callback_metadata
    cmd_line = ctx.cmd_line
    enum_defs = ctx.enum_defs
    func_metadata = ctx.func_metadata
    func_prototypes = ctx.func_prototypes
    func_typedefs = ctx.func_typedefs
    funcs = ctx.funcs
    gen = ctx.gen
    int_constants = ctx.int_constants
    lv_base_obj_pattern = ctx.lv_base_obj_pattern
    lv_func_returns_array = ctx.lv_func_returns_array
    lv_mp_type = ctx.lv_mp_type
    lv_str_enum_pattern = ctx.lv_str_enum_pattern
    lv_to_mp = ctx.lv_to_mp
    lv_to_mp_byref = ctx.lv_to_mp_byref
    lv_to_mp_funcptr = ctx.lv_to_mp_funcptr
    lvgl_json = ctx.lvgl_json
    module_name = ctx.module_name
    mp_to_lv = ctx.mp_to_lv
    obj_metadata = ctx.obj_metadata
    obj_names = ctx.obj_names
    parent_obj_names = ctx.parent_obj_names
    parser = ctx.parser
    pp_cmd = ctx.pp_cmd
    structs = ctx.structs
    structs_without_typedef = ctx.structs_without_typedef
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

    _emit_target, _emit_max_phase = require_one_of_target_lowerings(
        "micropython", "circuitpython"
    )
    _target_banner = target_banner(
        _emit_target, include=_emit_target != "micropython"
    )

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
 * Mpy includes
 */

#include <stdlib.h>
#include <string.h>
#include "py/obj.h"
#include "py/objint.h"
#include "py/objstr.h"
#include "py/objtuple.h"
#include "py/runtime.h"
#include "py/binary.h"
#include "py/objarray.h"
#include "py/objtype.h"
#include "py/objexcept.h"

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
#define LV_OBJ_T {obj_type}

typedef struct mp_lv_obj_type_t {{
    const lv_obj_class_t *lv_obj_class;
    const mp_obj_type_t *mp_obj_type;
}} mp_lv_obj_type_t;

static const mp_lv_obj_type_t mp_lv_{base_obj}_type;
static const mp_lv_obj_type_t *mp_lv_obj_types[];

static inline const mp_obj_type_t *get_BaseObj_type(void)
{{
    return mp_lv_{base_obj}_type.mp_obj_type;
}}

MP_DEFINE_EXCEPTION(LvReferenceError, Exception)
    """.format(obj_type=base_obj_type, base_obj=base_obj_name)
        )

    #
    # Emit Mpy helper functions
    #

    _mp_obj_get_ull_to_bytes = mp_obj_get_ull_to_bytes_source()

    print(
        """
/*
 * Helper functions
 */

#ifndef GENMPY_UNUSED
#ifdef __GNUC__
#define GENMPY_UNUSED __attribute__ ((unused))
#else
#define GENMPY_UNUSED
#endif // __GNUC__
#endif // GENMPY_UNUSED

// Custom function mp object

typedef mp_obj_t (*mp_fun_ptr_var_t)(size_t n, const mp_obj_t *, void *ptr);

typedef struct mp_lv_obj_fun_builtin_var_t {
    mp_obj_base_t base;
    mp_uint_t n_args;
    mp_fun_ptr_var_t mp_fun;
    void *lv_fun;
} mp_lv_obj_fun_builtin_var_t;

static mp_obj_t lv_fun_builtin_var_call(mp_obj_t self_in, size_t n_args, size_t n_kw, const mp_obj_t *args);
static mp_int_t mp_func_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags);

GENMPY_UNUSED static MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_type_fun_builtin_var,
    MP_QSTR_function,
    MP_TYPE_FLAG_BINDS_SELF | MP_TYPE_FLAG_BUILTIN_FUN,
    call, lv_fun_builtin_var_call,
    unary_op, mp_obj_int_unary_op,
    buffer, mp_func_get_buffer
);

GENMPY_UNUSED static MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_type_fun_builtin_static_var,
    MP_QSTR_function,
    MP_TYPE_FLAG_BUILTIN_FUN,
    call, lv_fun_builtin_var_call,
    unary_op, mp_obj_int_unary_op,
    buffer, mp_func_get_buffer
);

static mp_obj_t lv_fun_builtin_var_call(mp_obj_t self_in, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    assert(MP_OBJ_IS_TYPE(self_in, &mp_lv_type_fun_builtin_var) ||
           MP_OBJ_IS_TYPE(self_in, &mp_lv_type_fun_builtin_static_var));
    mp_lv_obj_fun_builtin_var_t *self = MP_OBJ_TO_PTR(self_in);
    mp_arg_check_num(n_args, n_kw, self->n_args, self->n_args, false);
    return self->mp_fun(n_args, args, self->lv_fun);
}

static mp_int_t mp_func_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    (void)flags;
    assert(MP_OBJ_IS_TYPE(self_in, &mp_lv_type_fun_builtin_var) ||
           MP_OBJ_IS_TYPE(self_in, &mp_lv_type_fun_builtin_static_var));
    mp_lv_obj_fun_builtin_var_t *self = MP_OBJ_TO_PTR(self_in);

    bufinfo->buf = &self->lv_fun;
    bufinfo->len = sizeof(self->lv_fun);
    bufinfo->typecode = BYTEARRAY_TYPECODE;
    return 0;
}

#define MP_DEFINE_CONST_LV_FUN_OBJ_VAR(obj_name, n_args, mp_fun, lv_fun) \\
    const mp_lv_obj_fun_builtin_var_t obj_name = \\
        {{&mp_lv_type_fun_builtin_var}, n_args, mp_fun, lv_fun}

#define MP_DEFINE_CONST_LV_FUN_OBJ_STATIC_VAR(obj_name, n_args, mp_fun, lv_fun) \\
    const mp_lv_obj_fun_builtin_var_t obj_name = \\
        {{&mp_lv_type_fun_builtin_static_var}, n_args, mp_fun, lv_fun}

// Casting

typedef struct mp_lv_struct_t
{
    mp_obj_base_t base;
    void *data;
} mp_lv_struct_t;

static const mp_lv_struct_t mp_lv_null_obj;

#ifdef LV_OBJ_T
static mp_int_t mp_lv_obj_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags);
#else
static mp_int_t mp_lv_obj_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags){ return 0; }
#endif

static mp_int_t mp_blob_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags);

static mp_obj_t get_native_obj(mp_obj_t mp_obj)
{
    if (!MP_OBJ_IS_OBJ(mp_obj)) return mp_obj;
    const mp_obj_type_t *native_type = ((mp_obj_base_t*)mp_obj)->type;
    if (native_type == NULL)
        return NULL;
    if (MP_OBJ_TYPE_GET_SLOT_OR_NULL(native_type, parent) == NULL ||
        (MP_OBJ_TYPE_GET_SLOT_OR_NULL(native_type, buffer) == mp_blob_get_buffer) ||
        (MP_OBJ_TYPE_GET_SLOT_OR_NULL(native_type, buffer) == mp_lv_obj_get_buffer))
       return mp_obj;
    while (MP_OBJ_TYPE_GET_SLOT_OR_NULL(native_type, parent)) native_type = MP_OBJ_TYPE_GET_SLOT(native_type, parent);
    return mp_obj_cast_to_native_base(mp_obj, MP_OBJ_FROM_PTR(native_type));
}

static mp_obj_t dict_to_struct(mp_obj_t dict, const mp_obj_type_t *type);

static mp_obj_t make_new_lv_struct(
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args);

static mp_obj_t cast(mp_obj_t mp_obj, const mp_obj_type_t *mp_type)
{
    mp_obj_t res = NULL;
    if (mp_obj == mp_const_none && MP_OBJ_TYPE_GET_SLOT_OR_NULL(mp_type, make_new) == &make_new_lv_struct) {
        res = MP_OBJ_FROM_PTR(&mp_lv_null_obj);
    } else if (MP_OBJ_IS_OBJ(mp_obj)) {
        res = get_native_obj(mp_obj);
        if (res){
            const mp_obj_type_t *res_type = ((mp_obj_base_t*)res)->type;
            if (res_type != mp_type){
                if (res_type == &mp_type_dict &&
                    MP_OBJ_TYPE_GET_SLOT_OR_NULL(mp_type, make_new) == &make_new_lv_struct)
                        res = dict_to_struct(res, mp_type);
                else res = NULL;
            }
        }
    }
    if (res == NULL) nlr_raise(
        mp_obj_new_exception_msg_varg(
            &mp_type_SyntaxError, MP_ERROR_TEXT("Can't convert %s to %s!"), mp_obj_get_type_str(mp_obj), qstr_str(mp_type->name)));
    return res;
}

// object handling
// This section is enabled only when objects are supported

#ifdef LV_OBJ_T

typedef struct mp_lv_obj_t {
    mp_obj_base_t base;
    LV_OBJ_T *lv_obj;
    LV_OBJ_T *callbacks;
} mp_lv_obj_t;

static inline LV_OBJ_T *mp_to_lv(mp_obj_t mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    mp_obj_t native_obj = get_native_obj(mp_obj);
    if (native_obj == MP_OBJ_NULL ||
        MP_OBJ_TYPE_GET_SLOT_OR_NULL(mp_obj_get_type(native_obj), buffer) != mp_lv_obj_get_buffer) {
        nlr_raise(
            mp_obj_new_exception_msg_varg(
                &mp_type_SyntaxError,
                MP_ERROR_TEXT("Can't convert %s to an LVGL object!"),
                mp_obj_get_type_str(mp_obj)));
    }
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(native_obj);
    if (mp_lv_obj->lv_obj == NULL) {
        nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_LvReferenceError, MP_ERROR_TEXT("Referenced object was deleted!")));
    }
    return mp_lv_obj->lv_obj;
}

static inline LV_OBJ_T *mp_get_callbacks(mp_obj_t mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    mp_lv_obj_t *mp_lv_obj = MP_OBJ_TO_PTR(get_native_obj(mp_obj));
    if (mp_lv_obj == NULL)
        nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_SyntaxError, MP_ERROR_TEXT("'user_data' argument must be either a dict or None!")));
    if (!mp_lv_obj->callbacks) mp_lv_obj->callbacks = mp_obj_new_dict(0);
    return mp_lv_obj->callbacks;
}

static inline const mp_obj_type_t *get_BaseObj_type(void);

static void mp_lv_delete_cb(lv_event_t * e)
{
    LV_OBJ_T *lv_obj = e->current_target;
    if (lv_obj){
        mp_lv_obj_t *self = lv_obj->user_data;
        if (self) {
            self->lv_obj = NULL;
        }
    }
}

static inline mp_obj_t lv_to_mp(LV_OBJ_T *lv_obj)
{
    if (lv_obj == NULL) return mp_const_none;
    mp_lv_obj_t *self = (mp_lv_obj_t*)lv_obj->user_data;
    if (!self)
    {
        // Find the object type
        const mp_obj_type_t *mp_obj_type = get_BaseObj_type();
        const lv_obj_class_t *lv_obj_class = lv_obj_get_class(lv_obj);
        const mp_lv_obj_type_t **iter = &mp_lv_obj_types[0];
        for (; *iter; iter++) {
            if ((*iter)->lv_obj_class == lv_obj_class) {
                mp_obj_type = (*iter)->mp_obj_type;
                break;
            }
        }

        // Create the MP object
        self = m_new_obj(mp_lv_obj_t);
        *self = (mp_lv_obj_t){
            .base = {(const mp_obj_type_t *)mp_obj_type},
            .lv_obj = lv_obj,
            .callbacks = NULL,
        };

        // Register the Python object in user_data
        lv_obj->user_data = self;

        // Register a "Delete" event callback
        lv_obj_add_event_cb(lv_obj, mp_lv_delete_cb, LV_EVENT_DELETE, NULL);
    }
    return MP_OBJ_FROM_PTR(self);
}

static void* mp_to_ptr(mp_obj_t self_in);

static mp_obj_t cast_obj_type(const mp_obj_type_t* type, mp_obj_t obj)
{
    mp_lv_obj_t *self = m_new_obj(mp_lv_obj_t);
    *self = (mp_lv_obj_t){
        .base = {type},
        .lv_obj = mp_to_ptr(obj),
        .callbacks = NULL,
    };
    if (!self->lv_obj) return mp_const_none;
    return MP_OBJ_FROM_PTR(self);
}

static mp_obj_t cast_obj(mp_obj_t type_obj, mp_obj_t obj)
{
    return cast_obj_type((const mp_obj_type_t *)type_obj, obj);
}

static mp_obj_t make_new(
    const mp_lv_obj_fun_builtin_var_t *lv_obj_var,
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{
    mp_obj_t lv_obj;
    if (n_args == 0 && n_kw == 0) // allow no args, and pass NULL as parent in such case
    {
        const mp_obj_t no_args[] = {mp_const_none};
        lv_obj = mp_call_function_n_kw(MP_OBJ_FROM_PTR(lv_obj_var), 1, 0, no_args);
    }
    else
    {
        lv_obj = mp_call_function_n_kw(MP_OBJ_FROM_PTR(lv_obj_var), n_args, n_kw, args);
    }

    if (!lv_obj) return mp_const_none;

    mp_lv_obj_t *self = MP_OBJ_TO_PTR(lv_obj);
    if (self->base.type != type)
        return cast_obj_type(type, lv_obj);
    return lv_obj;
}

static MP_DEFINE_CONST_FUN_OBJ_2(cast_obj_obj, cast_obj);
static MP_DEFINE_CONST_CLASSMETHOD_OBJ(cast_obj_class_method, MP_ROM_PTR(&cast_obj_obj));

static mp_int_t mp_lv_obj_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    (void)flags;
    mp_lv_obj_t *self = MP_OBJ_TO_PTR(self_in);

    bufinfo->buf = &self->lv_obj;
    bufinfo->len = sizeof(self->lv_obj);
    bufinfo->typecode = BYTEARRAY_TYPECODE;
    return 0;
}

static mp_obj_t mp_lv_obj_binary_op(mp_binary_op_t op, mp_obj_t lhs_in, mp_obj_t rhs_in)
{
    mp_lv_obj_t *lhs = MP_OBJ_TO_PTR(lhs_in);
    mp_lv_obj_t *rhs = MP_OBJ_TO_PTR(rhs_in);
    switch (op)
    {
        case MP_BINARY_OP_EQUAL:
            return mp_obj_new_bool(lhs->lv_obj == rhs->lv_obj);
        case MP_BINARY_OP_NOT_EQUAL:
            return mp_obj_new_bool(lhs->lv_obj != rhs->lv_obj);
        default:
            return MP_OBJ_NULL;
    }
}

// Register LVGL root pointers
MP_REGISTER_ROOT_POINTER(void *mp_lv_roots);
MP_REGISTER_ROOT_POINTER(void *mp_lv_user_data);
MP_REGISTER_ROOT_POINTER(int mp_lv_roots_initialized);
MP_REGISTER_ROOT_POINTER(int lvgl_mod_initialized);

void *mp_lv_user_data;
int lvgl_mod_initialized = 0;

/* LV_GLOBAL_CUSTOM() must use this — not a cached C global. GC moves the
 * lv_global_t allocation and only updates MP_STATE_VM(mp_lv_roots). */
void *mp_lv_get_roots(void)
{
    return MP_STATE_VM(mp_lv_roots);
}

void mp_lv_init_gc(void)
{
    if (!MP_STATE_VM(mp_lv_roots_initialized)) {
        // mp_printf(&mp_plat_print, "[ INIT GC ]");
        MP_STATE_VM(mp_lv_roots) = m_new0(lv_global_t, 1);
        MP_STATE_VM(mp_lv_roots_initialized) = 1;
    }
}

void mp_lv_deinit_gc(void)
{

    // mp_printf(&mp_plat_print, "[ DEINIT GC ]");
    MP_STATE_VM(mp_lv_roots) = NULL;
    MP_STATE_VM(mp_lv_user_data) = NULL;
    MP_STATE_VM(mp_lv_roots_initialized) = 0;
    MP_STATE_VM(lvgl_mod_initialized) = 0;
    lvgl_mod_initialized = 0;

}

#ifndef LV_CIRCUITPYTHON_BUILD
static mp_obj_t lvgl_mod_init(void) {
    mp_lv_init_gc();
    if (!lv_is_initialized()) {
        lv_init();
    }
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(lvgl_mod_init_obj, lvgl_mod_init);


static mp_obj_t lvgl_mod_deinit(void) {
    if (lv_is_initialized()) {
        lv_deinit();
    }
    mp_lv_deinit_gc();
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_0(lvgl_mod_deinit_obj, lvgl_mod_deinit);
#endif /* !LV_CIRCUITPYTHON_BUILD */

#else // LV_OBJ_T

typedef struct mp_lv_obj_type_t {
    mp_obj_type_t *mp_obj_type;
} mp_lv_obj_type_t;

#endif

static inline mp_obj_t convert_to_bool(bool b)
{
    return b? mp_const_true: mp_const_false;
}

static inline mp_obj_t convert_to_str(const char *str)
{
    return str? mp_obj_new_str(str, strlen(str)): mp_const_none;
}

static inline const char *convert_from_str(mp_obj_t str)
{
    if (str == NULL || str == mp_const_none)
        return NULL;

    if (MP_OBJ_IS_TYPE(str, &mp_type_bytearray) ||
        MP_OBJ_IS_TYPE(str, &mp_type_memoryview)) {
            mp_buffer_info_t buffer_info;
            if (mp_get_buffer(str, &buffer_info, MP_BUFFER_READ)) {
                return buffer_info.buf;
            }
    }

    return mp_obj_str_get_str(str);
}

// struct handling

static mp_lv_struct_t *mp_to_lv_struct(mp_obj_t mp_obj)
{
    if (mp_obj == NULL || mp_obj == mp_const_none) return NULL;
    mp_obj_t native_obj = get_native_obj(mp_obj);
    if ( (!MP_OBJ_IS_OBJ(native_obj)) || (MP_OBJ_TYPE_GET_SLOT_OR_NULL(mp_obj_get_type(native_obj), make_new) != &make_new_lv_struct) ) nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_SyntaxError, MP_ERROR_TEXT("Expected Struct object!")));
    mp_lv_struct_t *mp_lv_struct = MP_OBJ_TO_PTR(native_obj);
    return mp_lv_struct;
}

static inline size_t get_lv_struct_size(const mp_obj_type_t *type)
{
    mp_obj_dict_t *self = MP_OBJ_TO_PTR(MP_OBJ_TYPE_GET_SLOT(type, locals_dict));
    mp_map_elem_t *elem = mp_map_lookup(&self->map, MP_OBJ_NEW_QSTR(MP_QSTR___SIZE__), MP_MAP_LOOKUP);
    if (elem == NULL) {
        return 0;
    } else {
        return (size_t)mp_obj_get_int(elem->value);
    }
}

static mp_obj_t make_new_lv_struct(
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{
    if ((!MP_OBJ_IS_TYPE(type, &mp_type_type)) || MP_OBJ_TYPE_GET_SLOT_OR_NULL(type, make_new) != &make_new_lv_struct)
        nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_SyntaxError, MP_ERROR_TEXT("Argument is not a struct type!")));
    size_t size = get_lv_struct_size(type);
    mp_arg_check_num(n_args, n_kw, 0, 1, false);
    mp_lv_struct_t *self = m_new_obj(mp_lv_struct_t);
    mp_lv_struct_t *other = (n_args > 0) && (!mp_obj_is_int(args[0])) ? mp_to_lv_struct(cast(args[0], type)): NULL;
    size_t count = (n_args > 0) && (mp_obj_is_int(args[0]))? mp_obj_get_int(args[0]): 1;
    *self = (mp_lv_struct_t){
        .base = {type},
        .data = (size == 0 || (other && other->data == NULL))? NULL: m_malloc(size * count)
    };
    if (self->data) {
        if (other) {
            memcpy(self->data, other->data, size * count);
        } else {
            memset(self->data, 0, size * count);
        }
    }
    return MP_OBJ_FROM_PTR(self);
}

static mp_obj_t lv_struct_binary_op(mp_binary_op_t op, mp_obj_t lhs_in, mp_obj_t rhs_in)
{
    mp_lv_struct_t *lhs = MP_OBJ_TO_PTR(lhs_in);
    mp_lv_struct_t *rhs = MP_OBJ_TO_PTR(rhs_in);
    switch (op)
    {
        case MP_BINARY_OP_EQUAL:
            return mp_obj_new_bool(lhs->data == rhs->data);
        case MP_BINARY_OP_NOT_EQUAL:
            return mp_obj_new_bool(lhs->data != rhs->data);
        default:
            return MP_OBJ_NULL;
    }
}

static mp_obj_t lv_struct_subscr(mp_obj_t self_in, mp_obj_t index, mp_obj_t value)
{
    mp_lv_struct_t *self = mp_to_lv_struct(self_in);

    if ((!self) || (!self->data))
        return NULL;
    if (!mp_obj_is_int(index)) {
        nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_SyntaxError, MP_ERROR_TEXT("Subscript index must be an integer!")));
    }

    const mp_obj_type_t *type = mp_obj_get_type(self_in);
    size_t element_size = get_lv_struct_size(type);
    if (element_size == 0) return mp_const_none;
    size_t element_index = mp_obj_get_int(index);
    void *element_addr = (byte*)self->data + element_size*element_index;

    if (value == MP_OBJ_NULL) {
        memset(element_addr, 0, element_size);
        return self_in;
    }

    mp_lv_struct_t *element_at_index = m_new_obj(mp_lv_struct_t);
    *element_at_index = (mp_lv_struct_t){
        .base = {type},
        .data = element_addr
    };

    if (value != MP_OBJ_SENTINEL){
        mp_lv_struct_t *other = mp_to_lv_struct(cast(value, type));
        if ((!other) || (!other->data))
            return NULL;
        memcpy(element_at_index->data, other->data, element_size);
    }

    return MP_OBJ_FROM_PTR(element_at_index);
}

GENMPY_UNUSED static void *copy_buffer(const void *buffer, size_t size)
{
    void *new_buffer = m_malloc(size);
    memcpy(new_buffer, buffer, size);
    return new_buffer;
}

// Reference an existing lv struct (or part of it)

static mp_obj_t lv_to_mp_struct(const mp_obj_type_t *type, void *lv_struct)
{
    if (lv_struct == NULL) return mp_const_none;
    mp_lv_struct_t *self = m_new_obj(mp_lv_struct_t);
    *self = (mp_lv_struct_t){
        .base = {type},
        .data = lv_struct
    };
    return MP_OBJ_FROM_PTR(self);
}

static void call_parent_methods(mp_obj_t obj, qstr attr, mp_obj_t *dest)
{
    const mp_obj_type_t *type = mp_obj_get_type(obj);
    while (MP_OBJ_TYPE_HAS_SLOT(type, locals_dict)) {
        // generic method lookup
        // this is a lookup in the object (ie not class or type)
        assert(MP_OBJ_TYPE_GET_SLOT(type, locals_dict)->base.type == &mp_type_dict); // MicroPython restriction, for now
        mp_map_t *locals_map = &MP_OBJ_TYPE_GET_SLOT(type, locals_dict)->map;
        mp_map_elem_t *elem = mp_map_lookup(locals_map, MP_OBJ_NEW_QSTR(attr), MP_MAP_LOOKUP);
        if (elem != NULL) {
            mp_convert_member_lookup(obj, type, elem->value, dest);
            break;
        }
        if (MP_OBJ_TYPE_GET_SLOT_OR_NULL(type, parent) == NULL) {
            break;
        }
        // search parents
        type = MP_OBJ_TYPE_GET_SLOT(type, parent);
    }
}

// Convert dict to struct

static mp_obj_t dict_to_struct(mp_obj_t dict, const mp_obj_type_t *type)
{
    mp_obj_t mp_struct = make_new_lv_struct(type, 0, 0, NULL);
    mp_obj_t native_dict = cast(dict, &mp_type_dict);
    mp_map_t *map = mp_obj_dict_get_map(native_dict);
    if (map == NULL) return mp_const_none;
    for (uint i = 0; i < map->alloc; i++) {
        mp_obj_t key = map->table[i].key;
        mp_obj_t value = map->table[i].value;
        if (key != MP_OBJ_NULL) {
            mp_obj_t dest[] = {MP_OBJ_SENTINEL, value};
            MP_OBJ_TYPE_GET_SLOT(type, attr)(mp_struct, mp_obj_str_get_qstr(key), dest);
            if (dest[0]) nlr_raise(
                mp_obj_new_exception_msg_varg(
                    &mp_type_SyntaxError, MP_ERROR_TEXT("Cannot set field %s on struct %s!"), qstr_str(mp_obj_str_get_qstr(key)), qstr_str(type->name)));
        }
    }
    return mp_struct;
}

// Convert mp object to ptr

static void* mp_to_ptr(mp_obj_t self_in)
{
    mp_buffer_info_t buffer_info;
    if (self_in == NULL || self_in == mp_const_none)
        return NULL;

//    if (MP_OBJ_IS_INT(self_in))
//        return (void*)mp_obj_get_int(self_in);

    // If an object is user instance, take it as is so it could be used as user_data
    if (mp_obj_is_instance_type(mp_obj_get_type(self_in))){
        return MP_OBJ_TO_PTR(self_in);
    }

    if (!mp_get_buffer(self_in, &buffer_info, MP_BUFFER_READ)) {
        // No buffer protocol - this is not a Struct or a Blob, it's some other mp object.
        // We only allow setting dict directly, since it's useful to setting user_data for passing data to C.
        // On other cases throw an exception, to avoid a crash later
        if (MP_OBJ_IS_TYPE(self_in, &mp_type_dict))
            return MP_OBJ_TO_PTR(self_in);
        else nlr_raise(
                mp_obj_new_exception_msg_varg(
                    &mp_type_SyntaxError, MP_ERROR_TEXT("Cannot convert '%s' to pointer!"), mp_obj_get_type_str(self_in)));
    }

    if (MP_OBJ_IS_STR_OR_BYTES(self_in) ||
        MP_OBJ_IS_TYPE(self_in, &mp_type_bytearray) ||
        MP_OBJ_IS_TYPE(self_in, &mp_type_memoryview))
            return buffer_info.buf;
    else
    {
        void *result;
        if (buffer_info.len != sizeof(result) || buffer_info.typecode != BYTEARRAY_TYPECODE){
            nlr_raise(
                mp_obj_new_exception_msg_varg(
                    &mp_type_SyntaxError, MP_ERROR_TEXT("Cannot convert %s to pointer! (buffer does not represent a pointer)"), mp_obj_get_type_str(self_in)));
        }
        memcpy(&result, buffer_info.buf, sizeof(result));
        return result;
    }
}

// Blob is a wrapper for void*

static void mp_blob_print(const mp_print_t *print,
    mp_obj_t self_in,
    mp_print_kind_t kind)
{
    mp_printf(print, "Blob");
}

static mp_int_t mp_blob_get_buffer(mp_obj_t self_in, mp_buffer_info_t *bufinfo, mp_uint_t flags) {
    (void)flags;
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(self_in);

    bufinfo->buf = &self->data;
    bufinfo->len = sizeof(self->data);
    bufinfo->typecode = BYTEARRAY_TYPECODE;
    return 0;
}

static const mp_obj_fun_builtin_var_t mp_lv_dereference_obj;

// Sometimes (but not always!) Blob represents a Micropython object.
// In such cases it's safe to cast the Blob back to the Micropython object
// cast argument is the underlying object type, and it's optional.

static mp_obj_t mp_blob_cast(size_t argc, const mp_obj_t *argv)
{
    mp_obj_t self = argv[0];
    void *ptr = mp_to_ptr(self);
    if (argc == 1) return MP_OBJ_FROM_PTR(ptr);
    mp_obj_t type = argv[1];
    if (!MP_OBJ_IS_TYPE(type, &mp_type_type))
        nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_SyntaxError, MP_ERROR_TEXT("Cast argument must be a type!")));
    return cast(MP_OBJ_FROM_PTR(ptr), type);
}

static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mp_blob_cast_obj, 1, 2, mp_blob_cast);

static const mp_rom_map_elem_t mp_blob_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___dereference__), MP_ROM_PTR(&mp_lv_dereference_obj) },
    { MP_ROM_QSTR(MP_QSTR___cast__), MP_ROM_PTR(&mp_blob_cast_obj) },
};

static MP_DEFINE_CONST_DICT(mp_blob_locals_dict, mp_blob_locals_dict_table);

static MP_DEFINE_CONST_OBJ_TYPE(
    mp_blob_type,
    MP_QSTR_Blob,
    MP_TYPE_FLAG_NONE,
    binary_op, lv_struct_binary_op,
    print, mp_blob_print,
    locals_dict, &mp_blob_locals_dict,
    buffer, mp_blob_get_buffer
);

static const mp_lv_struct_t mp_lv_null_obj = { {&mp_blob_type}, NULL };

static inline mp_obj_t ptr_to_mp(void *data)
{
    return lv_to_mp_struct(&mp_blob_type, data);
}

// Cast pointer to struct

static mp_obj_t mp_lv_cast(mp_obj_t type_obj, mp_obj_t ptr_obj)
{
    void *ptr = mp_to_ptr(ptr_obj);
    if (!ptr) return mp_const_none;
    mp_lv_struct_t *self = m_new_obj(mp_lv_struct_t);
    *self = (mp_lv_struct_t){
        .base = {(const mp_obj_type_t*)type_obj},
        .data = ptr
    };
    return MP_OBJ_FROM_PTR(self);
}

// Cast instance. Can be used in ISR when memory allocation is prohibited

static inline mp_obj_t mp_lv_cast_instance(mp_obj_t self_in, mp_obj_t ptr_obj)
{
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(self_in);
    self->data = mp_to_ptr(ptr_obj);
    return self_in;
}

static MP_DEFINE_CONST_FUN_OBJ_2(mp_lv_cast_obj, mp_lv_cast);
static MP_DEFINE_CONST_CLASSMETHOD_OBJ(mp_lv_cast_class_method, MP_ROM_PTR(&mp_lv_cast_obj));

static MP_DEFINE_CONST_FUN_OBJ_2(mp_lv_cast_instance_obj, mp_lv_cast_instance);

// Dereference a struct/blob. This allows access to the raw data the struct holds

static mp_obj_t mp_lv_dereference(size_t argc, const mp_obj_t *argv)
{
    mp_obj_t self_in = argv[0];
    mp_obj_t size_in = argc > 1? argv[1]: mp_const_none;
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(self_in);
    size_t size = 0;
    if (size_in == mp_const_none){
        const mp_obj_type_t *type = self->base.type;
        size = get_lv_struct_size(type);
    } else {
        size = (size_t)mp_obj_get_int(size_in);
    }
    if (size == 0) return mp_const_none;
    mp_obj_array_t *view = MP_OBJ_TO_PTR(mp_obj_new_memoryview(BYTEARRAY_TYPECODE,
        size, self->data));
    view->typecode |= 0x80; // used to indicate writable buffer
    return MP_OBJ_FROM_PTR(view);
}

static MP_DEFINE_CONST_FUN_OBJ_VAR_BETWEEN(mp_lv_dereference_obj, 1, 2, mp_lv_dereference);

// Callback function handling
// Callback is either a callable object or a pointer. If it's a callable object, set user_data to the callback.
// Multiple callbacks are kept per object/struct using a dict that associate callback name with callback object
// In case of an lv_obj_t, user_data is mp_lv_obj_t which contains a member "callbacks" for that dict.
// In case of a struct, user_data is a pointer to that dict directly

static mp_obj_t get_callback_dict_from_user_data(void *user_data)
{
    if (user_data){
        mp_obj_t obj = MP_OBJ_FROM_PTR(user_data);
#ifdef LV_OBJ_T
        return
            MP_OBJ_IS_TYPE(obj, &mp_type_dict)? obj: // Handle the case of dict for a struct
            mp_get_callbacks(obj); // Handle the case of mp_lv_obj_t for an lv_obj_t
#else
        return obj;
#endif
    }
    return NULL;
}

typedef void *(*mp_lv_get_user_data)(void *);
typedef void (*mp_lv_set_user_data)(void *, void *);

static void *mp_lv_callback(mp_obj_t mp_callback, void *lv_callback, qstr callback_name,
     void **user_data_ptr, void *containing_struct, mp_lv_get_user_data get_user_data, mp_lv_set_user_data set_user_data)
{
    if (lv_callback && mp_obj_is_callable(mp_callback)) {
        void *user_data = NULL;
        if (user_data_ptr) {
            // user_data is either a dict of callbacks in case of struct, or a pointer to mp_lv_obj_t in case of lv_obj_t
            if (! (*user_data_ptr) ) *user_data_ptr = MP_OBJ_TO_PTR(mp_obj_new_dict(0)); // if it's NULL - it's a dict for a struct
            user_data = *user_data_ptr;
        }
        else if (get_user_data && set_user_data) {
            user_data = get_user_data(containing_struct);
            if (!user_data) {
                user_data = MP_OBJ_TO_PTR(mp_obj_new_dict(0));
                set_user_data(containing_struct, user_data);
            }
        }

        if (user_data) {
            mp_obj_t callbacks = get_callback_dict_from_user_data(user_data);
            mp_obj_dict_store(callbacks, MP_OBJ_NEW_QSTR(callback_name), mp_callback);
        }
        return lv_callback;
    } else {
        return mp_to_ptr(mp_callback);
    }
}

static int _nesting = 0;

// Call a Python callback from LVGL C code without ever unwinding through
// the C frames that invoked it. A raising callback used to nlr-unwind past
// both the `_nesting--` (leaving the counter stuck nonzero, which silently
// disables every consumer gating on `lv._nesting.value == 0` until a hard
// reset, C statics surviving soft reset) and LVGL's own re-entrancy state
// (lv_timer_handler's already-running flag), which wedged timer handling
// even with the counter balanced. So: report the exception here and return
// a benign result (0 lowers safely to void/int/bool/enum/pointer returns);
// LVGL's C state stays consistent and the next callback runs normally.
static mp_obj_t mp_lv_nesting_call(mp_obj_t func, size_t n_args, const mp_obj_t *args)
{
    nlr_buf_t nlr;
    mp_obj_t result;
    _nesting++;
    if (nlr_push(&nlr) == 0) {
        result = mp_call_function_n_kw(func, n_args, 0, args);
        nlr_pop();
    } else {
        mp_obj_print_exception(&mp_plat_print, MP_OBJ_FROM_PTR(nlr.ret_val));
        result = MP_OBJ_NEW_SMALL_INT(0);
    }
    _nesting--;
    return result;
}

// How many Python callbacks LVGL is inside right now. The MicroPython port's
// assert handler reads it: at zero, an exception raised from a failed LVGL
// assert unwinds out of every LVGL frame, so the handler first clears the
// state LVGL holds for the length of a pass; above zero, the callback's own
// nlr frame catches it and LVGL carries on, so that state must stay.
int mp_lv_nesting_depth(void);
int mp_lv_nesting_depth(void)
{
    return _nesting;
}

// Function pointers wrapper

static mp_obj_t mp_lv_funcptr(const mp_lv_obj_fun_builtin_var_t *mp_fun, void *lv_fun, void *lv_callback, qstr func_name, void *user_data)
{
    if (lv_fun == NULL)
        return mp_const_none;
    if (lv_fun == lv_callback) {
        mp_obj_t callbacks = get_callback_dict_from_user_data(user_data);
        if (callbacks)
            return mp_obj_dict_get(callbacks, MP_OBJ_NEW_QSTR(func_name));
    }
    mp_lv_obj_fun_builtin_var_t *funcptr = m_new_obj(mp_lv_obj_fun_builtin_var_t);
    *funcptr = *mp_fun;
    funcptr->lv_fun = lv_fun;
    return MP_OBJ_FROM_PTR(funcptr);
}

// Missing implementation for 64bit integer conversion

static unsigned long long mp_obj_get_ull(mp_obj_t obj)
{
    if (mp_obj_is_small_int(obj))
        return MP_OBJ_SMALL_INT_VALUE(obj);

    unsigned long long val = 0;
    bool big_endian = !(__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__);
    __MP_OBJ_GET_ULL_TO_BYTES__
    return val;
}


// Array of natives

typedef struct mp_lv_array_t
{
    mp_lv_struct_t base;
    size_t element_size;
    bool is_signed;
} mp_lv_array_t;

static void mp_lv_array_print(const mp_print_t *print,
    mp_obj_t self_in,
    mp_print_kind_t kind)
{
    mp_lv_array_t *self = MP_OBJ_TO_PTR(self_in);
    size_t element_size = self->element_size;
    bool is_signed = self->is_signed;
    mp_printf(print, "C Array (%sint%d[])", is_signed? "": "u", element_size*8);
}

static mp_obj_t lv_array_subscr(mp_obj_t self_in, mp_obj_t index, mp_obj_t value)
{
    mp_lv_array_t *self = MP_OBJ_TO_PTR(self_in);

    if ((!self) || (!self->base.data))
        return NULL;
    if (!mp_obj_is_int(index)) {
        nlr_raise(
            mp_obj_new_exception_msg(
                &mp_type_SyntaxError, MP_ERROR_TEXT("Subscript index must be an integer!")));
    }

    size_t element_size = self->element_size;
    size_t element_index = mp_obj_get_int(index);
    void *element_addr = (byte*)self->base.data + element_size*element_index;
    bool is_signed = self->is_signed;
    union {
        long long val;
        unsigned long long uval;
    } element;
    memset(&element, 0, sizeof(element));

    if (value == MP_OBJ_NULL){
        memset(element_addr, 0, element_size);
    }
    else if (value == MP_OBJ_SENTINEL){
        memcpy(&element, element_addr, element_size);
        return is_signed? mp_obj_new_int_from_ll(element.val): mp_obj_new_int_from_ull(element.uval);
    } else {
        if (!mp_obj_is_int(value)) {
            nlr_raise(
                mp_obj_new_exception_msg_varg(
                    &mp_type_SyntaxError, MP_ERROR_TEXT("Value '%s' must be an integer!"), mp_obj_get_type_str(value)));
        }
        element.uval = mp_obj_get_ull(value);
        memcpy(element_addr, &element, element_size);
    }

    return self_in;
}

static const mp_rom_map_elem_t mp_base_struct_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR___cast__), MP_ROM_PTR(&mp_lv_cast_class_method) },
    { MP_ROM_QSTR(MP_QSTR___cast_instance__), MP_ROM_PTR(&mp_lv_cast_instance_obj) },
    { MP_ROM_QSTR(MP_QSTR___dereference__), MP_ROM_PTR(&mp_lv_dereference_obj) },
};

static MP_DEFINE_CONST_DICT(mp_base_struct_locals_dict, mp_base_struct_locals_dict_table);

static MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_base_struct_type,
    MP_QSTR_Struct,
    MP_TYPE_FLAG_NONE,
    binary_op, lv_struct_binary_op,
    subscr, lv_struct_subscr,
    buffer, mp_blob_get_buffer,
    locals_dict, &mp_base_struct_locals_dict
);

// TODO: provide constructor
static MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_array_type,
    MP_QSTR_C_Array,
    MP_TYPE_FLAG_NONE,
    print, mp_lv_array_print,
    binary_op, lv_struct_binary_op,
    subscr, lv_array_subscr,
    buffer, mp_blob_get_buffer,
    locals_dict, &mp_base_struct_locals_dict
);

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

typedef struct {
    mp_obj_base_t base;
    mp_obj_t owner;
    char *data;
    size_t len;
    size_t elem_size;
    mp_obj_t (*read)(void *elem);
    void *(*write)(mp_obj_t value);
} mp_lv_struct_array_t;

static mp_obj_t lv_struct_array_subscr(mp_obj_t self_in, mp_obj_t index, mp_obj_t value)
{
    mp_lv_struct_array_t *self = MP_OBJ_TO_PTR(self_in);
    if (value == MP_OBJ_NULL) {
        mp_raise_TypeError(MP_ERROR_TEXT("can't delete struct array items"));
    }
    size_t i = mp_get_index(self->base.type, self->len, index, false);
    char *elem = self->data + i * self->elem_size;
    if (value == MP_OBJ_SENTINEL) {
        return self->read(elem);
    }
    memcpy(elem, self->write(value), self->elem_size);
    return mp_const_none;
}

static mp_obj_t lv_struct_array_unary_op(mp_unary_op_t op, mp_obj_t self_in)
{
    mp_lv_struct_array_t *self = MP_OBJ_TO_PTR(self_in);
    switch (op) {
        case MP_UNARY_OP_LEN: return MP_OBJ_NEW_SMALL_INT(self->len);
        case MP_UNARY_OP_BOOL: return mp_obj_new_bool(self->len != 0);
        default: return MP_OBJ_NULL;
    }
}

// Iterates views of the elements, the same objects indexing returns.
static mp_obj_t lv_struct_array_getiter(mp_obj_t self_in, mp_obj_iter_buf_t *iter_buf)
{
    mp_lv_struct_array_t *self = MP_OBJ_TO_PTR(self_in);
    mp_obj_t items = mp_obj_new_tuple(self->len, NULL);
    mp_obj_tuple_t *t = MP_OBJ_TO_PTR(items);
    for (size_t i = 0; i < self->len; i++) {
        t->items[i] = self->read(self->data + i * self->elem_size);
    }
    return mp_getiter(items, iter_buf);
}

static MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_struct_array_type,
    MP_QSTR_StructArray,
    MP_TYPE_FLAG_ITER_IS_GETITER,
    unary_op, lv_struct_array_unary_op,
    subscr, lv_struct_array_subscr,
    iter, lv_struct_array_getiter
);

GENMPY_UNUSED static mp_obj_t mp_lv_struct_array_new(mp_obj_t owner, void *data,
    size_t len, size_t elem_size, mp_obj_t (*read)(void *), void *(*write)(mp_obj_t))
{
    mp_lv_struct_array_t *self = m_new_obj(mp_lv_struct_array_t);
    self->base.type = &mp_lv_struct_array_type;
    self->owner = owner;
    self->data = (char *)data;
    self->len = len;
    self->elem_size = elem_size;
    self->read = read;
    self->write = write;
    return MP_OBJ_FROM_PTR(self);
}

GENMPY_UNUSED static void mp_lv_struct_array_assign(void *data, size_t len,
    size_t elem_size, void *(*write)(mp_obj_t), mp_obj_t value)
{
    if (MP_OBJ_IS_STR_OR_BYTES(value) ||
        MP_OBJ_IS_TYPE(value, &mp_type_bytearray) ||
        MP_OBJ_IS_TYPE(value, &mp_type_memoryview)) {
        mp_buffer_info_t bufinfo;
        mp_get_buffer_raise(value, &bufinfo, MP_BUFFER_READ);
        if (bufinfo.len != len * elem_size) {
            mp_raise_msg_varg(&mp_type_ValueError,
                MP_ERROR_TEXT("expected a buffer of %d bytes, got %d"),
                (int)(len * elem_size), (int)bufinfo.len);
        }
        memcpy(data, bufinfo.buf, bufinfo.len);
        return;
    }
    mp_obj_t mp_len = mp_obj_len_maybe(value);
    if (mp_len == MP_OBJ_NULL) {
        mp_raise_msg_varg(&mp_type_TypeError,
            MP_ERROR_TEXT("expected a sequence of %d structs, got '%s'"),
            (int)len, mp_obj_get_type_str(value));
    }
    if ((size_t)mp_obj_get_int(mp_len) != len) {
        mp_raise_msg_varg(&mp_type_ValueError,
            MP_ERROR_TEXT("expected %d items, got %d"),
            (int)len, (int)mp_obj_get_int(mp_len));
    }
    // Convert every item before writing any, so a bad item changes nothing.
    char *tmp = m_new(char, len * elem_size);
    for (size_t i = 0; i < len; i++) {
        mp_obj_t item = mp_obj_subscr(value, MP_OBJ_NEW_SMALL_INT(i), MP_OBJ_SENTINEL);
        memcpy(tmp + i * elem_size, write(item), elem_size);
    }
    memcpy(data, tmp, len * elem_size);
    m_del(char, tmp, len * elem_size);
}

GENMPY_UNUSED static mp_obj_t mp_array_from_ptr(void *lv_arr, size_t element_size, bool is_signed)
{
    mp_lv_array_t *self = m_new_obj(mp_lv_array_t);
    *self = (mp_lv_array_t){
        { {&mp_lv_array_type}, lv_arr },
        element_size,
        is_signed
    };
    return MP_OBJ_FROM_PTR(self);
}

GENMPY_UNUSED static void *mp_array_to_ptr(mp_obj_t *mp_arr, size_t element_size, GENMPY_UNUSED bool is_signed)
{
    if (MP_OBJ_IS_STR_OR_BYTES(mp_arr) ||
        MP_OBJ_IS_TYPE(mp_arr, &mp_type_bytearray) ||
        MP_OBJ_IS_TYPE(mp_arr, &mp_type_memoryview)){
            return mp_to_ptr(mp_arr);
    }

    mp_obj_t mp_len = mp_obj_len_maybe(mp_arr);
    if (mp_len == MP_OBJ_NULL) return mp_to_ptr(mp_arr);
    mp_int_t len = mp_obj_get_int(mp_len);
    void *lv_arr = m_malloc(len * element_size);
    byte *element_addr = (byte*)lv_arr;
    mp_obj_t iter = mp_getiter(mp_arr, NULL);
    mp_obj_t item;
    while ((item = mp_iternext(iter)) != MP_OBJ_STOP_ITERATION) {
        union {
            long long val;
            unsigned long long uval;
        } element;
        if (!mp_obj_is_int(item)) {
            nlr_raise(
                mp_obj_new_exception_msg_varg(
                    &mp_type_SyntaxError, MP_ERROR_TEXT("Value '%s' must be an integer!"), mp_obj_get_type_str(item)));
        }
        element.uval = mp_obj_get_ull(item);
        memcpy(element_addr, &element, element_size);
        element_addr += element_size;
    }
    return lv_arr;
}

#define MP_ARRAY_CONVERTOR(name, size, is_signed) \
GENMPY_UNUSED static mp_obj_t mp_array_from_ ## name(void *lv_arr)\
{\
    return mp_array_from_ptr(lv_arr, size, is_signed);\
}\
GENMPY_UNUSED static void *mp_array_to_ ## name(mp_obj_t mp_arr)\
{\
    return mp_array_to_ptr(mp_arr, size, is_signed);\
}

MP_ARRAY_CONVERTOR(u8ptr, 1, false)
MP_ARRAY_CONVERTOR(i8ptr, 1, true)
MP_ARRAY_CONVERTOR(u16ptr, 2, false)
MP_ARRAY_CONVERTOR(i16ptr, 2, true)
MP_ARRAY_CONVERTOR(u32ptr, 4, false)
MP_ARRAY_CONVERTOR(i32ptr, 4, true)
MP_ARRAY_CONVERTOR(u64ptr, 8, false)
MP_ARRAY_CONVERTOR(i64ptr, 8, true)

"""
        .replace("__MP_OBJ_GET_ULL_TO_BYTES__", _mp_obj_get_ull_to_bytes)
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
                print("MP_DEFINE_STR_OBJ(mp_%s, %s);" % (full_name, full_name))
                enum[member_name] = "&mp_%s" % full_name
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
    struct_aliases = collections.OrderedDict()
    callbacks_used_on_structs = []


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


    def _struct_array_elem_rw(decl):
        """(reader, writer) by pointer for a struct-element array field, else None."""
        elem_ast = decl.type.type
        if not isinstance(elem_ast, c_ast.TypeDecl):
            return None
        ptr_type = "%s *" % get_type(elem_ast, remove_quals=True)
        read = lv_to_mp.get(ptr_type) or ""
        write = mp_to_lv.get(ptr_type) or ""
        if read.startswith("mp_read_ptr_") and write.startswith("mp_write_ptr_"):
            return read, write
        return None

    def try_generate_struct(struct_name, struct):
        if struct_name in generated_structs:
            return None
        sanitized_struct_name = sanitize(struct_name)
        generated_structs[struct_name] = False  # Starting generating a struct
        # print("/* Starting generating %s */" % struct_name)
        if struct_name in mp_to_lv:
            return mp_to_lv[struct_name]
        # print('/* --> try_generate_struct %s: %s\n%s */' % (struct_name, gen.visit(struct), struct))
        if struct.decls is None:
            if struct_name == struct.name:
                return None
            if struct.name not in structs:
                return None
            return try_generate_type(structs[struct.name])
        flatten_struct_decls = flatten_struct(struct.decls)
        # Go over fields and try to generate type convertors for each
        # print('!! %s' % struct)
        # print('!!! %s' % flatten_struct_decls)
        write_cases = []
        read_cases = []
        for decl in flatten_struct_decls:
            # print('/* ==> decl %s: %s */' % (gen.visit(decl), decl))
            converted = try_generate_type(decl.type)
            type_name = get_type(decl.type, remove_quals=True)
            # print('/* --> %s: %s (%s)*/' % (decl.name, type_name, mp_to_lv[type_name] if type_name in mp_to_lv else '---'))
            # Handle the case of nested struct
            if not converted and is_struct(decl.type.type):
                parent_name = struct_name
                child_name = decl.type.declname
                type_name = "%s_%s_t" % (parent_name[:-2], child_name)
                print(
                    "typedef __typeof__( (({parent}*)(0))->{child} ) {new_struct};".format(
                        parent=parent_name, child=child_name, new_struct=type_name
                    )
                )
                try_generate_struct(type_name, decl.type.type)

            # print('==> %s %s: %s' % (type_name, str(type_name in mp_to_lv), decl))

            if (type_name not in mp_to_lv or not mp_to_lv[type_name]) or (
                type_name not in lv_to_mp or not lv_to_mp[type_name]
            ):
                # eprint("[%s] %s or %s : %s" % (isinstance(decl.type,c_ast.PtrDecl), type_name, get_type(decl.type), decl.type))
                if type_name in generated_structs:
                    print(
                        "/* Already started generating %s! skipping field '%s' */"
                        % (type_name, decl.name)
                    )
                    continue
                raise MissingConversionException(
                    "Missing conversion to %s when generating struct %s.%s"
                    % (type_name, struct_name, get_name(decl))
                )

            mp_to_lv_convertor = mp_to_lv[type_name]
            lv_to_mp_convertor = (
                lv_to_mp_byref[type_name]
                if type_name in lv_to_mp_byref
                else lv_to_mp[type_name]
            )

            cast = (
                "(void*)" if isinstance(decl.type, c_ast.PtrDecl) else ""
            )  # needed when field is const. casting to void overrides it

            callback = decl_to_callback(decl)

            if callback:
                if _emit_max_phase is not None and _emit_max_phase < 7:
                    continue
                # print("/* %s callback %s */" % (gen.visit(decl), callback))
                func_name, arg_type = callback
                user_data, _, _ = get_user_data(
                    arg_type,
                    func_name=func_name,
                    containing_struct=struct,
                    containing_struct_name=struct_name,
                )
                if callback not in callbacks_used_on_structs:
                    callbacks_used_on_structs.append(callback + (struct_name,))
                # Emit callback forward decl.
                if user_data in [
                    user_data_decl.name for user_data_decl in flatten_struct_decls
                ]:
                    full_user_data = "data->%s" % user_data
                    full_user_data_ptr = "&%s" % full_user_data
                    lv_callback = "%s_%s_callback" % (struct_name, func_name)
                    print(
                        "static %s %s_%s_callback(%s);"
                        % (
                            get_type(arg_type.type, remove_quals=False),
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
                            "Missing 'user_data' as a field of the first parameter of the callback function '%s_%s_callback'"
                            % (struct_name, func_name),
                        )
                    else:
                        gen_func_error(
                            decl, "Missing 'user_data' member in struct '%s'" % struct_name
                        )
                write_cases.append(
                    "case MP_QSTR_{field}: data->{decl_name} = {cast}mp_lv_callback(dest[1], {lv_callback} ,MP_QSTR_{struct_name}_{field}, {user_data}, NULL, NULL, NULL); break; // converting to callback {type_name}".format(
                        struct_name=struct_name,
                        field=sanitize(decl.name),
                        decl_name=decl.name,
                        lv_callback=lv_callback,
                        user_data=full_user_data_ptr,
                        type_name=type_name,
                        cast=cast,
                    )
                )
                read_cases.append(
                    "case MP_QSTR_{field}: dest[0] = mp_lv_funcptr(&mp_{funcptr}_mpobj, {cast}data->{decl_name}, {lv_callback} ,MP_QSTR_{struct_name}_{field}, {user_data}); break; // converting from callback {type_name}".format(
                        struct_name=struct_name,
                        field=sanitize(decl.name),
                        decl_name=decl.name,
                        lv_callback=lv_callback,
                        funcptr=lv_to_mp_funcptr[type_name],
                        user_data=full_user_data,
                        type_name=type_name,
                        cast=cast,
                    )
                )
            else:
                user_data = None
                # Only allow write to non-const members
                is_writeable = (
                    not hasattr(decl.type, "quals")
                ) or "const" not in decl.type.quals
                # Arrays must be handled by memcpy, otherwise we would get "assignment to expression with array type" error
                elem_rw = (
                    _struct_array_elem_rw(decl)
                    if isinstance(decl.type, c_ast.ArrayDecl)
                    else None
                )
                if elem_rw:
                    # A view, not a list of copies (lvgl-bindings#38).
                    elem_read, elem_write = elem_rw
                    shape = "data->{decl_name}, {dim}, sizeof({elem})".format(
                        decl_name=decl.name,
                        dim=gen.visit(decl.type.dim),
                        elem=gen.visit(decl.type.type),
                    )
                    if is_writeable:
                        write_cases.append(
                            "case MP_QSTR_{field}: mp_lv_struct_array_assign({shape}, {write}, dest[1]); break; // converting to {type_name}".format(
                                field=sanitize(decl.name),
                                shape=shape,
                                write=elem_write,
                                type_name=type_name,
                            )
                        )
                    read_cases.append(
                        "case MP_QSTR_{field}: dest[0] = mp_lv_struct_array_new(self_in, {shape}, {read}, {write}); break; // converting from {type_name}".format(
                            field=sanitize(decl.name),
                            shape=shape,
                            read=elem_read,
                            write=elem_write,
                            type_name=type_name,
                        )
                    )
                elif isinstance(decl.type, c_ast.ArrayDecl):
                    memcpy_size = "sizeof(%s)*%s" % (
                        gen.visit(decl.type.type),
                        gen.visit(decl.type.dim),
                    )
                    if is_writeable:
                        write_cases.append(
                            "case MP_QSTR_{field}: memcpy((void*)&data->{decl_name}, {cast}{convertor}(dest[1]), {size}); break; // converting to {type_name}".format(
                                field=sanitize(decl.name),
                                decl_name=decl.name,
                                convertor=mp_to_lv_convertor,
                                type_name=type_name,
                                cast=cast,
                                size=memcpy_size,
                            )
                        )
                    read_cases.append(
                        "case MP_QSTR_{field}: dest[0] = {convertor}({cast}data->{decl_name}); break; // converting from {type_name}".format(
                            field=sanitize(decl.name),
                            decl_name=decl.name,
                            convertor=lv_to_mp_convertor,
                            type_name=type_name,
                            cast=cast,
                        )
                    )
                else:
                    if is_writeable:
                        write_cases.append(
                            "case MP_QSTR_{field}: data->{decl_name} = {cast}{convertor}(dest[1]); break; // converting to {type_name}".format(
                                field=sanitize(decl.name),
                                decl_name=decl.name,
                                convertor=mp_to_lv_convertor,
                                type_name=type_name,
                                cast=cast,
                            )
                        )
                    read_cases.append(
                        "case MP_QSTR_{field}: dest[0] = {convertor}({cast}data->{decl_name}); break; // converting from {type_name}".format(
                            field=sanitize(decl.name),
                            decl_name=decl.name,
                            convertor=lv_to_mp_convertor,
                            type_name=type_name,
                            cast=cast,
                        )
                    )
        print(
            """
/*
 * Struct {struct_name}
 */

{pointer_helpers}

#define mp_read_{sanitized_struct_name}(field) mp_read_ptr_{sanitized_struct_name}(copy_buffer(&field, sizeof({struct_tag}{struct_name})))
#define mp_read_byref_{sanitized_struct_name}(field) mp_read_ptr_{sanitized_struct_name}(&field)

static void mp_{sanitized_struct_name}_attr(mp_obj_t self_in, qstr attr, mp_obj_t *dest)
{{
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(self_in);
    GENMPY_UNUSED {struct_tag}{struct_name} *data = ({struct_tag}{struct_name}*)self->data;

    if (dest[0] == MP_OBJ_NULL) {{
        // load attribute
        switch(attr)
        {{
            {read_cases};
            default: call_parent_methods(self_in, attr, dest); // fallback to locals_dict lookup
        }}
    }} else {{
        if (dest[1])
        {{
            // store attribute
            switch(attr)
            {{
                {write_cases};
                default: return;
            }}

            dest[0] = MP_OBJ_NULL; // indicate success
        }}
    }}
}}

static void mp_{sanitized_struct_name}_print(const mp_print_t *print,
    mp_obj_t self_in,
    mp_print_kind_t kind)
{{
    mp_printf(print, "struct {struct_name}");
}}

static const mp_obj_dict_t mp_{sanitized_struct_name}_locals_dict;

static MP_DEFINE_CONST_OBJ_TYPE(
    mp_{sanitized_struct_name}_type,
    MP_QSTR_{sanitized_struct_name},
    MP_TYPE_FLAG_NONE,
    print, mp_{sanitized_struct_name}_print,
    make_new, make_new_lv_struct,
    binary_op, lv_struct_binary_op,
    subscr, lv_struct_subscr,
    attr, mp_{sanitized_struct_name}_attr,
    locals_dict, &mp_{sanitized_struct_name}_locals_dict,
    buffer, mp_blob_get_buffer,
    parent, &mp_lv_base_struct_type
);

static inline const mp_obj_type_t *get_mp_{sanitized_struct_name}_type(void)
{{
    return &mp_{sanitized_struct_name}_type;
}}
    """.format(
                sanitized_struct_name=sanitized_struct_name,
                struct_name=struct_name,
                struct_tag="struct "
                if struct_name in structs_without_typedef.keys()
                else "",
                write_cases=";\n                ".join(write_cases),
                read_cases=";\n            ".join(read_cases),
                pointer_helpers=struct_pointer_helpers_source(
                    accept_none=False,
                    unused_qualifier="GENMPY_UNUSED ",
                    sanitized_struct_name=sanitized_struct_name,
                    struct_name=struct_name,
                    struct_tag="struct "
                    if struct_name in structs_without_typedef.keys()
                    else "",
                ),
            )
        )
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
        # print('/* --> struct "%s" generated! */' % (struct_name))
        generated_structs[struct_name] = True  # Completed generating a struct
        return struct_name


    #
    # Generate Array Types when needed
    #


    def try_generate_array_type(type_ast):
        arr_name = get_name(type_ast)
        if arr_name in mp_to_lv:
            return mp_to_lv[arr_name]
        # print('/* --> try_generate_array_type %s: %s */' % (arr_name, type_ast))
        dim = gen.visit(type_ast.dim) if hasattr(type_ast, "dim") and type_ast.dim else None
        element_type = get_type(type_ast.type, remove_quals=True)
        qualified_element_type = gen.visit(type_ast.type)
        if element_type not in mp_to_lv or not mp_to_lv[element_type]:
            try_generate_type(type_ast.type)
            if element_type not in mp_to_lv or not mp_to_lv[element_type]:
                raise MissingConversionException(
                    "Missing conversion to %s while generating array type conversion"
                    % element_type
                )
        type_ptr_ast = c_ast.PtrDecl(quals=[], type=type_ast.type)
        element_type_ptr = get_type(type_ptr_ast, remove_quals=True)
        qualified_element_ptr_type = gen.visit(type_ptr_ast)
        if element_type_ptr not in mp_to_lv or not mp_to_lv[element_type_ptr]:
            try_generate_type(type_ptr_ast)
            if element_type_ptr not in mp_to_lv or not mp_to_lv[element_type_ptr]:
                raise MissingConversionException(
                    "Missing conversion to %s while generating array type conversion"
                    % element_type_ptr
                )
        array_convertor_suffix = (
            arr_name.replace(" ", "_")
            .replace("*", "ptr")
            .replace("+", "plus")
            .replace("-", "minus")
            .replace("[", "__")
            .replace("]", "__")
            .replace("(", "__")
            .replace(")", "__")
            .replace("/", "_div_")
        )
        arr_to_c_convertor_name = "mp_arr_to_%s" % array_convertor_suffix
        arr_to_mp_convertor_name = "mp_arr_from_%s" % array_convertor_suffix
        print(
            (
                (
                    """
/*
 * Array convertors for {arr_name}
 */

GENMPY_UNUSED static {struct_tag}{type} *{arr_to_c_convertor_name}(mp_obj_t mp_arr)
{{
    // A packed buffer is already the C array (lvgl-bindings#37).
    if (MP_OBJ_IS_STR_OR_BYTES(mp_arr) ||
        MP_OBJ_IS_TYPE(mp_arr, &mp_type_bytearray) ||
        MP_OBJ_IS_TYPE(mp_arr, &mp_type_memoryview))
        return mp_to_ptr(mp_arr);
    mp_obj_t mp_len = mp_obj_len_maybe(mp_arr);
    if (mp_len == MP_OBJ_NULL) return mp_to_ptr(mp_arr);
    mp_int_t len = mp_obj_get_int(mp_len);
    {check_dim}
    {struct_tag}{type} *lv_arr = ({struct_tag}{type}*)m_malloc(len * sizeof({struct_tag}{type}));
    mp_obj_t iter = mp_getiter(mp_arr, NULL);
    mp_obj_t item;
    size_t i = 0;
    while ((item = mp_iternext(iter)) != MP_OBJ_STOP_ITERATION) {{
        lv_arr[i++] = {mp_to_lv_convertor}(item);
    }}
    return ({struct_tag}{type} *)lv_arr;
}}
"""
                )
                + (
                    """
GENMPY_UNUSED static mp_obj_t {arr_to_mp_convertor_name}({qualified_type} *arr)
{{
    mp_obj_t obj_arr[{dim}];
    for (size_t i=0; i<{dim}; i++){{
        obj_arr[i] = {lv_to_mp_convertor}(arr[i]);
    }}
    return mp_obj_new_list({dim}, obj_arr); // TODO: return custom iterable object!
}}
"""
                    if dim
                    else """
GENMPY_UNUSED static mp_obj_t {arr_to_mp_convertor_name}({qualified_type} *arr)
{{
    return {lv_to_mp_ptr_convertor}((void*)arr);
}}
"""
                )
            ).format(
                arr_to_c_convertor_name=arr_to_c_convertor_name,
                arr_to_mp_convertor_name=arr_to_mp_convertor_name,
                arr_name=arr_name,
                type=element_type,
                type_ptr=element_type_ptr,
                struct_tag="struct "
                if element_type in structs_without_typedef.keys()
                else "",
                qualified_type=qualified_element_type,
                qualified_ptr_type=qualified_element_ptr_type,
                check_dim="//TODO check dim!" if dim else "",
                mp_to_lv_convertor=mp_to_lv[element_type],
                lv_to_mp_convertor=lv_to_mp[element_type],
                mp_to_lv_ptr_convertor=mp_to_lv[element_type_ptr],
                lv_to_mp_ptr_convertor=lv_to_mp[element_type_ptr],
                dim=dim if dim else 1,
            )
        )
        mp_to_lv[arr_name] = arr_to_c_convertor_name
        mp_to_lv["const %s" % arr_name] = arr_to_c_convertor_name
        lv_to_mp[arr_name] = arr_to_mp_convertor_name
        lv_to_mp["const %s" % arr_name] = arr_to_mp_convertor_name
        lv_mp_type[arr_name] = arr_to_c_convertor_name
        lv_mp_type["const %s" % arr_name] = "const %s" % arr_to_c_convertor_name
        return arr_to_c_convertor_name


    #
    # Generate types from typedefs when needed
    #

    generated_funcptr_helpers = collections.OrderedDict()


    def emit_function_pointer(helper_name, func):
        print("#define %s NULL\n" % helper_name)
        if _emit_max_phase is not None and _emit_max_phase < 4:
            return False
        gen_mp_func(func, None)
        print(
            "GENMPY_UNUSED static inline mp_obj_t mp_lv_{f}(void *func){{ "
            "return mp_lv_funcptr(&mp_{f}_mpobj, func, NULL, MP_QSTR_, NULL); }}\n".format(
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
    # Helper structs
    #


    def create_helper_struct(struct_str):
        print(struct_str)
        struct_str_ast = parser.parse(struct_str).ext[0].type
        struct_name = get_name(struct_str_ast)
        # print('/* --> %s: %s */' % (struct_name, struct_str_ast.type))
        structs[struct_name] = struct_str_ast.type
        try:
            try_generate_struct(struct_name, struct_str_ast.type)
        except MissingConversionException as exp:
            print("/* Helper structs NOT generated:\n    %s\n*/" % (repr(exp)))


    print(
        """
/*
 * Helper Structs
 */
        """
    )

    create_helper_struct(
        """
typedef union {
    void*           ptr_val;
    const char*     str_val;
    int             int_val;
    unsigned int    uint_val;
} C_Pointer;
"""
    )

    #
    #
    # Emit C callback functions
    #

    generated_callbacks = collections.OrderedDict()
    generated_funcs = collections.OrderedDict()

    if _emit_max_phase is None or _emit_max_phase > 1:

        if _emit_target == "circuitpython" and _emit_max_phase is not None and _emit_max_phase >= 2:
            from .emit_circuitpython_glue import emit_phase2_enums

            emit_phase2_enums()

        if _emit_max_phase is None or _emit_max_phase >= 4:

            def build_callback_func_arg(arg, index, func, func_name=None):
                arg_type = get_type(arg.type, remove_quals=True)
                cast = (
                    "(void*)" if isinstance(arg.type, c_ast.PtrDecl) else ""
                )  # needed when field is const. casting to void overrides it
                if not conversion_available(
                    conversions=lv_to_mp,
                    type_name=arg_type,
                    generate_type=lambda: try_generate_type(arg.type),
                ):
                    raise MissingConversionException(
                        "Callback: Missing conversion to %s" % arg_type
                    )
                arg_metadata = {"type": lv_mp_type[arg_type]}
                if arg.name:
                    arg_metadata["name"] = arg.name
                callback_metadata[func_name]["args"].append(arg_metadata)
                return "mp_args[{i}] = {convertor}({cast}arg{i});".format(
                    convertor=lv_to_mp[arg_type], i=index, cast=cast
                )


            def gen_callback_func(func, func_name=None, user_data_argument=False):
                if func_name in generated_callbacks:
                    return
                # print('/* --> callback: %s */' % (gen.visit(func)))
                callback_metadata[func_name] = {"args": []}
                args = func.args.params
                enumerated_args = []
                for i, arg in enumerate(args):
                    arg_name = f"arg{i}"
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
                    # print(f'/* --> {gen.visit(new_arg)} */')
                if not func_name:
                    func_name = get_arg_name(func.type)
                # print('/* --> callback: func_name = %s */' % func_name)
                if is_global_callback(func):
                    full_user_data = "MP_STATE_PORT(mp_lv_user_data)"
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
                        if (
                            len(args) < 1
                            or hasattr(args[0].type.type, "names")
                            and lv_base_obj_pattern.match(args[0].type.type.names[0])
                        ):
                            raise MissingConversionException(
                                "Callback: First argument of callback function must be lv_obj_t"
                            )
                    elif user_data_getter:
                        full_user_data = "%s(arg0)" % user_data_getter.name
                    else:
                        full_user_data = None

                    # if full_user_data: print('/* --> callback: %s user_data found!! %s */' %(gen.visit(func), full_user_data))
                    # else: print('/* --> callback: full_user_data NOT FOUND !! %s */' % (gen.visit(func)))
                    if not full_user_data:
                        raise MissingConversionException(
                            "Callback: user_data NOT FOUND! %s" % (gen.visit(func))
                        )
                return_type = get_type(func.type, remove_quals=False)
                if not callback_return_conversion_available(
                    return_type=return_type,
                    mp_to_lv=mp_to_lv,
                    generate_type=lambda: try_generate_type(func.type),
                ):
                    raise MissingConversionException(
                        "Callback return value: Missing conversion to %s" % return_type
                    )

                callback_metadata[func_name]["return_type"] = lv_mp_type[return_type]
                return_lowering = callback_return_lowering(
                    return_type=return_type,
                    mp_to_lv=mp_to_lv,
                )
                print(
                    """
/*
 * Callback function {func_name}
 * {func_prototype}
 */

GENMPY_UNUSED static {return_type} {func_name}_callback({func_args})
{{
    mp_obj_t mp_args[{num_args}];
    {build_args}
    mp_obj_t callbacks = get_callback_dict_from_user_data({user_data});
    {return_value_assignment}mp_lv_nesting_call(mp_obj_dict_get(callbacks, MP_OBJ_NEW_QSTR(MP_QSTR_{func_name})), {num_args}, mp_args);
    return{return_value};
}}
""".format(
                        func_prototype=gen.visit(func),
                        func_name=sanitize(func_name),
                        return_type=return_type,
                        func_args=", ".join([(gen.visit(arg)) for arg in enumerated_args]),
                        num_args=len(args),
                        build_args="\n    ".join(
                            [
                                build_callback_func_arg(arg, i, func, func_name=func_name)
                                for i, arg in enumerate(args)
                            ]
                        ),
                        user_data=full_user_data,
                        return_value_assignment=return_lowering.result_assignment,
                        return_value=return_lowering.return_value,
                    )
                )
                generated_callbacks[func_name] = True


            #
            # Emit Mpy function definitions
            #

            generated_funcs = collections.OrderedDict()


            def build_mp_func_arg(arg, index, func, obj_name):
                if isinstance(arg, c_ast.EllipsisParam):
                    raise MissingConversionException("Cannot convert ellipsis param")
                fixed_arg = copy.deepcopy(arg)
                convert_array_to_ptr(fixed_arg)
                if not fixed_arg.name:
                    fixed_arg.name = "arg%d" % index
                    add_default_declname(fixed_arg, fixed_arg.name)
                # print('/* --> FIXED ARG: %s */' % repr(fixed_arg))
                callback = decl_to_callback(arg)
                args = func.type.args.params if func.type.args else []
                # print('/* --> ARG: %s */' % arg)
                # print('/* --> FIRST ARG: %s */' % first_arg)
                if callback:
                    # Callback is supported in two modes:
                    # 1) last argument is a void* user_data which is passed to callback
                    # 2) first argument is a struct with user_data field, which is passed to callback

                    callback_name, arg_type = callback
                    # print('/* --> callback %s ARG TYPE: %s */' % (callback_name, arg_type))

                    try:
                        user_data_argument = False
                        full_user_data = None
                        user_data_getter = None
                        user_data_setter = None
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
                            user_data, user_data_getter, user_data_setter = get_user_data(
                                arg_type, callback_name
                            )
                            if is_global_callback(arg_type):
                                full_user_data = "&MP_STATE_PORT(mp_lv_user_data)"
                            else:
                                if user_data:
                                    full_user_data = "&%s->%s" % (first_arg.name, user_data)
                                elif user_data_getter and user_data_setter:
                                    full_user_data = "NULL"  # uses getter/setter instead
                                if index == 0:
                                    raise MissingConversionException(
                                        "Callback argument '%s' cannot be the first argument! We assume the first argument contains the user_data"
                                        % gen.visit(arg)
                                    )
                                if not full_user_data:
                                    raise MissingConversionException(
                                        "Callback function '%s' must receive a struct pointer with user_data member as its first argument!"
                                        % gen.visit(arg)
                                    )
                        # eprint("--> callback_metadata= %s_%s" % (struct_name, callback_name))
                        gen_callback_func(arg_type, "%s" % callback_name, user_data_argument)
                        arg_metadata = {
                            "type": "callback",
                            "function": callback_metadata[callback_name],
                        }
                        if arg.name:
                            arg_metadata["name"] = arg.name
                        func_metadata[func.name]["args"].append(arg_metadata)
                        return "void *{arg_name} = mp_lv_callback(mp_args[{i}], &{callback_name}_callback, MP_QSTR_{callback_name}, {full_user_data}, {containing_struct}, (mp_lv_get_user_data){user_data_getter}, (mp_lv_set_user_data){user_data_setter});".format(
                            i=index,
                            arg_name=fixed_arg.name,
                            callback_name=sanitize(callback_name),
                            full_user_data=full_user_data,
                            containing_struct=first_arg.name
                            if user_data_getter and user_data_setter
                            else "NULL",
                            user_data_getter=user_data_getter.name if user_data_getter else "NULL",
                            user_data_setter=user_data_setter.name if user_data_setter else "NULL",
                        )
                    except MissingConversionException as exp:
                        gen_func_error(arg, exp)
                        callback_name = "NULL"
                        full_user_data = "NULL"
                if not hasattr(arg, "type"):
                    raise MissingConversionException(
                        "Cannot convert function argument %s" % repr(arg)
                    )
                arg_type = get_type(arg.type, remove_quals=True)
                # print('/* --> arg = %s, arg_type = %s */' %(gen.visit(arg), arg_type))
                if not conversion_available(
                    conversions=mp_to_lv,
                    type_name=arg_type,
                    generate_type=lambda: try_generate_type(arg.type),
                ):
                    raise MissingConversionException("Missing conversion to %s" % arg_type)
                arg_metadata = {"type": lv_mp_type[arg_type]}
                if arg.name:
                    arg_metadata["name"] = arg.name
                func_metadata[func.name]["args"].append(arg_metadata)
                cast = (
                    ("(%s)" % gen.visit(fixed_arg.type)) if "const" in arg.quals else ""
                )  # allow conversion from non const to const, sometimes requires cast
                return "{var} = {cast}{convertor}(mp_args[{i}]);".format(
                    var=gen.visit(fixed_arg), cast=cast, convertor=mp_to_lv[arg_type], i=index
                )


            def emit_func_obj(func_obj_name, func_name, param_count, func_ptr, is_static):
                print(
                    """
static {builtin_macro}(mp_{func_obj_name}_mpobj, {param_count}, mp_{func_name}, {func_ptr});
    """.format(
                        func_obj_name=func_obj_name,
                        func_name=func_name,
                        func_ptr=func_ptr,
                        param_count=param_count,
                        builtin_macro="MP_DEFINE_CONST_LV_FUN_OBJ_STATIC_VAR"
                        if is_static
                        else "MP_DEFINE_CONST_LV_FUN_OBJ_VAR",
                    )
                )


            def gen_mp_func(func, obj_name):
                # print('/* gen_mp_func: %s : %s */' % (obj_name, func))
                if func.name in generated_funcs:
                    print(
                        """
/*
 * WARNING: %s was declared more than once!
 */
        """
                        % func.name
                    )
                    return
                # print("/* gen_mp_func %s */" % func.name)
                generated_funcs[func.name] = False  # starting to generate the function
                func_metadata[func.name] = {"type": "function", "args": []}

                args = func.type.args.params if func.type.args else []
                enumerated_args = enumerate(args)

                # Handle the case of a single function argument which is "void"
                if len(args) == 1 and get_type(args[0].type, remove_quals=True) == "void":
                    param_count = 0
                    args = []
                else:
                    param_count = len(args)

                # If func prototype matches an already generated func, reuse it and only emit func obj that points to it.
                prototype_str = gen.visit(function_prototype(func))
                if prototype_str in func_prototypes:
                    original_func = func_prototypes[prototype_str]
                    if function_reuse_allowed(
                        function_name=func.name,
                        original_name=original_func.name,
                        original_generated=generated_funcs[original_func.name] is True,
                        supports_dynamic_function_pointer=runtime.get(
                            "target_lowering_profile"
                        ).supports_dynamic_function_pointer,
                    ):
                        print("/* Reusing %s for %s */" % (original_func.name, func.name))
                        emit_func_obj(
                            func.name,
                            original_func.name,
                            param_count,
                            func.name,
                            is_static_member(func, base_obj_type),
                        )
                        func_metadata[func.name]["return_type"] = func_metadata[original_func.name][
                            "return_type"
                        ]
                        func_metadata[func.name]["args"] = func_metadata[original_func.name]["args"]
                        generated_funcs[func.name] = True  # completed generating the function
                        return
                func_prototypes[prototype_str] = func

                # user_data argument must be handled first, if it exists
                try:
                    i = [(arg.name if hasattr(arg, "name") else None) for arg in args].index(
                        "user_data"
                    )
                    if i > 0:
                        enumerated_args = [
                            (i, arg) for i, arg in enumerated_args
                        ]  # convert enumerate to list
                        enumerated_args[0], enumerated_args[i] = (
                            enumerated_args[i],
                            enumerated_args[0],
                        )
                except ValueError:
                    pass

                return_type = get_type(func.type.type, remove_quals=False)
                qualified_return_type = gen.visit(func.type.type)
                if isinstance(func.type.type, c_ast.PtrDecl) and lv_func_returns_array.match(
                    func.name
                ):
                    try_generate_array_type(func.type.type)
                # print('/* --> return_type = %s, qualified_return_type = %s\n%s */' % (return_type, qualified_return_type, func.type.type))
                if return_type != "void" and not conversion_available(
                    conversions=lv_to_mp,
                    type_name=return_type,
                    generate_type=lambda: try_generate_type(func.type.type),
                ):
                    raise MissingConversionException(
                        "Missing conversion from %s" % return_type
                    )
                return_lowering = function_return_lowering(
                    return_type=return_type,
                    qualified_return_type=qualified_return_type,
                    is_pointer=isinstance(func.type.type, c_ast.PtrDecl),
                    lv_to_mp=lv_to_mp,
                    lv_mp_type=lv_mp_type,
                )
                build_result = return_lowering.build_result
                build_return_value = return_lowering.build_return_value
                func_metadata[func.name]["return_type"] = (
                    return_lowering.metadata_return_type
                )
                if func.name == "lv_draw_buf_destroy" and _emit_target == "circuitpython":
                    print(
                        """
/*
 * {module_name} extension definition for:
 * {print_func}
 */

static mp_obj_t mp_{func}(size_t mp_n_args, const mp_obj_t *mp_args, void *lv_func_ptr)
{{
    mp_lv_struct_t *self = MP_OBJ_TO_PTR(mp_args[0]);
    lv_draw_buf_t *buf = (lv_draw_buf_t *)self->data;
    if (buf != NULL) {{
        ((void (*)(lv_draw_buf_t *))lv_func_ptr)(buf);
        self->data = NULL;
    }}
    return mp_const_none;
}}

 """
                        .format(
                            module_name=module_name,
                            func=func.name,
                            print_func=gen.visit(func),
                        )
                    )
                else:
                    print(
                    """
/*
 * {module_name} extension definition for:
 * {print_func}
 */

static mp_obj_t mp_{func}(size_t mp_n_args, const mp_obj_t *mp_args, void *lv_func_ptr)
{{
    {build_args}
    {build_result}(({func_ptr})lv_func_ptr)({send_args});
    return {build_return_value};
}}

 """.format(
                        module_name=module_name,
                        func=func.name,
                        func_ptr=prototype_str,
                        print_func=gen.visit(func),
                        build_args="\n    ".join(
                            [
                                build_mp_func_arg(arg, i, func, obj_name)
                                for i, arg in enumerated_args
                                if isinstance(arg, c_ast.EllipsisParam)
                                or (not isinstance(arg.type, c_ast.TypeDecl))
                                or (not isinstance(arg.type.type, c_ast.IdentifierType))
                                or "void" not in arg.type.type.names
                            ]
                        ),  # Handle the case of 'void' param which should be ignored
                        send_args=", ".join(
                            [
                                (arg.name if (hasattr(arg, "name") and arg.name) else ("arg%d" % i))
                                for i, arg in enumerate(args)
                            ]
                        ),
                        build_result=build_result,
                        build_return_value=build_return_value,
                    )
                )

                emit_func_obj(
                    func.name,
                    func.name,
                    param_count,
                    func.name,
                    is_static_member(func, base_obj_type),
                )
                generated_funcs[func.name] = True  # completed generating the function
                # print('/* is_struct_function() = %s, is_static_member() = %s, get_first_arg_type()=%s, obj_name = %s */' % (
                #    is_struct_function(func), is_static_member(func, base_obj_type), get_first_arg_type(func), base_obj_type))


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


        def gen_obj_methods(obj_name):
            helper_members = (
                ["{ MP_ROM_QSTR(MP_QSTR___cast__), MP_ROM_PTR(&cast_obj_class_method) }"]
                if len(obj_names) > 0 and obj_name == base_obj_name
                else []
            )
            members = [
                "{{ MP_ROM_QSTR(MP_QSTR_{method_name}), MP_ROM_PTR(&mp_{method}_mpobj) }}".format(
                    method=method.name,
                    method_name=sanitize(method_name_from_func_name(method.name)),
                )
                for method in get_methods(obj_name)
            ]
            obj_metadata[obj_name]["members"].update(
                {
                    method_name_from_func_name(method.name): func_metadata[method.name]
                    for method in get_methods(obj_name)
                }
            )
            # add parent methods
            parent_members = []
            if obj_name in parent_obj_names and parent_obj_names[obj_name] != None:
                # parent_members += gen_obj_methods(parent_obj_names[obj_name])
                obj_metadata[obj_name]["members"].update(
                    obj_metadata[parent_obj_names[obj_name]]["members"]
                )
            # add enum members
            enum_members = [
                "{{ MP_ROM_QSTR(MP_QSTR_{enum_member}), MP_ROM_PTR({enum_member_value}) }}".format(
                    enum_member=export_name(enum_member_name, "enum_member"),
                    enum_member_value=get_enum_value(obj_name, enum_member_name),
                )
                for enum_member_name in get_enum_members(obj_name)
            ]
            obj_metadata[obj_name]["members"].update(
                {
                    get_enum_member_name(enum_member_name): {"type": "enum_member"}
                    for enum_member_name in get_enum_members(obj_name)
                }
            )
            # add enums that match object name
            obj_enums = [
                enum_name for enum_name in enums.keys() if is_method_of(enum_name, obj_name)
            ]
            enum_types = [
                "{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_lv_{enum}_type_base) }}".format(
                    name=export_name(method_name_from_func_name(enum_name), "enum"),
                    enum=enum_name
                )
                for enum_name in obj_enums
            ]
            obj_metadata[obj_name]["members"].update(
                {
                    method_name_from_func_name(enum_name): {"type": "enum_type"}
                    for enum_name in obj_enums
                }
            )
            for enum_name in obj_enums:
                obj_metadata[obj_name]["members"][method_name_from_func_name(enum_name)].update(
                    obj_metadata[enum_name]
                )
                if is_widget_scoped_only_enum(enum_name):
                    enum_referenced[enum_name] = True
            return members + parent_members + enum_members + enum_types + helper_members


        def gen_obj(obj_name):
            # eprint('Generating object %s...' % obj_name)
            is_obj = has_ctor(obj_name)
            should_add_base_methods = is_obj and obj_name != "obj"
            obj_metadata[obj_name] = {"members": collections.OrderedDict()}

            # Generate object methods
            for method in get_methods(obj_name):
                try:
                    gen_mp_func(method, obj_name)
                except MissingConversionException as exp:
                    gen_func_error(method, exp)

            # Generate object construction function, if needed
            if is_obj:
                ctor_func = get_ctor(obj_name)
                try:
                    gen_mp_func(ctor_func, obj_name)
                except MissingConversionException as exp:
                    gen_func_error(ctor_func, exp)

            # print([method.name for method in methods])
            ctor = """
static mp_obj_t {obj}_make_new(
    const mp_obj_type_t *type,
    size_t n_args,
    size_t n_kw,
    const mp_obj_t *args)
{{
    return make_new(&mp_{ctor_name}_mpobj, type, n_args, n_kw, args);
}}
"""

            print(
                """
/*
 * {module_name} {obj} object definitions
 */
    """.format(module_name=module_name, obj=obj_name)
            )

            print(
                """
static const mp_rom_map_elem_t {obj}_locals_dict_table[] = {{
    {locals_dict_entries}
}};

static MP_DEFINE_CONST_DICT({obj}_locals_dict, {obj}_locals_dict_table);

static void {obj}_print(const mp_print_t *print,
    mp_obj_t self_in,
    mp_print_kind_t kind)
{{
    mp_printf(print, "{module_name} {obj}");
}}

{ctor}

static MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_{obj}_type_base,
    MP_QSTR_{obj},
    MP_TYPE_FLAG_NONE,
    print, {obj}_print,
    {make_new}
    {binary_op}
    attr, call_parent_methods,
    {buffer}
    {parent}
    locals_dict, &{obj}_locals_dict
);

GENMPY_UNUSED static const mp_lv_obj_type_t mp_lv_{obj}_type = {{
#ifdef LV_OBJ_T
    .lv_obj_class = {lv_class},
#endif
    .mp_obj_type = &mp_lv_{obj}_type_base,
}};
    """.format(
                    module_name=module_name,
                    obj=sanitize(obj_name),
                    locals_dict_entries=",\n    ".join(gen_obj_methods(obj_name)),
                    ctor=ctor.format(obj=obj_name, ctor_name=ctor_func.name)
                    if has_ctor(obj_name)
                    else "",
                    make_new="make_new, %s_make_new," % obj_name if is_obj else "",
                    binary_op="binary_op, mp_lv_obj_binary_op," if is_obj else "",
                    buffer="buffer, mp_lv_obj_get_buffer," if is_obj else "",
                    parent="parent, &mp_lv_%s_type_base," % parent_obj_names[obj_name]
                    if obj_name in parent_obj_names and parent_obj_names[obj_name]
                    else "",
                    lv_class="&lv_%s_class" % obj_name if is_obj else "NULL",
                )
            )


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

            generated_obj_names = collections.OrderedDict()
            for obj_name in object_generation_order(obj_names, parent_obj_names):
                gen_obj(obj_name)
                generated_obj_names[obj_name] = True

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


    def _emit_all_struct_types():
        print(
            """
/*
 * CircuitPython phase-3 struct type generation
 */
"""
        )
        for struct_name in list(structs.keys()):
            if generated_structs.get(struct_name):
                continue
            try:
                try_generate_struct(struct_name, structs[struct_name])
            except MissingConversionException as exp:
                print(
                    """
/*
 * Struct NOT generated: {name}
 * {problem}
 */
""".format(
                        name=struct_name,
                        problem=exp,
                    )
                )


    struct_locals_basic = collections.OrderedDict()


    def _emit_struct_locals_dicts(include_methods=False, struct_list=None):
        if struct_list is None:
            struct_names = list(generated_structs.keys())
        else:
            struct_names = struct_list
        for struct_name in struct_names:
            if not generated_structs.get(struct_name):
                continue
            if include_methods:
                if generated_struct_functions.get(struct_name):
                    continue
            else:
                if struct_locals_basic.get(struct_name):
                    continue
            sanitized_struct_name = sanitize(struct_name)
            struct_funcs = (
                list(get_struct_functions(struct_name)) if include_methods else []
            )
            if include_methods:
                for struct_func in struct_funcs[:]:
                    try:
                        if struct_func.name not in generated_funcs:
                            gen_mp_func(struct_func, struct_name)
                    except MissingConversionException as exp:
                        gen_func_error(struct_func, exp)
                        struct_funcs.remove(struct_func)
            if struct_name not in structs or structs[struct_name].decls:
                struct_size_attr = "{{ MP_ROM_QSTR(MP_QSTR___SIZE__), MP_ROM_PTR(MP_ROM_INT(sizeof({struct_tag}{struct_name}))) }},".format(
                    struct_name=struct_name,
                    struct_tag="struct "
                    if struct_name in structs_without_typedef.keys()
                    else "",
                )
            else:
                struct_size_attr = ""
            print(
                """
static const mp_rom_map_elem_t mp_{sanitized_struct_name}_locals_dict_table[] = {{
    {struct_size}
    {functions}
}};

static MP_DEFINE_CONST_DICT(mp_{sanitized_struct_name}_locals_dict, mp_{sanitized_struct_name}_locals_dict_table);
        """.format(
                    struct_size=struct_size_attr,
                    sanitized_struct_name=sanitized_struct_name,
                    functions="".join(
                        [
                            "{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{func}_mpobj) }},\n    ".format(
                                name=sanitize(noncommon_part(f.name, struct_name)),
                                func=f.name,
                            )
                            for f in struct_funcs
                        ]
                    ),
                )
            )
            if include_methods:
                generated_struct_functions[struct_name] = True
            else:
                struct_locals_basic[struct_name] = True


    def gen_global(global_name, global_type_ast):
        global_type = get_type(global_type_ast, remove_quals=True)
        generated_global = try_generate_type(global_type_ast)
        # print("/* generated_global = %s */" % generated_global)
        if global_type not in generated_structs:
            wrapped_type = lv_mp_type[global_type]
            if not wrapped_type:
                raise MissingConversionException(
                    "Missing conversion to %s when generating global %s"
                    % (wrapped_type, global_name)
                )
            global_type = sanitize("_lv_mp_%s_wrapper" % wrapped_type)
            custom_struct_str = """
typedef struct {{
    {type} value;
}} {name};
        """.format(type=wrapped_type, name=global_type)
            if global_type not in generated_structs:
                print("/* Global struct wrapper for %s */" % wrapped_type)
                print(custom_struct_str)
                # eprint("%s: %s\n" % (wrapped_type, custom_struct_str))
                try_generate_struct(
                    global_type, parser.parse(custom_struct_str).ext[0].type.type
                )

        print(
            """
/*
 * {module_name} {global_name} global definitions
 */

{definition}
    """.format(
                module_name=module_name,
                global_name=global_name,
                definition=guarded(
                    """static const mp_lv_struct_t mp_{global_name} = {{
    {{ &mp_{struct_name}_type }},
    ({cast}*)&{global_name}
}};""".format(
                        global_name=global_name,
                        struct_name=global_type,
                        cast=gen.visit(global_type_ast),
                    ),
                    global_name,
                ),
            )
        )


    generated_globals = []
    for global_name in blobs:
        try:
            gen_global(global_name, blobs[global_name])
            generated_globals.append(global_name)
        except MissingConversionException as exp:
            gen_func_error(global_name, exp)

    if _emit_max_phase is None or _emit_max_phase >= 4:
        #
        # Generate struct-functions
        #

        # eprint("/* Generating struct-functions */")
        try_generate_structs_from_first_argument()
        _emit_struct_locals_dicts(include_methods=True)

    elif _emit_target == "circuitpython" and _emit_max_phase == 3:
        _emit_all_struct_types()
        _emit_struct_locals_dicts(include_methods=False)

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
        module_funcs = [func for func in funcs if func.name not in generated_funcs]
        module_funcs = filter_module_funcs_for_target(
            module_funcs, _emit_target, runtime.get("api_model")
        )
        module_funcs = filter_registration_module_funcs(module_funcs)
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

    #
    # Emit Mpy Module definition
    #

    emit_target = _emit_target
    if emit_target == "circuitpython":
        from .emit_circuitpython_glue import emit_phase2_enums, finish_cp_fragment

        if _emit_max_phase is not None and _emit_max_phase >= 2:
            emit_phase2_enums()
        if _emit_max_phase is not None and _emit_max_phase < 6:
            module_funcs = []
        runtime.set_("module_funcs", module_funcs)
        runtime.set_("generated_globals", generated_globals)
        runtime.set_("int_constants", int_constants)
        runtime.set_("generated_structs", generated_structs)
        runtime.set_("struct_aliases", struct_aliases)
        runtime.set_("enums", runtime.get("enums"))
        runtime.set_("enum_referenced", enum_referenced)
        if len(obj_names) > 0 and (_emit_max_phase is None or _emit_max_phase >= 5):
            print(
                """
static const mp_lv_obj_type_t *mp_lv_obj_types[] = {{
    {obj_types},
    NULL
}};
""".format(
                    obj_types=",\n    ".join(
                        ["&mp_lv_%s_type" % sanitize(o) for o in obj_names]
                    )
                )
            )
        finish_cp_fragment(_emit_max_phase or 7)
        EmitterResult.capture(locals()).apply(ctx)
        return

    # eprint("/* Generating module definition */")
    public_struct_names = public_struct_c_names(
        runtime.get("api_model"), _emit_target
    )
    public_enum_names = public_enum_module_names(
        runtime.get("api_model"), _emit_target
    )
    print(
        """

/*
 * {module_name} module definitions
 */

static const mp_rom_map_elem_t {module_name}_globals_table[] = {{
    {{ MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_{module_name}) }},
    {{ MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&lvgl_mod_init_obj) }},
    {{ MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&lvgl_mod_deinit_obj) }},
    {objects}
    {functions}
    {enums}
    {structs}
    {struct_aliases}
    {blobs}
    {int_constants}
#ifdef LV_OBJ_T
    {{ MP_ROM_QSTR(MP_QSTR_LvReferenceError), MP_ROM_PTR(&mp_type_LvReferenceError) }},
#endif // LV_OBJ_T
}};
""".format(
            module_name=sanitize(module_name),
            objects="".join(
                [
                    "{{ MP_ROM_QSTR(MP_QSTR_{export_name}), MP_ROM_PTR(&mp_lv_{obj}_type_base) }},\n    ".format(
                        export_name=export_name(o, "object"),
                        obj=sanitize(o),
                    )
                    for o in obj_names
                ]
            ),
            functions="".join(
                [
                    "{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{func}_mpobj) }},\n    ".format(
                        name=export_name(f.name, "function"), func=f.name
                    )
                    for f in module_funcs
                ]
            ),
            enums="".join(
                [
                    "{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_lv_{enum}_type_base) }},\n    ".format(
                        name=export_name(enum_name, "enum"), enum=enum_name
                    )
                    for enum_name in enums.keys()
                    if enum_name not in enum_referenced
                    and (
                        public_enum_names is None
                        or export_name(enum_name, "enum") in public_enum_names
                    )
                ]
            ),
            structs="".join(
                [
                    "{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{struct_name}_type) }},\n    ".format(
                        name=export_name(struct_name, "struct"),
                        struct_name=sanitize(struct_name),
                    )
                    for struct_name in generated_structs
                    if generated_structs[struct_name]
                    and (
                        public_struct_names is None
                        or struct_name in public_struct_names
                    )
                ]
            ),
            struct_aliases="".join(
                [
                    "{{ MP_ROM_QSTR(MP_QSTR_{alias_name}), MP_ROM_PTR(&mp_{struct_name}_type) }},\n    ".format(
                        struct_name=sanitize(struct_name),
                        alias_name=export_name(
                            struct_aliases[struct_name], "struct"
                        ),
                    )
                    for struct_name in struct_aliases.keys()
                    if public_struct_names is None
                    or struct_aliases[struct_name] in public_struct_names
                ]
            ),
            blobs="".join(
                [
                    guarded(
                        "{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{global_name}) }},".format(
                            name=export_name(global_name, "blob"),
                            global_name=global_name,
                        ),
                        global_name,
                        indent="    ",
                    )
                    + "\n    "
                    # _nesting is deliberately kept here even though the
                    # canonical API model marks it private: see the
                    # comment in emit_backend.module_registration_plan and
                    # api_model.build_api_model.
                    for global_name in generated_globals
                ]
            ),
            int_constants="".join(
                [
                    "{{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(MP_ROM_INT({value})) }},\n    ".format(
                        name=export_name(int_constant, "constant"),
                        value=int_constant,
                    )
                    for int_constant in int_constants
                ]
            ),
        )
    )


    print(
        """
static MP_DEFINE_CONST_DICT (
    mp_module_{module_name}_globals,
    {module_name}_globals_table
);

const mp_obj_module_t mp_module_{module_name} = {{
    .base = {{ &mp_type_module }},
    .globals = (mp_obj_dict_t*)&mp_module_{module_name}_globals
}};

MP_REGISTER_MODULE(MP_QSTR_{module_name}, mp_module_{module_name});

""".format(
            module_name=module_name,
        )
    )

    # Add an array of all object types

    if len(obj_names) > 0:
        print(
            """
static const mp_lv_obj_type_t *mp_lv_obj_types[] = {{
    {obj_types},
    NULL
}};
    """.format(
                obj_types=",\n    ".join(
                    ["&mp_lv_%s_type" % obj_name for obj_name in obj_names]
                )
            )
        )

    EmitterResult.capture(locals()).apply(ctx)
