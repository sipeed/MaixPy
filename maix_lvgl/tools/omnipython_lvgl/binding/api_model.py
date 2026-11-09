# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Target-neutral public API model built from the declaration IR.

This module describes the API independently of any C runtime or binding
backend.  Conversion details and target exceptions are intentionally separate
so the three backends can lower the same model.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field, replace
from os.path import commonprefix
from typing import Any, Mapping, Optional, Tuple

from .ir import (
    CEnum,
    CField,
    CParameter,
    CStruct,
    CType,
    DeclarationIndex,
    DeclarationIR,
    SourceLocation,
)

TARGETS = ("micropython", "circuitpython", "cpython")
API_SCHEMA_VERSION = 3


# These are the established public spellings used by the upstream-compatible
# Python API.  They describe enum ownership and naming only; they do not alter
# C declarations or generated C output.
_MODULE_ENUM_NAME_OVERRIDES = {
    "animimg_part_t": "ANIM_IMAGE_PART",
    "cache_reserve_cond_res_t": "CACHE_RESERVE_COND",
    "indev_gesture_type_t": "INDEV_GESTURE",
    "event_code_t": "EVENT",
    "align_t": "ALIGN",
    "color_format_t": "COLOR_FORMAT",
    "grad_dir_t": "GRAD_DIR",
    "grad_extend_t": "GRAD_EXTEND",
    "base_dir_t": "BASE_DIR",
    "opa_t": "OPA",
    "text_align_t": "TEXT_ALIGN",
    "palette_t": "PALETTE",
    "font_kerning_t": "FONT_KERNING",
    "font_subpx_t": "FONT_SUBPX",
    "font_glyph_format_t": "FONT_GLYPH_FORMAT",
    "dir_t": "DIR",
    "result_t": "RESULT",
    "log_level_t": "LOG_LEVEL",
    "font_fmt_txt_bitmap_format_t": "FONT_FMT_TXT",
    "font_fmt_txt_cmap_type_t": "FONT_FMT_TXT_CMAP",
    "fs_whence_t": "FS_SEEK",
}
_WIDGET_ENUM_NAME_OVERRIDES = {
    "barcode_encoding_t": ("barcode", "ENCODING_CODE128"),
    "menu_mode_header_t": ("menu", "HEADER"),
    "menu_mode_root_back_button_t": ("menu", "ROOT_BACK_BUTTON"),
    "obj_tree_walk_res_t": ("obj", "TREE_WALK"),
}


