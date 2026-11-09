# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Validate a generated pyi against the canonical API manifest."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping

from .api_model import API_SCHEMA_VERSION, TARGETS
from .emit_pyi_canonical import _identifier
from .verify_api import validate_api_data

_ALL_TARGETS = frozenset(TARGETS)
_HELPER_NAMES = frozenset({"C_Pointer", "LvReferenceError"})
_PRIVATE_HELPER_NAMES = frozenset({"_Blob", "_BlobT", "_Struct", "_StructT", "_Nesting"})


def _available(item: Mapping[str, Any], target: str) -> bool:
    available = set(item.get("available_on", ()))
    return _ALL_TARGETS <= available if target == "all" else target in available


def _public(item: Mapping[str, Any], target: str) -> bool:
    return item.get("visibility") == "public" and _available(item, target)


def _top_level_nodes(tree: ast.Module) -> dict[str, ast.AST]:
    nodes: dict[str, ast.AST] = {}
    for node in tree.body:
        names = []
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.append(node.target.id)
        elif isinstance(node, ast.Assign):
            names.extend(
                target.id for target in node.targets if isinstance(target, ast.Name)
            )
        for name in names:
            nodes[name] = node
    return nodes


def _class_nodes(tree: ast.Module) -> dict[str, ast.ClassDef]:
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def _member_nodes(class_node: ast.ClassDef) -> dict[str, ast.AST]:
    nodes: dict[str, ast.AST] = {}
    for node in class_node.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            nodes[node.name] = node
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            nodes[node.target.id] = node
    return nodes


def _annotation_text(node: ast.AST | None) -> str | None:
    return ast.unparse(node) if node is not None else None


