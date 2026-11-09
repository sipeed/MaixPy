#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Validate the generated target-neutral API model and its content hash."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .api_model import API_SCHEMA_VERSION, TARGETS, api_hash_for_dict


def _validate_type_view(view, label, errors):
    if not isinstance(view, dict):
        errors.append("%s must be an object" % label)
        return
    for key in ("python_type", "category", "conversion"):
        if not isinstance(view.get(key), str) or not view[key]:
            errors.append("%s.%s must be a non-empty string" % (label, key))
    if "nullable" in view and not isinstance(view["nullable"], bool):
        errors.append("%s.nullable must be boolean" % label)
    if "lifetime" in view and (
        not isinstance(view["lifetime"], str) or not view["lifetime"]
    ):
        errors.append("%s.lifetime must be a non-empty string" % label)


def validate_api_data(data):
    errors = []
    if data.get("schema_version") != API_SCHEMA_VERSION:
        errors.append("unsupported API schema version")
    if not isinstance(data.get("api_hash"), str):
        errors.append("missing api_hash")
    elif data["api_hash"] != api_hash_for_dict(data):
        errors.append("api_hash does not match canonical content")
    if data.get("module_prefix") != "lv":
        errors.append("unexpected module prefix")
    sections = (
        "functions",
        "objects",
        "structs",
        "enums",
        "typedefs",
        "variables",
        "constants",
    )
    for section in sections:
        if not isinstance(data.get(section), list):
            errors.append("section %s must be a list" % section)
    function_exports = {}
    for function in data.get("functions", ()):
        parameters = function.get("parameters")
        if isinstance(parameters, list):
            for index, parameter in enumerate(parameters):
                _validate_type_view(
                    parameter.get("view"),
                    "function %s parameter %d view"
                    % (function.get("c_name"), index),
                    errors,
                )
        else:
            errors.append(
                "function %s parameters must be a list" % function.get("c_name")
            )
        _validate_type_view(
            function.get("return_view"),
            "function %s return view" % function.get("c_name"),
            errors,
        )
        available = function.get("available_on", ())
        if not set(available) <= set(TARGETS):
            errors.append("function %s has an unknown target" % function.get("c_name"))
        if function.get("visibility") == "public" and not available:
            errors.append("public function %s has no targets" % function.get("c_name"))
        if function.get("visibility") == "public":
            key = (
                function.get("role"),
                function.get("receiver"),
                function.get("python_name"),
            )
            if key in function_exports:
                errors.append(
                    "duplicate function export %s (%s and %s)"
                    % (
                        function.get("python_name"),
                        function_exports[key],
                        function.get("c_name"),
                    )
                )
            else:
                function_exports[key] = function.get("c_name")
    for section in (
        "objects",
        "structs",
        "enums",
        "typedefs",
        "variables",
        "constants",
    ):
        for item in data.get(section, ()):
            if section == "enums" and item.get("member_type") not in {"int", "str"}:
                errors.append(
                    "enum %s has an unsupported member type"
                    % (item.get("python_name") or item.get("c_name"))
                )
            if section == "structs":
                fields = item.get("fields")
                if isinstance(fields, list):
                    for index, field in enumerate(fields):
                        _validate_type_view(
                            field.get("view"),
                            "struct %s field %d view"
                            % (item.get("python_name"), index),
                            errors,
                        )
                else:
                    errors.append(
                        "struct %s fields must be a list" % item.get("python_name")
                    )
            elif section in {"typedefs", "variables"}:
                _validate_type_view(
                    item.get("view"),
                    "%s %s view" % (section[:-1], item.get("python_name")),
                    errors,
                )
            available = item.get("available_on", ())
            if not set(available) <= set(TARGETS):
                name = item.get("python_name") or item.get("name") or item.get("c_name")
                errors.append("%s %s has an unknown target" % (section, name))
            if item.get("visibility") == "public" and not available:
                name = item.get("python_name") or item.get("name") or item.get("c_name")
                errors.append("public %s %s has no targets" % (section, name))
    names = {}
    for function in data.get("functions", ()):
        if function.get("visibility") != "public" or function.get("role") != "module":
            continue
        name = function.get("python_name")
        if name in names:
            errors.append(
                "duplicate module export %s (function and %s)" % (name, names[name])
            )
        else:
            names[name] = "function"
    type_names = {
        item.get("python_name")
        for section in ("structs", "enums")
        for item in data.get(section, ())
        if item.get("visibility") == "public"
    }
    for section in ("objects", "structs", "enums", "typedefs", "variables", "constants"):
        for item in data.get(section, ()):
            if item.get("visibility") != "public":
                continue
            name = item.get("python_name") or item.get("name")
            if (
                section == "typedefs"
                and name in type_names
                and item.get("type", {}).get("kind") in {"struct", "union", "enum"}
            ):
                continue
            if name in names:
                errors.append(
                    "duplicate module export %s (%s and %s)"
                    % (name, names[name], section)
                )
            else:
                names[name] = section
            members = item.get("members")
            if isinstance(members, list):
                member_names = [member.get("name") for member in members]
                if len(member_names) != len(set(member_names)):
                    errors.append("duplicate enum members: %s" % name)
            methods = item.get("methods") if section == "objects" else None
            if isinstance(methods, list) and len(methods) != len(set(methods)):
                errors.append("duplicate object methods: %s" % name)
    return errors


def main(argv=None):
    path = Path((argv or sys.argv)[1])
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    errors = validate_api_data(data)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("OK: %s (%s)" % (path, data["api_hash"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
