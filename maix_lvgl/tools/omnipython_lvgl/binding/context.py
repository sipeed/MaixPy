# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Per-generation BindingContext; synced into runtime for analyze/emit."""
from __future__ import print_function

import collections
import re
from dataclasses import dataclass, fields
from typing import Any, Mapping


@dataclass(frozen=True)
class EmitterResult:
    """Explicit per-run state returned by a native C emitter."""

    headers: Any
    enums: Any
    generated_structs: Any
    generated_struct_functions: Any
    struct_aliases: Any
    callbacks_used_on_structs: Any
    generated_callbacks: Any
    generated_funcs: Any
    enum_referenced: Any
    generated_obj_names: Any
    generated_globals: Any
    module_funcs: Any
    functions_not_generated: Any

    @classmethod
    def capture(cls, namespace: Mapping[str, Any]) -> "EmitterResult":
        """Capture the declared emitter outputs from one function scope."""
        return cls(**{field.name: namespace[field.name] for field in fields(cls)})

    def apply(self, ctx: "BindingContext") -> None:
        """Publish one completed result without touching module globals."""
        for field in fields(self):
            setattr(ctx, field.name, getattr(self, field.name))


class BindingContext:
    """Holds all inputs and intermediate state for one generation run."""

    EXPORT_NAMES = (
        "module_name",
        "module_prefix",
        "base_obj_name",
        "base_obj_type",
        "lv_ext_pattern",
        "lv_obj_pattern",
        "lv_func_pattern",
        "create_obj_pattern",
        "lv_method_pattern",
        "lv_base_obj_pattern",
        "lv_str_enum_pattern",
        "lv_callback_type_pattern",
        "lv_global_callback_pattern",
        "lv_func_returns_array",
        "lv_enum_name_pattern",
        "obj_metadata",
        "func_metadata",
        "callback_metadata",
        "func_prototypes",
        "parser",
        "gen",
        "parsed_ast",
        "ast",
        "declaration_ir",
        "declaration_index",
        "api_model",
        "lvgl_json",
        "forward_struct_decls",
        "typedefs",
        "synonym",
        "struct_typedefs",
        "structs_without_typedef",
        "structs",
        "explicit_structs",
        "opaque_structs",
        "func_defs",
        "func_decls",
        "all_funcs",
        "funcs",
        "obj_ctors",
        "obj_names",
        "parent_obj_names",
        "enum_defs",
        "func_typedefs",
        "blobs",
        "int_constants",
        "mp_to_lv",
        "lv_to_mp",
        "lv_mp_type",
        "lv_to_mp_byref",
        "lv_to_mp_funcptr",
        "headers",
        "enums",
        "generated_structs",
        "generated_struct_functions",
        "struct_aliases",
        "callbacks_used_on_structs",
        "generated_callbacks",
        "generated_funcs",
        "enum_referenced",
        "generated_obj_names",
        "generated_globals",
        "module_funcs",
        "functions_not_generated",
        "args",
        "pp_cmd",
        "cmd_line",
        "s",
    )

    def __init__(self, args, source, pp_cmd, cmd_line, emit_print):
        self.args = args
        self.s = source
        self.pp_cmd = pp_cmd
        self.cmd_line = cmd_line
        self.emit_print = emit_print
        self.module_name = args.module_name
        self.module_prefix = (
            args.module_prefix if args.module_prefix else args.module_name
        )
        self.base_obj_name = "obj"
        self.base_obj_type = None
        self.parsed_ast = None
        self.declaration_ir = None
        self.declaration_index = None
        self.headers = list(args.input)

    def init_patterns(self):
        p = self.module_prefix
        b = self.base_obj_name
        self.base_obj_type = "%s_%s_t" % (p, b)
        self.lv_ext_pattern = re.compile("^{prefix}_([^_]+)_ext_t".format(prefix=p))
        self.lv_obj_pattern = re.compile(
            "^{prefix}_([^_]+)".format(prefix=p), re.IGNORECASE
        )
        self.lv_func_pattern = re.compile(
            "^{prefix}_(.+)".format(prefix=p), re.IGNORECASE
        )
        self.create_obj_pattern = re.compile(
            "^{prefix}_(.+)_create$".format(prefix=p)
        )
        self.lv_method_pattern = re.compile(
            "^{prefix}_[^_]+_(.+)".format(prefix=p), re.IGNORECASE
        )
        self.lv_base_obj_pattern = re.compile(
            "^(struct _){{0,1}}{prefix}_{base_name}_t( [*]){{0,1}}".format(
                prefix=p, base_name=b
            )
        )
        self.lv_str_enum_pattern = re.compile(
            "^_?{prefix}_STR_(.+)".format(prefix=p.upper())
        )
        self.lv_callback_type_pattern = re.compile(
            "({prefix}_){{0,1}}(.+)_cb(_t){{0,1}}".format(prefix=p)
        )
        self.lv_global_callback_pattern = re.compile(".*g_cb_t")
        self.lv_func_returns_array = re.compile(".*_array$")
        self.lv_enum_name_pattern = re.compile(
            "^(ENUM_){{0,1}}({prefix}_){{0,1}}(.*)".format(prefix=p.upper())
        )

    def export_names(self):
        return self.EXPORT_NAMES