def api_hash_for_dict(data: Mapping[str, Any]) -> str:
    """Hash API content without trusting or including its stored hash field."""

    content = dict(data)
    content.pop("api_hash", None)
    encoded = json.dumps(content, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _type_to_dict(type_: CType) -> Mapping[str, Any]:
    result = {"kind": type_.kind}
    if type_.name is not None:
        result["name"] = type_.name
    if type_.qualifiers:
        result["qualifiers"] = list(type_.qualifiers)
    if type_.target is not None:
        result["target"] = _type_to_dict(type_.target)
    if type_.element is not None:
        result["element"] = _type_to_dict(type_.element)
    if type_.dimensions:
        result["dimensions"] = list(type_.dimensions)
    if type_.return_type is not None:
        result["return_type"] = _type_to_dict(type_.return_type)
    if type_.parameters:
        result["parameters"] = [_parameter_to_dict(parameter) for parameter in type_.parameters]
    if type_.variadic:
        result["variadic"] = True
    return result


def _field_to_dict(
    field_: CField, view: Optional[ApiTypeView] = None
) -> Mapping[str, Any]:
    result = {"name": field_.name, "type": _type_to_dict(field_.type)}
    if view is not None:
        result["view"] = view.to_dict()
    if field_.bit_width is not None:
        result["bit_width"] = field_.bit_width
    return result


def _location_to_dict(location: SourceLocation) -> Mapping[str, Any]:
    return {
        "file": location.file,
        "line": location.line,
        "column": location.column,
    }


@dataclass(frozen=True)
class ApiTypeView:
    """Target-neutral interpretation of one C type at the Python boundary."""

    python_type: str
    category: str
    conversion: str
    nullable: Optional[bool] = None
    lifetime: Optional[str] = None

    def to_dict(self) -> Mapping[str, Any]:
        result = {
            "python_type": self.python_type,
            "category": self.category,
            "conversion": self.conversion,
        }
        if self.nullable is not None:
            result["nullable"] = self.nullable
        if self.lifetime is not None:
            result["lifetime"] = self.lifetime
        return result


def _parameter_to_dict(
    parameter: CParameter, view: Optional[ApiTypeView] = None
) -> Mapping[str, Any]:
    result = {"name": parameter.name, "type": _type_to_dict(parameter.type)}
    if view is not None:
        result["view"] = view.to_dict()
    if parameter.location.file is not None:
        result["location"] = {
            "file": parameter.location.file,
            "line": parameter.location.line,
            "column": parameter.location.column,
        }
    return result


@dataclass(frozen=True)
class ApiFunction:
    c_name: str
    python_name: str
    role: str
    parameters: Tuple[CParameter, ...]
    return_type: CType
    receiver: Optional[str] = None
    static: bool = False
    variadic: bool = False
    storage: Tuple[str, ...] = ()
    function_specifiers: Tuple[str, ...] = ()
    available_on: Tuple[str, ...] = TARGETS
    visibility: str = "public"
    policy_reason: Optional[str] = None
    location: Optional[SourceLocation] = field(default=None)
    parameter_views: Tuple[ApiTypeView, ...] = ()
    return_view: Optional[ApiTypeView] = None

    def to_dict(self) -> Mapping[str, Any]:
        result = {
            "c_name": self.c_name,
            "python_name": self.python_name,
            "role": self.role,
            "parameters": [
                _parameter_to_dict(
                    parameter,
                    self.parameter_views[index]
                    if index < len(self.parameter_views)
                    else None,
                )
                for index, parameter in enumerate(self.parameters)
            ],
            "return_type": _type_to_dict(self.return_type),
            "static": self.static,
            "variadic": self.variadic,
            "storage": list(self.storage),
            "function_specifiers": list(self.function_specifiers),
            "available_on": list(self.available_on),
            "visibility": self.visibility,
        }
        if self.return_view is not None:
            result["return_view"] = self.return_view.to_dict()
        if self.policy_reason is not None:
            result["policy_reason"] = self.policy_reason
        if self.receiver is not None:
            result["receiver"] = self.receiver
        if self.location is not None:
            result["location"] = _location_to_dict(self.location)
        return result


@dataclass(frozen=True)
class ApiStruct:
    c_name: Optional[str]
    python_name: str
    kind: str
    fields: Tuple[CField, ...]
    typedef_names: Tuple[str, ...] = ()
    complete: bool = False
    available_on: Tuple[str, ...] = TARGETS
    methods: Tuple[str, ...] = ()
    visibility: str = "public"
    policy_reason: Optional[str] = None
    location: Optional[SourceLocation] = field(default=None)
    field_views: Tuple[ApiTypeView, ...] = ()

    def to_dict(self) -> Mapping[str, Any]:
        result = {
            "c_name": self.c_name,
            "python_name": self.python_name,
            "kind": self.kind,
            "fields": [
                _field_to_dict(
                    field_,
                    self.field_views[index]
                    if index < len(self.field_views)
                    else None,
                )
                for index, field_ in enumerate(self.fields)
            ],
            "typedef_names": list(self.typedef_names),
            "complete": self.complete,
            "available_on": list(self.available_on),
            "methods": list(self.methods),
            "visibility": self.visibility,
        }
        if self.policy_reason is not None:
            result["policy_reason"] = self.policy_reason
        if self.location is not None:
            result["location"] = _location_to_dict(self.location)
        return result


@dataclass(frozen=True)
class ApiEnum:
    c_name: Optional[str]
    python_name: str
    members: Tuple[Tuple[str, Optional[str]], ...]
    member_type: str = "int"
    typedef_names: Tuple[str, ...] = ()
    complete: bool = False
    available_on: Tuple[str, ...] = TARGETS
    visibility: str = "public"
    policy_reason: Optional[str] = None
    location: Optional[SourceLocation] = field(default=None)
    module_name: Optional[str] = None
    owners: Tuple[Tuple[str, str], ...] = ()

    def to_dict(self) -> Mapping[str, Any]:
        result = {
            "c_name": self.c_name,
            "python_name": self.python_name,
            "members": [
                {"name": name, "value": value} for name, value in self.members
            ],
            "member_type": self.member_type,
            "typedef_names": list(self.typedef_names),
            "complete": self.complete,
            "available_on": list(self.available_on),
            "visibility": self.visibility,
            "module_name": self.module_name,
            "owners": [
                {"object": object_name, "name": nested_name}
                for object_name, nested_name in self.owners
            ],
        }
        if self.policy_reason is not None:
            result["policy_reason"] = self.policy_reason
        if self.location is not None:
            result["location"] = _location_to_dict(self.location)
        return result


@dataclass(frozen=True)
class ApiTypedef:
    name: str
    type: CType
    c_name: Optional[str] = None
    callback: bool = False
    available_on: Tuple[str, ...] = TARGETS
    visibility: str = "public"
    policy_reason: Optional[str] = None
    location: Optional[SourceLocation] = field(default=None)
    type_view: Optional[ApiTypeView] = None

    def to_dict(self) -> Mapping[str, Any]:
        result = {
            "name": self.name,
            "c_name": self.c_name or self.name,
            "type": _type_to_dict(self.type),
            "callback": self.callback,
            "available_on": list(self.available_on),
            "visibility": self.visibility,
        }
        if self.type_view is not None:
            result["view"] = self.type_view.to_dict()
        if self.policy_reason is not None:
            result["policy_reason"] = self.policy_reason
        if self.location is not None:
            result["location"] = _location_to_dict(self.location)
        return result


@dataclass(frozen=True)
class ApiVariable:
    c_name: str
    type: CType
    python_name: Optional[str] = None
    storage: Tuple[str, ...] = ()
    available_on: Tuple[str, ...] = TARGETS
    visibility: str = "public"
    policy_reason: Optional[str] = None
    location: Optional[SourceLocation] = field(default=None)
    type_view: Optional[ApiTypeView] = None

    def to_dict(self) -> Mapping[str, Any]:
        result = {
            "c_name": self.c_name,
            "python_name": self.python_name or self.c_name,
            "type": _type_to_dict(self.type),
            "storage": list(self.storage),
            "available_on": list(self.available_on),
            "visibility": self.visibility,
        }
        if self.type_view is not None:
            result["view"] = self.type_view.to_dict()
        if self.policy_reason is not None:
            result["policy_reason"] = self.policy_reason
        if self.location is not None:
            result["location"] = _location_to_dict(self.location)
        return result


@dataclass(frozen=True)
class ApiConstant:
    c_name: str
    python_name: str
    value: Optional[str]
    available_on: Tuple[str, ...] = TARGETS
    visibility: str = "public"
    policy_reason: Optional[str] = None
    location: Optional[SourceLocation] = field(default=None)

    def to_dict(self) -> Mapping[str, Any]:
        result = {
            "c_name": self.c_name,
            "python_name": self.python_name,
            "value": self.value,
            "available_on": list(self.available_on),
            "visibility": self.visibility,
        }
        if self.policy_reason is not None:
            result["policy_reason"] = self.policy_reason
        if self.location is not None:
            result["location"] = _location_to_dict(self.location)
        return result


@dataclass(frozen=True)
class ApiObject:
    python_name: str
    c_type: str
    constructor: Optional[str]
    methods: Tuple[str, ...]
    parent: Optional[str] = None
    available_on: Tuple[str, ...] = TARGETS
    visibility: str = "public"
    policy_reason: Optional[str] = None

    def to_dict(self) -> Mapping[str, Any]:
        return {
            "python_name": self.python_name,
            "c_type": self.c_type,
            "constructor": self.constructor,
            "methods": list(self.methods),
            "parent": self.parent,
            "available_on": list(self.available_on),
            "visibility": self.visibility,
            **(
                {"policy_reason": self.policy_reason}
                if self.policy_reason is not None
                else {}
            ),
        }


@dataclass(frozen=True)
class ApiModel:
    module_prefix: str
    functions: Tuple[ApiFunction, ...]
    objects: Tuple[ApiObject, ...]
    structs: Tuple[ApiStruct, ...]
    enums: Tuple[ApiEnum, ...]
    typedefs: Tuple[ApiTypedef, ...]
    variables: Tuple[ApiVariable, ...]
    constants: Tuple[ApiConstant, ...] = ()
    schema_version: int = API_SCHEMA_VERSION

    def _content_dict(self) -> Mapping[str, Any]:
        return {
            "schema_version": self.schema_version,
            "module_prefix": self.module_prefix,
            "functions": [
                item.to_dict() for item in sorted(self.functions, key=lambda x: x.c_name)
            ],
            "objects": [
                item.to_dict() for item in sorted(self.objects, key=lambda x: x.python_name)
            ],
            "structs": [
                item.to_dict()
                for item in sorted(
                    self.structs, key=lambda x: (x.python_name, x.c_name or "")
                )
            ],
            "enums": [
                item.to_dict()
                for item in sorted(
                    self.enums, key=lambda x: (x.python_name, x.c_name or "")
                )
            ],
            "typedefs": [
                item.to_dict() for item in sorted(self.typedefs, key=lambda x: x.name)
            ],
            "variables": [
                item.to_dict() for item in sorted(self.variables, key=lambda x: x.c_name)
            ],
            "constants": [
                item.to_dict()
                for item in sorted(self.constants, key=lambda x: x.python_name)
            ],
        }

    @property
    def api_hash(self) -> str:
        return api_hash_for_dict(self._content_dict())

    def validation_errors(self) -> Tuple[str, ...]:
        """Return semantic model errors that do not require a target backend."""

        errors = []
        seen = {}

        def add(scope: str, name: str, source: str) -> None:
            key = (scope, name)
            previous = seen.get(key)
            if previous is not None:
                errors.append(
                    "duplicate export %s.%s (%s and %s)"
                    % (scope, name, previous, source)
                )
            else:
                seen[key] = source

        for function in self.functions:
            if function.visibility != "public":
                continue
            scope = (
                "module"
                if function.role == "module"
                else "constructor.%s" % function.receiver
                if function.role == "constructor"
                else "%s.%s" % (function.role, function.receiver or "<missing>")
            )
            add(scope, function.python_name, function.c_name)
            if not set(function.available_on) <= set(TARGETS):
                errors.append("unknown target on function %s" % function.c_name)
            if not function.available_on:
                errors.append("public function has no targets: %s" % function.c_name)

        for obj in self.objects:
            if obj.visibility == "public":
                add("module", obj.python_name, "object " + obj.python_name)
                if len(obj.methods) != len(set(obj.methods)):
                    errors.append("duplicate object methods: %s" % obj.python_name)
        for struct in self.structs:
            if struct.visibility == "public":
                add("module", struct.python_name, "struct " + struct.python_name)
        for enum in self.enums:
            if enum.visibility == "public":
                if enum.module_name is not None:
                    add("module", enum.module_name, "enum " + enum.python_name)
                for object_name, nested_name in enum.owners:
                    add(
                        "object." + object_name,
                        nested_name,
                        "enum " + enum.python_name,
                    )
                members = [name for name, _value in enum.members]
                if len(members) != len(set(members)):
                    errors.append("duplicate enum members: %s" % enum.python_name)
        type_names = {
            item.python_name
            for item in self.structs + self.enums
            if item.visibility == "public"
        }
        for typedef in self.typedefs:
            if typedef.visibility == "public":
                # A typedef that names a concrete struct/enum is the C alias
                # for that same Python type, not a second module export.
                if typedef.name in type_names and typedef.type.kind in {
                    "struct",
                    "union",
                    "enum",
                }:
                    continue
                add("module", typedef.name, "typedef " + typedef.c_name)
        for variable in self.variables:
            if variable.visibility == "public":
                add("module", variable.python_name or variable.c_name, "variable " + variable.c_name)
        for constant in self.constants:
            if constant.visibility == "public":
                add("module", constant.python_name, "constant " + constant.c_name)
        return tuple(errors)

    def to_dict(self) -> Mapping[str, Any]:
        result = dict(self._content_dict())
        result["api_hash"] = self.api_hash
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def _strip_prefix(name: str, module_prefix: str) -> str:
    prefix = module_prefix + "_"
    return name[len(prefix) :] if name.startswith(prefix) else name


def _python_type_name(name: str, module_prefix: str) -> str:
    """Return the legacy Python spelling for an LVGL typedef/tag name."""

    name = name.removeprefix("_" + module_prefix + "_")
    name = name.removeprefix(module_prefix + "_")
    if name and name[0].isdigit():
        return "_" + name
    return name


def _python_enum_name(name: Optional[str], module_prefix: str) -> str:
    if not name:
        return "<anonymous>"
    return _python_type_name(name, module_prefix).removesuffix("_t").upper()


def _python_enum_member_name(name: str, enum_name: str, module_prefix: str) -> str:
    for prefix in (
        "ENUM_" + module_prefix.upper() + "_" + enum_name + "_",
        module_prefix.upper() + "_" + enum_name + "_",
    ):
        if name.startswith(prefix):
            return name[len(prefix) :]
    if name.startswith("ENUM_" + module_prefix.upper() + "_"):
        return name[len("ENUM_" + module_prefix.upper() + "_") :]
    return name


def _same_struct(index: DeclarationIndex, left: Optional[str], right: Optional[str]) -> bool:
    if left is None or right is None:
        return left == right
    return index._struct_identity(left) == index._struct_identity(right)


def _public_struct_name(struct: CStruct) -> str:
    if struct.typedef_names:
        # The preprocessor can expose both a private implementation alias and
        # its public spelling.  Prefer the stable public spelling and make the
        return sorted(
            struct.typedef_names,
            key=lambda name: (name.startswith("_"), name),
        )[0]
    if struct.name:
        return struct.name
    return "<anonymous>"


def _struct_method_name(function_name: str, struct_c_name: str) -> str:
    """The name the runtimes give a struct method: the part of the function
    name after the last ``_`` it shares with the struct's C name, so
    lv_grad_linear_init on lv_grad_dsc_t is ``linear_init``
    (analyze.noncommon_part; lvgl-bindings#39)."""
    n = len(commonprefix([function_name, struct_c_name])) - 1
    while n > 0 and function_name[n] != "_":
        n -= 1
    return function_name[n + 1 :]


def _method_name(function_name: str, receiver: str, module_prefix: str) -> str:
    plain = _strip_prefix(function_name, module_prefix)
    stems = [receiver]
    if receiver.endswith("_t"):
        stems.append(receiver[:-2])
    for stem in stems:
        if plain.startswith(stem + "_"):
            return plain[len(stem) + 1 :]
    return plain


def _enum_stem(enum: CEnum, module_prefix: str) -> str:
    """Infer the public enum stem from its enumerator names."""

    names = [member for member in enum.members if not member.startswith("_")]
    if not names:
        return ""
    normalized = [
        name.removeprefix("ENUM_")
        for name in names
        if name.removeprefix("ENUM_").startswith(module_prefix.upper() + "_")
    ]
    if not normalized:
        return ""
    common_prefix = commonprefix(normalized)
    common = common_prefix.rstrip("_")
    if common_prefix and not common_prefix.endswith("_"):
        common = common.rsplit("_", 1)[0]
    if not common:
        return ""
    module_prefix_upper = module_prefix.upper() + "_"
    if common.startswith(module_prefix_upper):
        common = common[len(module_prefix_upper) :]
    return common.removesuffix("_T").upper()


def _enum_exports(
    enum: CEnum,
    *,
    module_prefix: str,
    object_names: Tuple[str, ...],
) -> Tuple[Optional[str], Tuple[Tuple[str, str], ...], str]:
    """Return module export, nested owners, and the C-derived enum stem."""

    typedef_names = tuple(
        name
        for name in enum.typedef_names
        if name.startswith(module_prefix + "_")
    )
    typedef_name = (
        typedef_names[0][len(module_prefix) + 1 :]
        if typedef_names
        else ""
    )
    stem = _enum_stem(enum, module_prefix)
    if typedef_name in _MODULE_ENUM_NAME_OVERRIDES:
        return _MODULE_ENUM_NAME_OVERRIDES[typedef_name], (), stem
    widget_override = _WIDGET_ENUM_NAME_OVERRIDES.get(typedef_name)
    if widget_override is not None:
        owner, nested_name = widget_override
        return None, ((owner, nested_name),), stem
    if stem == "STR_SYMBOL":
        return "SYMBOL", (), stem

    object_names = tuple(sorted(object_names, key=len, reverse=True))
    for object_name in object_names:
        prefix = object_name.upper() + "_"
        if stem.startswith(prefix):
            nested_name = stem[len(prefix) :]
            if nested_name:
                # OBJ_FLAG is intentionally exported both as lv.OBJ_FLAG and
                # as obj.FLAG by the established binding API.
                if object_name == "obj" and nested_name == "FLAG":
                    return "OBJ_FLAG", ((object_name, nested_name),), stem
                return None, ((object_name, nested_name),), stem

    if typedef_name:
        module_name = _python_enum_name(
            module_prefix + "_" + typedef_name, module_prefix
        )
    else:
        module_name = stem
    return module_name or None, (), stem


_INTEGER_TYPES = frozenset(
    {
        "char",
        "short",
        "int",
        "long",
        "signed",
        "unsigned",
        "_Bool",
        "bool",
        "int8_t",
        "uint8_t",
        "int16_t",
        "uint16_t",
        "int32_t",
        "uint32_t",
        "int64_t",
        "uint64_t",
        "intptr_t",
        "uintptr_t",
        "size_t",
    }
)
_INTEGER_WORDS = frozenset({"char", "short", "int", "long", "signed", "unsigned"})


def _is_integer_name(name: Optional[str]) -> bool:
    if not name:
        return False
    if name in _INTEGER_TYPES:
        return True
    words = set(name.split())
    return bool(words) and words <= _INTEGER_WORDS and "float" not in words


def _build_type_view_resolver(
    objects: Tuple[ApiObject, ...],
    structs: Tuple[ApiStruct, ...],
    enums: Tuple[ApiEnum, ...],
    typedefs: Tuple[ApiTypedef, ...],
):
    """Create a target-neutral C-to-Python type-view resolver."""

    def is_hidden_implementation(item) -> bool:
        """Exclude declarations deliberately hidden by API policy.

        Declarations outside the LVGL prefix are still useful as boundary
        types when a public LVGL function uses them.  A non-default policy
        reason, however, is an explicit decision that the implementation type
        must not appear in public annotations (for example ``global_t``).
        """

        return (
            item.visibility == "private"
            and item.policy_reason not in {None, "outside module prefix"}
        )

    object_by_c = {
        item.c_type: item.python_name
        for item in objects
        if not is_hidden_implementation(item)
    }
    struct_by_c = {}
    for item in structs:
        object_name = next(
            (
                object_.python_name
                for object_ in objects
                if object_.python_name + "_t" == item.python_name
                or object_.c_type in item.typedef_names
                or item.c_name == "_" + object_.c_type
            ),
            None,
        )
        if object_name is not None:
            for alias in (item.c_name,) + item.typedef_names:
                if alias:
                    object_by_c[alias] = object_name
            continue
        if is_hidden_implementation(item):
            continue
        if item.c_name:
            struct_by_c[item.c_name] = item.python_name
        for alias in item.typedef_names:
            struct_by_c[alias] = item.python_name
    enum_by_c = {}
    for item in enums:
        if is_hidden_implementation(item):
            continue
        if item.module_name is not None:
            python_type = item.module_name
        elif item.owners:
            owner, nested_name = item.owners[0]
            python_type = "%s.%s" % (owner, nested_name)
        else:
            python_type = item.python_name
        for alias in item.typedef_names:
            enum_by_c[alias] = python_type + " | int"
        if item.c_name:
            enum_by_c[item.c_name] = python_type + " | int"
    typedef_by_c = {
        item.c_name or item.name: item for item in typedefs
    }

    def named_view(name: Optional[str], seen: Tuple[str, ...]) -> ApiTypeView:
        if not name:
            return ApiTypeView("Any", "unknown", "unsupported")
        if name in object_by_c:
            return ApiTypeView(object_by_c[name], "object", "object_handle")
        if name in struct_by_c:
            return ApiTypeView(struct_by_c[name], "struct", "struct_value")
        if name in enum_by_c:
            return ApiTypeView(enum_by_c[name], "enum", "enum_int")
        typedef = typedef_by_c.get(name)
        if typedef is not None and name not in seen:
            return view(typedef.type, seen + (name,), alias=name)
        if name == "void":
            return ApiTypeView("None", "void", "none")
        if _is_integer_name(name):
            return ApiTypeView("int", "scalar", "integer")
        if name in {"float", "double"}:
            return ApiTypeView("float", "scalar", "float")
        if name == "va_list":
            return ApiTypeView("Any", "opaque", "opaque")
        return ApiTypeView("Any", "unknown", "unsupported")

    def view(
        type_: CType,
        seen: Tuple[str, ...] = (),
        alias: Optional[str] = None,
    ) -> ApiTypeView:
        if type_.kind in {"primitive", "identifier"}:
            return named_view(type_.name, seen)
        if type_.kind in {"struct", "union"}:
            result = named_view(type_.name, seen)
            if type_.name is None and alias is not None:
                result = named_view(alias, seen)
            if result.category == "unknown":
                return ApiTypeView("Any", "struct", "struct_value")
            return result
        if type_.kind == "enum":
            result = named_view(type_.name, seen)
            if type_.name is None and alias is not None:
                result = named_view(alias, seen)
            if result.category == "unknown":
                return ApiTypeView("int", "enum", "enum_int")
            return result
        if type_.kind == "pointer":
            target = type_.target or CType(kind="primitive", name="void")
            if target.kind == "function":
                return ApiTypeView(
                    callable_type(target),
                    "callback",
                    "callback",
                )
            if target.kind in {"primitive", "identifier", "struct", "union", "enum"}:
                target_view = view(target, seen)
                if target_view.category == "object":
                    return ApiTypeView(
                        target_view.python_type,
                        "object_pointer",
                        "object_handle",
                    )
                if target_view.category == "struct":
                    return ApiTypeView(
                        target_view.python_type,
                        "struct_pointer",
                        "struct_pointer",
                    )
                if target_view.category == "enum":
                    return ApiTypeView(
                        target_view.python_type,
                        "enum_pointer",
                        "enum_pointer",
                    )
                if target.kind == "primitive" and target.name == "char":
                    return ApiTypeView("str", "string", "string")
                if (
                    target.kind == "primitive" and _is_integer_name(target.name)
                ) or (
                    target.kind == "identifier"
                    and target_view.category == "scalar"
                    and target_view.python_type == "int"
                ):
                    return ApiTypeView("Any", "typed_buffer", "typed_buffer")
                if target.kind == "primitive" and target.name == "void":
                    return ApiTypeView("Any", "opaque_pointer", "opaque")
            return ApiTypeView("Any", "pointer", "pointer")
        if type_.kind == "array":
            element = type_.element or CType(kind="primitive", name="void")
            element_type = view(element, seen).python_type
            return ApiTypeView("Sequence[%s]" % element_type, "array", "array")
        if type_.kind == "function":
            return ApiTypeView(callable_type(type_), "callback", "callback")
        if type_.kind == "ellipsis":
            return ApiTypeView("Any", "variadic", "variadic")
        return ApiTypeView("Any", "unknown", "unsupported")

    def callable_type(type_: CType) -> str:
        parameters = [view(parameter.type).python_type for parameter in type_.parameters]
        return_type = view(type_.return_type or CType(kind="primitive", name="void"))
        if type_.variadic:
            parameter_spec = "..."
        else:
            parameter_spec = "[%s]" % ", ".join(parameters)
        return "Callable[%s, %s]" % (parameter_spec, return_type.python_type)

    return view


def build_api_model(
    declarations: DeclarationIR,
    *,
    module_prefix: str = "lv",
    base_obj_type: str = "lv_obj_t",
    policy=None,
) -> ApiModel:
    """Build a deterministic API model with explicit visibility policy."""
    if policy is None:
        from .api_policy import ApiPolicy

        policy = ApiPolicy.default(module_prefix=module_prefix)
    index = DeclarationIndex.from_ir(declarations, module_prefix=module_prefix)

    struct_names = {
        id(struct): _public_struct_name(struct) for struct in declarations.structs
    }
    struct_python_names = {
        id(struct): _python_type_name(struct_names[id(struct)], module_prefix)
        for struct in declarations.structs
    }
    struct_receivers = {}
    struct_c_receivers = {}
    for struct in declarations.structs:
        receiver = struct_names[id(struct)]
        for function in index.struct_functions(receiver):
            struct_receivers.setdefault(
                function.name, struct_python_names[id(struct)]
            )
            struct_c_receivers.setdefault(function.name, receiver)

    constructors = {}
    for function in declarations.functions:
        decision = policy.function(function.name)
        plain = _strip_prefix(function.name, module_prefix)
        if (
            decision.visibility != "public"
            or not plain.endswith("_create")
            or not function.parameters
        ):
            continue
        if _same_struct(
            index,
            index.first_argument_type_name(function.name),
            base_obj_type,
        ):
            constructors[plain[: -len("_create")]] = function.name

    functions = []
    object_methods = {name: [] for name in constructors}
    for function in declarations.functions:
        decision = policy.function(function.name)
        plain = _strip_prefix(function.name, module_prefix)
        role = "module"
        receiver = None
        if function.name in constructors.values():
            role = "constructor"
            receiver = next(
                name for name, c_name in constructors.items() if c_name == function.name
            )
        elif decision.visibility == "public":
            matching_objects = sorted(
                (
                    object_name
                    for object_name in constructors
                    if plain.startswith(object_name + "_")
                ),
                key=len,
                reverse=True,
            )
            if matching_objects:
                role = "object_method"
                receiver = matching_objects[0]
                object_methods[receiver].append(
                    plain[len(receiver) + 1 :]
                )
        if role == "module" and function.name in struct_receivers:
            role = "struct_method"
            receiver = struct_receivers[function.name]
        functions.append(
            ApiFunction(
                c_name=function.name,
                python_name=(
                    "create"
                    if role == "constructor"
                    else _struct_method_name(
                        function.name, struct_c_receivers[function.name]
                    )
                    if role == "struct_method"
                    else _method_name(function.name, receiver, module_prefix)
                    if receiver is not None
                    else plain
                ),
                role=role,
                receiver=receiver,
                parameters=function.parameters,
                return_type=function.return_type,
                static=(
                    role == "object_method"
                    and not _same_struct(
                        index,
                        index.first_argument_type_name(function.name),
                        base_obj_type,
                    )
                ),
                variadic=function.variadic,
                storage=function.storage,
                function_specifiers=function.function_specifiers,
                available_on=decision.available_on,
                visibility=decision.visibility,
                policy_reason=decision.reason,
                location=function.location,
            )
        )

    objects = tuple(
        ApiObject(
            python_name=name,
            c_type=module_prefix + "_" + name + "_t",
            constructor=constructors[name],
            methods=tuple(sorted(object_methods[name])),
            parent=None if name == "obj" else "obj",
            available_on=tuple(
                target
                for target in TARGETS
                if all(
                    target in function.available_on
                    for function in functions
                    if function.receiver == name
                )
            ),
        )
        for name in sorted(constructors)
    )

    # A C record is a public Python struct only when a public declaration can
    # actually produce or consume it.  Prefix-based visibility alone exposed
    # object backing records and configuration-only implementation records in
    # the stub even though no backend registered them.  Compute this closure
    # once from the target-neutral declarations instead of learning it from a
    # generated target artifact.
    struct_by_c_name = {}
    for struct in declarations.structs:
        for name in (struct.name,) + tuple(struct.typedef_names):
            if name:
                struct_by_c_name[name] = struct

    def referenced_type_names(type_):
        names = set()
        if type_ is None:
            return names
        if type_.kind in {"identifier", "struct", "union"} and type_.name:
            names.add(type_.name)
        names.update(referenced_type_names(type_.target))
        names.update(referenced_type_names(type_.element))
        names.update(referenced_type_names(type_.return_type))
        for parameter in type_.parameters:
            names.update(referenced_type_names(parameter.type))
        return names

    object_c_types = {item.c_type for item in objects}
    pending_struct_names = set()
    for declaration, api_function in zip(declarations.functions, functions):
        if api_function.visibility != "public":
            continue
        pending_struct_names.update(referenced_type_names(declaration.return_type))
        for parameter in declaration.parameters:
            pending_struct_names.update(referenced_type_names(parameter.type))
    for variable in declarations.variables:
        if policy.variable(variable.name).visibility == "public":
            pending_struct_names.update(referenced_type_names(variable.type))
    pending_struct_names.difference_update(object_c_types)

    reachable_structs = set()
    while pending_struct_names:
        type_name = pending_struct_names.pop()
        struct = struct_by_c_name.get(type_name)
        if struct is None or id(struct) in reachable_structs:
            continue
        reachable_structs.add(id(struct))
        for field in struct.fields:
            field_names = referenced_type_names(field.type)
            field_names.difference_update(object_c_types)
            pending_struct_names.update(field_names)

    function_by_name = {function.c_name: function for function in functions}
    structs = []
    for struct in sorted(
        declarations.structs,
        key=lambda item: (_public_struct_name(item), item.name or ""),
    ):
        decision = policy.struct((struct.name,) + tuple(struct.typedef_names))
        record_names = {name for name in (struct.name,) + tuple(struct.typedef_names) if name}
        if decision.visibility == "public" and record_names & object_c_types:
            visibility = "private"
            policy_reason = "represented by an LVGL object wrapper"
        elif decision.visibility == "public" and id(struct) not in reachable_structs:
            visibility = "private"
            policy_reason = "not reachable from a public binding boundary"
        else:
            visibility = decision.visibility
            policy_reason = decision.reason
        structs.append(ApiStruct(
            c_name=struct.name,
            python_name=struct_python_names[id(struct)],
            kind=struct.kind,
            fields=struct.fields,
            typedef_names=struct.typedef_names,
            complete=struct.complete,
            methods=tuple(
                sorted(
                    function_by_name[function.name].python_name
                    for function in index.struct_functions(struct_names[id(struct)])
                    if function.name in function_by_name
                )
            ),
            visibility=visibility,
            policy_reason=policy_reason,
            location=struct.location,
        ))
    structs = tuple(structs)
    enums = []
    symbol_members = None
    object_names = tuple(constructors)
    for enum in sorted(
        declarations.enums,
        key=lambda item: (
            item.typedef_names[0]
            if item.typedef_names
            else item.name or "<anonymous>",
            item.name or "",
        ),
    ):
        if not enum.name and not enum.typedef_names:
            continue
        enum_name = _python_enum_name(
            enum.typedef_names[0] if enum.typedef_names else enum.name,
            module_prefix,
        )
        module_name, owners, enum_stem = _enum_exports(
            enum,
            module_prefix=module_prefix,
            object_names=object_names,
        )
        decision = policy.enum((enum.name,) + tuple(enum.typedef_names))
        members = tuple(
            (
                _python_enum_member_name(member, enum_stem, module_prefix),
                value,
            )
            for member, value in (
                enum.values or tuple((member, None) for member in enum.members)
            )
        )
        enums.append(
            ApiEnum(
                c_name=enum.name,
                python_name=enum_name,
                members=members,
                typedef_names=enum.typedef_names,
                complete=enum.complete,
                visibility=decision.visibility,
                policy_reason=decision.reason,
                location=enum.location,
                module_name=module_name,
                owners=owners,
            )
        )
        if enum_stem == "STR_SYMBOL":
            symbol_members = members
    if symbol_members:
        enums.append(
            ApiEnum(
                c_name=None,
                python_name="SYMBOL",
                members=symbol_members,
                member_type="str",
                complete=True,
                location=next(
                    enum.location
                    for enum in enums
                    if enum.python_name == "STR_SYMBOL_ID"
                ),
                module_name="SYMBOL",
            )
        )
    typedefs = tuple(
        ApiTypedef(
            name=_python_type_name(typedef.name, module_prefix),
            c_name=typedef.name,
            type=typedef.type,
            callback=typedef.name in declarations.callback_typedefs,
            visibility=(decision := policy.typedef(typedef.name)).visibility,
            policy_reason=decision.reason,
            location=typedef.location,
        )
        for typedef in declarations.typedefs
    )
    variables = list(
        ApiVariable(
            c_name=variable.name,
            type=variable.type,
            python_name=_strip_prefix(variable.name, module_prefix),
            storage=variable.storage,
            visibility=(decision := policy.variable(variable.name)).visibility,
            policy_reason=decision.reason,
            location=variable.location,
        )
        for variable in declarations.variables
    )
    # _nesting is not an LVGL declaration; it is a synthetic entry for the
    # binding-internal callback re-entrancy counter injected into
    # analyze.py's `blobs` (see analyze.py). It is deliberately private
    # (not part of the documented public API) but still emitted as a real
    # MicroPython/CircuitPython module global and stubbed, because
    # PyDevices' display_driver.py (pydevices lib/) depends on it to
    # detect reentrant lv.task_handler() calls. See emit_backend.py's
    # module_registration_plan and emit_pyi_canonical.py's CanonicalPyiEmitter
    # for the matching audited exceptions.
    variables.append(
        ApiVariable(
            c_name="_nesting",
            type=CType(kind="primitive", name="int"),
            python_name="_nesting",
            storage=("static",),
            visibility="private",
            policy_reason="Binding re-entrancy guard; not a user-facing LVGL symbol.",
        )
    )
    constants = []
    anonymous_groups = {}
    enum_prefix = "ENUM_" + module_prefix.upper() + "_"
    for enum in declarations.enums:
        for name, value in enum.values:
            if not name.startswith(enum_prefix):
                continue
            suffix = name[len(enum_prefix) :]
            group = suffix.rsplit("_", 1)[0] if "_" in suffix else suffix
            anonymous_groups.setdefault(group, []).append((enum, name, value))
    for group, members in sorted(anonymous_groups.items()):
        if len(members) > 1:
            enums.append(
                ApiEnum(
                    c_name=None,
                    python_name=group,
                    members=tuple(
                        (
                            _python_enum_member_name(name, group, module_prefix),
                            value,
                        )
                        for _enum, name, value in members
                    ),
                    complete=True,
                    location=members[0][0].location,
                    module_name=group,
                )
            )
        else:
            enum, name, value = members[0]
            constants.append(
                ApiConstant(
                    c_name=name,
                    python_name=name[len(enum_prefix) :],
                    value=value,
                    location=enum.location,
                )
                )
    enum_tuple = tuple(enums)
    type_view = _build_type_view_resolver(
        objects, structs, enum_tuple, typedefs
    )

    def parameter_type_view(type_):
        resolved = type_view(type_)
        if type_.kind == "array" and type_.element is not None:
            element = type_view(type_.element)
            if element.category == "struct":
                # Native runtimes consume one contiguous Struct allocation,
                # constructed as ``point_t(count)`` and indexed in Python.
                # A list of independently allocated wrappers is not a valid C
                # array and must not be advertised as Sequence[point_t].
                return ApiTypeView(
                    element.python_type,
                    "struct_array",
                    "struct_pointer",
                    nullable=resolved.nullable,
                    lifetime=resolved.lifetime,
                )
        return resolved

    functions = tuple(
        replace(
            function,
            parameter_views=tuple(
                parameter_type_view(parameter.type)
                for parameter in function.parameters
            ),
            return_view=type_view(function.return_type),
        )
        for function in functions
    )
    structs = tuple(
        replace(
            struct,
            field_views=tuple(type_view(field_.type) for field_ in struct.fields),
        )
        for struct in structs
    )
    typedefs = tuple(
        replace(
            typedef,
            type_view=type_view(typedef.type, alias=typedef.c_name or typedef.name),
        )
        for typedef in typedefs
    )
    variables = tuple(
        replace(variable, type_view=type_view(variable.type))
        for variable in variables
    )
    return ApiModel(
        module_prefix=module_prefix,
        functions=functions,
        objects=objects,
        structs=structs,
        enums=enum_tuple,
        typedefs=typedefs,
        variables=variables,
        constants=tuple(constants),
    )


def write_api_model(model: ApiModel, path: Any) -> None:
    """Write deterministic JSON for review, hashing, and downstream checks."""
    with open(path, "w", encoding="utf-8") as output:
        output.write(model.to_json())
