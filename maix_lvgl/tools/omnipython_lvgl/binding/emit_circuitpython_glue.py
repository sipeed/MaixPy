# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""CircuitPython bookends: phase-2 enums and LVCP_MODULE_GLOBALS module table."""
from __future__ import print_function

import collections

from . import runtime
from .util import guarded
from .emit_backend import enum_namespace_plan, module_registration_plan, public_enum_module_names, public_struct_c_names


# This module owns no mirrored emitter globals; generated output is routed
# through the active run context explicitly.
print = runtime.emit
from .analyze import get_enum_members, get_enum_member_name, get_enum_value
from .helpers import (
    export_name,
    get_enum_name,
    is_method_of,
    is_widget_scoped_only_enum,
    method_name_from_func_name,
    sanitize,
    simplify_identifier,
)


def _module_global_entries(
    max_phase,
    int_constants,
    generated_globals,
    enums,
    enum_referenced,
    generated_structs=None,
    struct_aliases=None,
    obj_names=None,
    module_funcs=None,
):
    canonical_enum_names = public_enum_module_names(
        runtime.get("api_model"), "circuitpython"
    )
    plan = module_registration_plan(
        max_phase=max_phase,
        int_constants=int_constants,
        generated_globals=generated_globals,
        enums=enums,
        enum_referenced=enum_referenced,
        generated_structs=generated_structs or {},
        struct_aliases=struct_aliases or {},
        obj_names=obj_names or (),
        module_funcs=module_funcs or (),
        public_struct_names=public_struct_c_names(
            runtime.get("api_model"), "circuitpython"
        ),
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
    entries = []
    if plan.int_constants or plan.generated_globals:
        for int_constant in plan.int_constants:
            entries.append(
                "    {{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(MP_ROM_INT({value})) }}".format(
                    name=export_name(int_constant, "constant"),
                    value=int_constant,
                )
            )
        for global_name in plan.generated_globals:
            entries.append(
                guarded(
                    "    {{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{global_name}) }},".format(
                        name=export_name(global_name, "blob"),
                        global_name=global_name,
                    ),
                    global_name,
                )
            )
    if plan.enum_names:
        for enum_name in plan.enum_names:
            entries.append(
                "    {{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_lv_{enum}_type_base) }}".format(
                    name=export_name(enum_name, "enum"),
                    enum=enum_name,
                )
            )
    if plan.struct_names:
        for struct_name in plan.struct_names:
            entries.append(
                "    {{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{struct_name}_type) }}".format(
                    name=export_name(struct_name, "struct"),
                    struct_name=sanitize(struct_name),
                )
            )
    if plan.struct_alias_names:
        for struct_name in plan.struct_alias_names:
            entries.append(
                "    {{ MP_ROM_QSTR(MP_QSTR_{alias_name}), MP_ROM_PTR(&mp_{struct_name}_type) }}".format(
                    struct_name=sanitize(struct_name),
                    alias_name=export_name(struct_aliases[struct_name], "struct"),
                )
            )
    if plan.object_names:
        entries.append(
            "    { MP_ROM_QSTR(MP_QSTR_LvReferenceError), MP_ROM_PTR(&mp_type_LvReferenceError) }"
        )
        for obj_name in plan.object_names:
            entries.append(
                "    {{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_lv_{obj}_type_base) }}".format(
                    name=export_name(obj_name, "object"),
                    obj=sanitize(obj_name),
                )
            )
    if plan.module_functions:
        for func in plan.module_functions:
            entries.append(
                "    {{ MP_ROM_QSTR(MP_QSTR_{name}), MP_ROM_PTR(&mp_{func}_mpobj) }}".format(
                    name=export_name(func.name, "function"),
                    func=func.name,
                )
            )
    return entries


def _table(entries):
    """Join table entries; an entry that already ends in its comma keeps it.

    Entries wrapped in ``#if``/``#endif`` carry their comma inside the guard.
    """
    return "\n".join(
        entry if entry.endswith(",") or entry.endswith("#endif") else entry + ","
        for entry in entries
    )


def finish_cp_fragment(max_phase):
    """Emit mergeable module entry table for shared-bindings/lvgl/__init__.c."""
    int_constants = runtime.get("int_constants", [])
    generated_globals = runtime.get("generated_globals", [])
    enums = runtime.get("enums", {})
    enum_referenced = runtime.get("enum_referenced", collections.OrderedDict())
    generated_structs = runtime.get("generated_structs", {})
    struct_aliases = runtime.get("struct_aliases", collections.OrderedDict())
    obj_names = runtime.get("obj_names", [])
    module_funcs = runtime.get("module_funcs", [])

    entries = _module_global_entries(
        max_phase,
        int_constants,
        generated_globals,
        enums,
        enum_referenced,
        generated_structs=generated_structs,
        struct_aliases=struct_aliases,
        obj_names=obj_names,
        module_funcs=module_funcs,
    )

    spike_entries = [
        "    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lvgl) }",
        "    { MP_ROM_QSTR(MP_QSTR___version__), MP_ROM_QSTR(MP_QSTR_9) }",
        "    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&lvgl_init_obj) }",
        "    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&lvgl_deinit_obj) }",
    ]
    all_entries = spike_entries + entries

    print(
        """
/*
 * CircuitPython module dict (generated; spike registers via MP_REGISTER_MODULE).
 * Hand-written init/deinit callables live in shared-bindings/lvgl/__init.c.
 */

#ifndef LVCP_MODULE_GLOBALS_H
#define LVCP_MODULE_GLOBALS_H

#include "py/obj.h"

extern const mp_obj_module_t lvgl_module;

#endif /* LVCP_MODULE_GLOBALS_H */

extern const mp_obj_fun_builtin_fixed_t lvgl_init_obj;
extern const mp_obj_fun_builtin_fixed_t lvgl_deinit_obj;

static const mp_rom_map_elem_t lvgl_module_globals_table[] = {{
{table}
}};

static MP_DEFINE_CONST_DICT(lvgl_module_globals, lvgl_module_globals_table);

const mp_obj_module_t lvgl_module = {{
    .base = {{ &mp_type_module }},
    .globals = (mp_obj_dict_t *)&lvgl_module_globals,
}};

const mp_rom_map_elem_t lvgl_module_entries[] = {{
{table}
}};

const size_t lvgl_module_entry_count = sizeof(lvgl_module_entries) / sizeof(lvgl_module_entries[0]);
""".format(
            table=_table(all_entries) if all_entries else "    /* no module entries */"
        )
    )

    runtime.set_("generated_globals", generated_globals)
    runtime.set_("int_constants", int_constants)
    runtime.set_("enum_referenced", enum_referenced)


def finish_phase1_fragment():
    """Emit phase-1 module entry table (alias for finish_cp_fragment(1))."""
    finish_cp_fragment(1)


def emit_phase2_enums():
    """Emit enum type objects (same C shape as emit_c_micropython_style.gen_obj for enum keys)."""
    if runtime.get("_cp_enums_emitted", False):
        return
    runtime.set_("_cp_enums_emitted", True)
    enums = runtime.get("enums", {})
    obj_metadata = runtime.get("obj_metadata")
    enum_referenced = collections.OrderedDict()
    module_name = runtime.get("module_name", "lvgl")

    print(
        """
/*
 * CircuitPython phase-2 enum type objects
 */
"""
    )

    for enum_plan in enum_namespace_plan(
        enums=enums,
        get_enum_members=get_enum_members,
        is_method_of=is_method_of,
        is_widget_scoped=is_widget_scoped_only_enum,
    ):
        obj_name = enum_plan.name
        obj_metadata[obj_name] = {"members": collections.OrderedDict()}

        enum_members = [
            "{{ MP_ROM_QSTR(MP_QSTR_{enum_member}), MP_ROM_PTR({enum_member_value}) }}".format(
                enum_member=export_name(enum_member_name, "enum_member"),
                enum_member_value=get_enum_value(obj_name, enum_member_name),
            )
            for enum_member_name in enum_plan.members
        ]
        obj_metadata[obj_name]["members"].update(
            {
                get_enum_member_name(enum_member_name): {"type": "enum_member"}
                for enum_member_name in enum_plan.members
            }
        )

        obj_enums = enum_plan.nested_names
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
            if enum_name in obj_metadata:
                obj_metadata[obj_name]["members"][
                    method_name_from_func_name(enum_name)
                ].update(obj_metadata[enum_name])
            if enum_name in enum_plan.widget_scoped_nested_names:
                enum_referenced[enum_name] = True

        locals_dict_entries = ",\n    ".join(enum_members + enum_types)

        print(
            """
/*
 * {module_name} {obj} object definitions
 */

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

static MP_DEFINE_CONST_OBJ_TYPE(
    mp_lv_{obj}_type_base,
    MP_QSTR_{obj},
    MP_TYPE_FLAG_NONE,
    print, {obj}_print,
    attr, call_parent_methods,
    locals_dict, &{obj}_locals_dict
);

GENMPY_UNUSED static const mp_lv_obj_type_t mp_lv_{obj}_type = {{
#ifdef LV_OBJ_T
    .lv_obj_class = NULL,
#endif
    .mp_obj_type = &mp_lv_{obj}_type_base,
}};
""".format(
                module_name=module_name,
                obj=sanitize(obj_name),
                locals_dict_entries=locals_dict_entries,
            )
        )

    runtime.set_("obj_metadata", obj_metadata)
    runtime.set_("enum_referenced", enum_referenced)
