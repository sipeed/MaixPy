#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Verify every native module namespace against the canonical API model."""
from __future__ import print_function

import json
import re
import sys
from pathlib import Path

# Also exported at module level (lv.OBJ_FLAG) while nested on obj.FLAG.
MODULE_LEVEL_DUPLEX_ENUMS = frozenset(["OBJ_FLAG"])

WIDGET_SCOPED_MODULE_ENUMS = frozenset(
    [
        "IMAGE_FLAGS",
        "IMAGE_SRC",
        "IMAGE_ALIGN",
        "IMAGE_COMPRESS",
        "BAR_MODE",
        "SLIDER_MODE",
        "ARC_MODE",
        "ROLLER_MODE",
        "KEYBOARD_MODE",
        "LABEL_LONG_MODE",
        "CHART_UPDATE_MODE",
        "CHART_AXIS",
        "CHART_TYPE",
        "IMAGEBUTTON_STATE",
        "OBJ_POINT_TRANSFORM_FLAG",
        "OBJ_TREE_WALK",
        "OBJ_CLASS_EDITABLE",
        "OBJ_CLASS_GROUP_DEF",
        "OBJ_CLASS_THEME_INHERITABLE",
        "BUTTONMATRIX_CTRL",
        "TABLE_CELL_CTRL",
        "MENU_HEADER",
        "MENU_ROOT_BACK_BUTTON",
        "SCALE_MODE",
    ]
)

WIDGET_ENUM_ATTRS = {
    "obj": ["FLAG"],
    "image": ["FLAGS"],
    "label": ["LONG_MODE"],
    "bar": ["MODE"],
}


def mp_module_names(text):
    m = re.search(
        r"(?:lvgl_globals_table|lvgl_module_globals_table)\[\] = \{(.*?)\n\};",
        text,
        re.S,
    )
    if not m:
        return set()
    names = set()
    for line in m.group(1).splitlines():
        match = re.search(r"MP_ROM_QSTR\(MP_QSTR_(\w+)\)", line)
        if match:
            names.add(match.group(1))
    return names


def py_module_names(text):
    names = set(
        re.findall(
            r'PyModule_Add(?:Object|StringConstant|IntConstant)\(m,\s*"([^"]+)"',
            text,
        )
    )
    methods = re.search(r"static PyMethodDef lvgl_methods\[\] = \{(.*?)\n\};", text, re.S)
    if methods:
        names.update(re.findall(r'\{"([^"]+)"\s*,', methods.group(1)))
    return names


def mp_obj_enum_attrs(text, obj):
    m = re.search(
        rf"static const mp_rom_map_elem_t {obj}_locals_dict_table\[\] = \{{(.*?)\}};",
        text,
        re.S,
    )
    if not m:
        return set()
    attrs = set()
    for line in m.group(1).splitlines():
        if "_type_base" not in line:
            continue
        q = re.search(r"MP_ROM_QSTR\(MP_QSTR_(\w+)\)", line)
        if q:
            attrs.add(q.group(1))
    return attrs


def py_obj_enum_attrs(text, obj):
    block = re.search(r"PyInit_lvgl\(void\).*?return m;", text, re.S)
    if not block:
        return set()
    attrs = set()
    for m in re.finditer(
        rf'py_lv_{obj}_type\)->tp_dict,\s*"([^"]+)"',
        block.group(0),
    ):
        attrs.add(m.group(1))
    return attrs


def canonical_module_names(data, target):
    names = {"C_Pointer", "LvReferenceError"}
    names.update(
        item["python_name"]
        for item in data.get("functions", ())
        if item.get("visibility") == "public"
        and item.get("role") == "module"
        and target in item.get("available_on", ())
    )
    for section in ("objects", "structs", "variables", "constants"):
        names.update(
            item.get("python_name") or item.get("name")
            for item in data.get(section, ())
            if item.get("visibility") == "public"
            and target in item.get("available_on", ())
            and item.get("c_name") != "_nesting"
        )
    names.update(
        item["module_name"]
        for item in data.get("enums", ())
        if item.get("visibility") == "public"
        and target in item.get("available_on", ())
        and item.get("module_name")
    )
    return names


def verify(target, text, expected_names):
    errors = []
    names = mp_module_names(text) if target == "CircuitPython" else py_module_names(text)
    if target == "MicroPython":
        names = mp_module_names(text)
    # _nesting is deliberately private in the canonical API model (it is
    # not an LVGL declaration) yet is still emitted for MicroPython and
    # CircuitPython; see api_model.build_api_model and emit_backend's
    # module_registration_plan. Treat it like the other non-canonical but
    # expected infrastructure exports rather than flagging it as unexpected.
    integration_names = {"__name__", "__version__", "_nesting"}
    missing = expected_names - names
    unexpected = names - expected_names - integration_names
    if missing:
        errors.append("module missing exports: %s" % ", ".join(sorted(missing)))
    if unexpected:
        errors.append("module has unexpected exports: %s" % ", ".join(sorted(unexpected)))

    obj_enum_fn = mp_obj_enum_attrs if target != "CPython" else py_obj_enum_attrs
    for obj, expected in WIDGET_ENUM_ATTRS.items():
        attrs = obj_enum_fn(text, obj)
        for attr in expected:
            if attr not in attrs:
                errors.append("%s missing enum attr %s" % (obj, attr))

    return errors


def main(argv):
    generated = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parent.parent / "generated"
    files = {
        "MicroPython": generated / "lvgl_micropython.c",
        "CircuitPython": generated / "lvgl_circuitpython.c",
        "CPython": generated / "lvgl_python.c",
    }
    api = json.loads((generated / "api.json").read_text())

    failed = False
    for target, path in files.items():
        if not path.is_file():
            print("FAIL: missing %s" % path)
            failed = True
            continue
        canonical_target = target.lower()
        errors = verify(
            target,
            path.read_text(),
            canonical_module_names(api, canonical_target),
        )
        if errors:
            failed = True
            print("FAIL %s:" % target)
            for err in errors:
                print("  - %s" % err)
        else:
            print("OK: %s namespace parity" % target)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