def _class_type_aliases(class_node: ast.ClassDef) -> dict[str, str]:
    aliases = {}
    for node in class_node.body:
        if not (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and isinstance(node.annotation, ast.Name)
            and node.annotation.id == "TypeAlias"
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        aliases[node.value.value] = node.target.id
    return aliases


def _apply_type_aliases(
    python_type: str, type_aliases: Mapping[str, str]
) -> str:
    for type_name, alias in type_aliases.items():
        python_type = re.sub(r"\b%s\b" % re.escape(type_name), alias, python_type)
    return python_type


def _expected_parameters(
    function: Mapping[str, Any],
    *,
    skip_receiver: bool,
    constructor: bool,
    type_aliases: Mapping[str, str] | None = None,
) -> list[tuple[str, str, bool]]:
    parameters = list(function.get("parameters", ()))
    if skip_receiver and not function.get("static"):
        parameters = parameters[1:]
    used = {"self"} if not constructor and not function.get("static") else set()
    result = []
    for index, parameter in enumerate(parameters):
        name = _identifier(parameter.get("name") or "arg")
        original = name
        suffix = 2
        while name in used:
            name = "%s%d" % (original, suffix)
            suffix += 1
        used.add(name)
        if parameter.get("type", {}).get("kind") == "ellipsis":
            result.append(("*" + name, "Any", False))
            continue
        parameter_type = parameter.get("view", {}).get("python_type")
        if not isinstance(parameter_type, str) or not parameter_type:
            parameter_type = "Any"
        parameter_type = _apply_type_aliases(parameter_type, type_aliases or {})
        default = (
            constructor
            and index == 0
            and parameter.get("name") == "parent"
            and parameter.get("view", {}).get("category") == "object_pointer"
        )
        if default:
            parameter_type += " | None"
        result.append((name, parameter_type, default))
    if function.get("variadic"):
        result.append(("*args", "Any", False))
    return result


def _expected_function_signature(
    function: Mapping[str, Any],
    *,
    instance: bool,
    skip_receiver: bool = False,
    type_aliases: Mapping[str, str] | None = None,
) -> tuple[list[tuple[str, str, bool]], str, bool]:
    constructor = function.get("role") == "constructor"
    parameters = _expected_parameters(
        function,
        skip_receiver=skip_receiver,
        constructor=constructor,
        type_aliases=type_aliases,
    )
    if instance or constructor:
        parameters.insert(0, ("self", "", False))
    return_type = "None" if constructor else function.get("return_view", {}).get("python_type")
    if not isinstance(return_type, str) or not return_type:
        return_type = "Any"
    return_type = _apply_type_aliases(return_type, type_aliases or {})
    return parameters, return_type, bool(function.get("static"))


def _actual_function_signature(node: ast.FunctionDef) -> tuple[list[tuple[str, str | None]], str | None, bool]:
    parameters = []
    for argument in node.args.posonlyargs + node.args.args:
        parameters.append((argument.arg, _annotation_text(argument.annotation)))
    if node.args.vararg is not None:
        parameters.append(("*" + node.args.vararg.arg, _annotation_text(node.args.vararg.annotation)))
    for argument in node.args.kwonlyargs:
        parameters.append((argument.arg, _annotation_text(argument.annotation)))
    if node.args.kwarg is not None:
        parameters.append(("**" + node.args.kwarg.arg, _annotation_text(node.args.kwarg.annotation)))
    static = any(
        isinstance(decorator, ast.Name) and decorator.id == "staticmethod"
        for decorator in node.decorator_list
    )
    return parameters, _annotation_text(node.returns), static


def _default_parameter_indexes(node: ast.FunctionDef) -> set[int]:
    first_default = len(node.args.args) - len(node.args.defaults)
    return set(range(first_default, len(node.args.args)))


def _expected_top_level(data: Mapping[str, Any], target: str) -> set[str]:
    expected = set(_HELPER_NAMES | _PRIVATE_HELPER_NAMES)
    for section in ("objects", "structs"):
        expected.update(
            _identifier(item["python_name"])
            for item in data.get(section, ())
            if _public(item, target)
        )
    expected.update(
        _identifier(item["module_name"])
        for item in data.get("enums", ())
        if _public(item, target) and item.get("module_name")
    )
    expected.update(
        _identifier(item["python_name"])
        for item in data.get("functions", ())
        if _public(item, target) and item.get("role") == "module"
    )
    expected.update(
        _identifier(item["python_name"])
        for item in data.get("variables", ())
        if _public(item, target) and item.get("c_name") != "_nesting"
    )
    # _nesting is private in the canonical model but still deliberately
    # stubbed (as `_Nesting`, see CanonicalPyiEmitter) for the targets that
    # emit it; see api_model.build_api_model for the rationale.
    if any(item.get("c_name") == "_nesting" for item in data.get("variables", ())):
        expected.add("_nesting")
    expected.update(
        _identifier(item["python_name"])
        for item in data.get("constants", ())
        if _public(item, target)
    )
    return expected


def _expected_enum_members(enum: Mapping[str, Any]) -> set[str]:
    return {_identifier(member["name"]) for member in enum.get("members", ())}


def _expected_class_members(
    data: Mapping[str, Any], class_name: str, target: str
) -> set[str]:
    expected: set[str] = set()
    struct = next(
        (
            item
            for item in data.get("structs", ())
            if item.get("python_name") == class_name and _public(item, target)
        ),
        None,
    )
    if struct is not None:
        field_names = {
            _identifier(field.get("name") or "field")
            for field in struct.get("fields", ())
        }
        expected.update(field_names)
        expected.update(
            _identifier(function["python_name"])
            for function in data.get("functions", ())
            if function.get("role") == "struct_method"
            and function.get("receiver") == class_name
            and _public(function, target)
            and _identifier(function["python_name"]) not in field_names
        )

    object_ = next(
        (
            item
            for item in data.get("objects", ())
            if item.get("python_name") == class_name and _public(item, target)
        ),
        None,
    )
    if object_ is not None:
        expected.update(
            owner["name"]
            for enum in data.get("enums", ())
            if _public(enum, target)
            for owner in enum.get("owners", ())
            if owner.get("object") == class_name
        )
        if any(
            function.get("role") == "constructor"
            and function.get("receiver") == class_name
            and _public(function, target)
            for function in data.get("functions", ())
        ):
            expected.add("__init__")
        expected.update(
            _identifier(function["python_name"])
            for function in data.get("functions", ())
            if function.get("role") == "object_method"
            and function.get("receiver") == class_name
            and _public(function, target)
        )
    return expected


def validate_pyi_data(
    data: Mapping[str, Any], source: str, *, target: str = "all"
) -> list[str]:
    """Return manifest discrepancies for one generated stub source."""

    errors = []
    if data.get("schema_version") != API_SCHEMA_VERSION:
        return ["unsupported API schema version"]
    if target not in TARGETS + ("all",):
        return ["unsupported stub target: %s" % target]
    api_errors = validate_api_data(data)
    if api_errors:
        return ["invalid API model: %s" % error for error in api_errors]
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return ["stub is not valid Python: %s" % error]

    actual_top = set(_top_level_nodes(tree))
    expected_top = _expected_top_level(data, target)
    for name in sorted(expected_top - actual_top):
        errors.append("missing top-level export: %s" % name)
    for name in sorted(actual_top - expected_top):
        errors.append("unexpected top-level export: %s" % name)

    classes = _class_nodes(tree)
    for item in data.get("enums", ()):
        if not (_public(item, target) and item.get("module_name")):
            continue
        name = _identifier(item["module_name"])
        class_node = classes.get(name)
        if class_node is None:
            continue
        actual_members = set(_member_nodes(class_node))
        expected_members = _expected_enum_members(item)
        for member in sorted(expected_members - actual_members):
            errors.append("missing enum member: %s.%s" % (name, member))
        for member in sorted(actual_members - expected_members):
            errors.append("unexpected enum member: %s.%s" % (name, member))

    for item in data.get("objects", ()):
        if not _public(item, target):
            continue
        name = _identifier(item["python_name"])
        class_node = classes.get(name)
        if class_node is None:
            continue
        actual_members = set(_member_nodes(class_node))
        expected_members = _expected_class_members(data, item["python_name"], target)
        for member in sorted(expected_members - actual_members):
            errors.append("missing member: %s.%s" % (name, member))
        for member in sorted(actual_members - expected_members):
            if not member.startswith("__"):
                errors.append("unexpected member: %s.%s" % (name, member))

    for item in data.get("structs", ()):
        if not _public(item, target):
            continue
        name = _identifier(item["python_name"])
        class_node = classes.get(name)
        if class_node is None:
            continue
        actual_members = set(_member_nodes(class_node))
        expected_members = _expected_class_members(data, item["python_name"], target)
        for member in sorted(expected_members - actual_members):
            errors.append("missing member: %s.%s" % (name, member))
        for member in sorted(actual_members - expected_members):
            if not member.startswith("__"):
                errors.append("unexpected member: %s.%s" % (name, member))

    top_nodes = _top_level_nodes(tree)

    def check_function(
        function: Mapping[str, Any],
        node: ast.FunctionDef,
        *,
        label: str,
        instance: bool,
        skip_receiver: bool = False,
        type_aliases: Mapping[str, str] | None = None,
    ) -> None:
        expected, return_type, expected_static = _expected_function_signature(
            function,
            instance=instance,
            skip_receiver=skip_receiver,
            type_aliases=type_aliases,
        )
        actual, actual_return, actual_static = _actual_function_signature(node)
        expected_shape = [(name, annotation or None) for name, annotation, _ in expected]
        if actual != expected_shape or actual_return != return_type:
            errors.append(
                "signature mismatch: %s (expected %s -> %s, got %s -> %s)"
                % (label, expected_shape, return_type, actual, actual_return)
            )
        expected_defaults = {
            index
            for index, (_name, _annotation, has_default) in enumerate(expected)
            if has_default and not _name.startswith("*")
        }
        if _default_parameter_indexes(node) != expected_defaults:
            errors.append("default mismatch: %s" % label)
        if actual_static != expected_static:
            errors.append("staticmethod mismatch: %s" % label)

    for function in data.get("functions", ()):
        if not _public(function, target):
            continue
        role = function.get("role")
        if role == "module":
            node = top_nodes.get(_identifier(function["python_name"]))
            if isinstance(node, ast.FunctionDef):
                check_function(function, node, label=function["python_name"], instance=False)
            continue
        receiver = function.get("receiver")
        if not receiver:
            continue
        receiver_node = classes.get(_identifier(receiver))
        if receiver_node is None:
            continue
        members = _member_nodes(receiver_node)
        if role == "constructor":
            node_name = "__init__"
            instance = True
            skip_receiver = False
        elif role in {"object_method", "struct_method"}:
            node_name = _identifier(function["python_name"])
            instance = not function.get("static")
            skip_receiver = instance
        else:
            continue
        node = members.get(node_name)
        if isinstance(node, ast.FunctionDef):
            check_function(
                function,
                node,
                label="%s.%s" % (receiver, node_name),
                instance=instance,
                skip_receiver=skip_receiver,
                type_aliases=(
                    _class_type_aliases(receiver_node)
                    if role == "struct_method"
                    else None
                ),
            )

    for item in data.get("enums", ()):
        if not _public(item, target):
            continue
        enum_type = item.get("member_type", "int")
        targets = []
        if item.get("module_name"):
            targets.append((_identifier(item["module_name"]), classes.get(_identifier(item["module_name"]))))
        for owner in item.get("owners", ()):
            owner_node = classes.get(_identifier(owner["object"]))
            nested = _member_nodes(owner_node).get(owner["name"]) if owner_node else None
            targets.append(("%s.%s" % (owner["object"], owner["name"]), nested))
        for enum_label, enum_node in targets:
            if not isinstance(enum_node, ast.ClassDef):
                continue
            for member in item.get("members", ()):
                member_node = _member_nodes(enum_node).get(_identifier(member["name"]))
                if isinstance(member_node, ast.AnnAssign):
                    actual_type = _annotation_text(member_node.annotation)
                    if actual_type != enum_type:
                        errors.append(
                            "enum member type mismatch: %s.%s (expected %s, got %s)"
                            % (enum_label, member["name"], enum_type, actual_type)
                        )

    for item in data.get("structs", ()):
        if not _public(item, target):
            continue
        class_node = classes.get(_identifier(item["python_name"]))
        if class_node is None:
            continue
        members = _member_nodes(class_node)
        type_aliases = _class_type_aliases(class_node)
        for field in item.get("fields", ()):
            field_node = members.get(_identifier(field.get("name") or "field"))
            if isinstance(field_node, ast.AnnAssign):
                expected_type = field.get("view", {}).get("python_type")
                if isinstance(expected_type, str):
                    expected_type = _apply_type_aliases(expected_type, type_aliases)
                actual_type = _annotation_text(field_node.annotation)
                if actual_type != expected_type:
                    errors.append(
                        "field type mismatch: %s.%s (expected %s, got %s)"
                        % (
                            item["python_name"],
                            field.get("name"),
                            expected_type,
                            actual_type,
                        )
                    )

    for variable in data.get("variables", ()):
        if not _public(variable, target) or variable.get("c_name") == "_nesting":
            continue
        node = top_nodes.get(_identifier(variable["python_name"]))
        if isinstance(node, ast.AnnAssign):
            expected_type = variable.get("view", {}).get("python_type")
            actual_type = _annotation_text(node.annotation)
            if actual_type != expected_type:
                errors.append(
                    "variable type mismatch: %s (expected %s, got %s)"
                    % (variable["python_name"], expected_type, actual_type)
                )

    for constant in data.get("constants", ()):
        if not _public(constant, target):
            continue
        node = top_nodes.get(_identifier(constant["python_name"]))
        if isinstance(node, ast.AnnAssign) and _annotation_text(node.annotation) != "int":
            errors.append("constant type mismatch: %s" % constant["python_name"])

    return errors


def validate_pyi_file(api_path: Path, pyi_path: Path, *, target: str = "all") -> list[str]:
    with api_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return validate_pyi_data(
        data,
        pyi_path.read_text(encoding="utf-8"),
        target=target,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("api", type=Path, help="canonical generated/api.json")
    parser.add_argument("pyi", type=Path, help="generated/lvgl.pyi")
    parser.add_argument(
        "--target",
        choices=list(TARGETS) + ["all"],
        default="all",
        help="stub target represented by the pyi",
    )
    args = parser.parse_args(argv)
    errors = validate_pyi_file(args.api, args.pyi, target=args.target)
    if errors:
        for error in errors:
            print("FAIL: %s" % error, file=sys.stderr)
        return 1
    print("OK: %s matches canonical API manifest" % args.pyi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
