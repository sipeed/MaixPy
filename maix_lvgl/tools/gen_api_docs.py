#!/usr/bin/env python3
"""Generate MaixPy-style Markdown API docs from binding/lvgl.pyi.

The output mirrors MaixPy's docs/api structure:

    docs/api/
    ├── api.json
    ├── config.json
    ├── README.md
    ├── README2.md
    ├── sidebar.yaml
    └── maix_lvgl/
        ├── lvgl.md
        └── maix_lvgl.md

The module pages use the same Section/table/code-block layout as MaixPy's
MaixCDK doc_tool output (Module / Enum / Variable / Function / Class).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE = "maix_lvgl"


@dataclass
class Method:
    name: str
    signature: str
    args: list[tuple[str, str, str | None]] = field(default_factory=list)
    ret: str = ""


@dataclass
class Field:
    name: str
    type: str


@dataclass
class Class:
    name: str
    bases: list[str] = field(default_factory=list)
    methods: list[Method] = field(default_factory=list)
    fields: list[Field] = field(default_factory=list)
    nested: list["Class"] = field(default_factory=list)


def _strip_trailer(text: str) -> str:
    text = re.sub(r"\s*:\s*\.\.\.\s*$", "", text.strip())
    return re.sub(r"\s+", " ", text)


def _logical_lines(text: str) -> list[str]:
    lines: list[str] = []
    buf = ""
    for raw in text.splitlines():
        line = raw.rstrip()
        buf = line if not buf else buf + " " + line.strip()
        stripped = buf.lstrip()
        if stripped.startswith(("def ", "class ")) and buf.count("(") > buf.count(")"):
            continue
        lines.append(buf)
        buf = ""
    if buf:
        lines.append(buf)
    return lines


def _split_args(text: str) -> list[str]:
    parts: list[str] = []
    depth = 0
    current = ""
    for ch in text:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())
    return parts


def parse_signature(signature: str):
    text = signature.strip()
    if text.startswith("def "):
        text = text[4:]
    name, rest = text.split("(", 1)
    depth = 1
    index = 0
    while index < len(rest):
        if rest[index] == "(":
            depth += 1
        elif rest[index] == ")":
            depth -= 1
            if depth == 0:
                break
        index += 1
    args_text = rest[:index]
    tail = rest[index + 1 :].strip()
    ret = ""
    if tail.startswith("->"):
        ret = tail[2:].strip().rstrip(":").strip()
    args: list[tuple[str, str, str | None]] = []
    for part in _split_args(args_text):
        if part in ("/", "*") or part.startswith("**"):
            continue
        if part.startswith("*"):
            part = part[1:]
        if not part:
            continue
        if ":" in part:
            arg_name, arg_type = part.split(":", 1)
            arg_name, arg_type = arg_name.strip(), arg_type.strip()
        else:
            arg_name, arg_type = part, ""
        default = None
        if "=" in arg_type:
            arg_type, default = arg_type.split("=", 1)
            arg_type, default = arg_type.strip(), default.strip()
        if arg_name in ("self", "cls"):
            continue
        args.append((arg_type, arg_name, default))
    return name.strip(), args, ret


def parse_pyi(text: str):
    classes: list[Class] = []
    functions: list[Method] = []
    variables: list[Field] = []
    current: Class | None = None
    nested: Class | None = None

    for line in _logical_lines(text):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "from ", "import ")):
            continue
        indent = len(line) - len(line.lstrip())
        class_match = re.match(r"class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:", stripped)
        def_match = re.match(r"def\s+(\w+)\s*\((.*)\)\s*(?:->\s*(.*?))?\s*:\s*\.\.\.", stripped)
        field_match = re.match(r"(\w+)\s*:\s*(.+)", stripped)

        if indent == 0:
            nested = None
            if class_match:
                bases = [b.strip() for b in (class_match.group(2) or "").split(",") if b.strip()]
                current = Class(class_match.group(1), bases)
                classes.append(current)
                continue
            if def_match:
                name, args, ret = parse_signature(_strip_trailer(stripped))
                functions.append(Method(name, _strip_trailer(stripped), args, ret))
                current = None
                continue
            if field_match:
                variables.append(Field(field_match.group(1), _strip_trailer(field_match.group(2))))
            continue

        if current is None:
            continue
        if indent == 4:
            if class_match:
                bases = [b.strip() for b in (class_match.group(2) or "").split(",") if b.strip()]
                nested = Class(class_match.group(1), bases)
                current.nested.append(nested)
                continue
            nested = None
            if def_match:
                name, args, ret = parse_signature(_strip_trailer(stripped))
                current.methods.append(Method(name, _strip_trailer(stripped), args, ret))
                continue
            if field_match:
                current.fields.append(Field(field_match.group(1), _strip_trailer(field_match.group(2))))
            continue

        target = nested if nested is not None else current
        if def_match:
            name, args, ret = parse_signature(_strip_trailer(stripped))
            target.methods.append(Method(name, _strip_trailer(stripped), args, ret))
        elif field_match:
            target.fields.append(Field(field_match.group(1), _strip_trailer(field_match.group(2))))

    return classes, functions, variables


def classify(cls: Class) -> str:
    name = cls.name
    bases = " ".join(cls.bases)
    if "Exception" in bases or name == "_Struct" or (name.startswith("_") and name not in ("_Struct",)):
        return "skip"
    if (
        cls.fields
        and not cls.methods
        and not cls.nested
        and all(re.fullmatch(r"(ClassVar\[)?int(\])?", f.type.strip()) for f in cls.fields)
    ):
        return "enum"
    return "class"


# ---------------------------------------------------------------------------
# api.json model (subset of MaixPy's api tree shape)
# ---------------------------------------------------------------------------
def _doc_for_method(method: Method) -> dict:
    doc: dict = {"brief": ""}
    params = []
    for arg_type, arg_name, default in method.args:
        text = f"{arg_name}: {arg_type}"
        if default is not None:
            text += f", default {default}"
        params.append(text)
    if params:
        doc["param"] = params
    if method.ret and method.ret not in ("None", "NoneType"):
        doc["return"] = method.ret
    return doc


def _c_def(method: Method, with_self: bool = False) -> str:
    ret = method.ret or "void"
    args = []
    if with_self:
        args.append("self")
    for arg_type, arg_name, _default in method.args:
        args.append(f"{arg_type} {arg_name}".strip() if arg_type else arg_name)
    return f"{ret} {method.name}({', '.join(args)})"


def _py_def(method: Method) -> str:
    args = []
    for arg_type, arg_name, default in method.args:
        text = f"{arg_name}: {arg_type}" if arg_type else arg_name
        if default is not None:
            text += f" = {default}"
        args.append(text)
    ret = f" -> {method.ret}" if method.ret else ""
    return f"def {method.name}({', '.join(args)}){ret}"


def _method_item(method: Method, full_name: str) -> dict:
    return {
        "type": "func",
        "name": method.name,
        "doc": {**_doc_for_method(method), "maixpy": full_name},
        "args": [[a[0], a[1], a[2]] for a in method.args],
        "ret_type": method.ret,
        "static": False,
        "def": _c_def(method),
        "py_def": _py_def(method),
    }


def _class_item(cls: Class, full_name: str) -> dict:
    members = {}
    for method in cls.methods:
        members[method.name] = _method_item(method, f"{full_name}.{method.name}")
    for fld in cls.fields:
        members[fld.name] = {
            "type": "var",
            "name": fld.name,
            "doc": {"brief": f"{cls.name} field", "maixpy": f"{full_name}.{fld.name}"},
            "value": fld.type,
            "static": False,
            "readonly": False,
            "def": f"{fld.type} {fld.name}",
        }
    item = {
        "type": "class",
        "name": cls.name,
        "doc": {"brief": "", "maixpy": full_name},
        "def": f"class {cls.name}" + (f"({', '.join(cls.bases)})" if cls.bases else ""),
        "members": members,
    }
    if cls.nested:
        item["nested"] = [
            {
                "type": "enum",
                "name": nested.name,
                "doc": {"brief": "", "maixpy": f"{full_name}.{nested.name}"},
                "values": [[f.name, None, "int"] for f in nested.fields],
                "def": f"enum {nested.name}",
            }
            for nested in cls.nested
        ]
    return item


def build_modules(classes, functions, variables) -> dict:
    lvgl_members: dict = {}
    for func in sorted(functions, key=lambda m: m.name):
        lvgl_members[func.name] = _method_item(func, f"{MODULE}.lvgl.{func.name}")
    for var in sorted(variables, key=lambda f: f.name):
        lvgl_members[var.name] = {
            "type": "var",
            "name": var.name,
            "doc": {"brief": "", "maixpy": f"{MODULE}.lvgl.{var.name}"},
            "value": var.type,
            "static": False,
            "readonly": False,
            "def": f"{var.type} {var.name}",
        }
    for cls in sorted(classes, key=lambda c: c.name):
        if classify(cls) == "enum":
            lvgl_members[cls.name] = {
                "type": "enum",
                "name": cls.name,
                "doc": {"brief": "", "maixpy": f"{MODULE}.lvgl.{cls.name}"},
                "values": [[f.name, None, "int"] for f in cls.fields],
                "def": f"enum class {cls.name}",
            }
        elif classify(cls) == "class":
            lvgl_members[cls.name] = _class_item(cls, f"{MODULE}.lvgl.{cls.name}")

    backend = {
        "type": "module",
        "doc": {"brief": "maix_lvgl backend: bind MaixPy display/touchscreen to LVGL"},
        "members": {
            "init": {
                "type": "func",
                "name": "init",
                "doc": {
                    "brief": "Initialize LVGL and bind MaixPy display/touchscreen.",
                    "param": [
                        "display: maix.display.Display, opened internally when omitted",
                        "touchscreen: maix.touchscreen.TouchScreen, pass False to disable input",
                        "width: display width when opening internally",
                        "height: display height when opening internally",
                    ],
                    "maixpy": "maix_lvgl.init",
                },
                "args": [["Display | None", "display", "None"], ["TouchScreen | bool | None", "touchscreen", "None"], ["int | None", "width", "None"], ["int | None", "height", "None"]],
                "ret_type": "DisplayDriver",
                "static": False,
                "def": "DisplayDriver init(Display * display, TouchScreen * touchscreen, int width, int height)",
                "py_def": "def init(display=None, touchscreen=None, width=None, height=None)",
            },
            "deinit": {
                "type": "func",
                "name": "deinit",
                "doc": {"brief": "Stop LVGL and release resources opened by init().", "maixpy": "maix_lvgl.deinit"},
                "args": [],
                "ret_type": "None",
                "static": False,
                "def": "void deinit()",
                "py_def": "def deinit()",
            },
            "timer_handler": {
                "type": "func",
                "name": "timer_handler",
                "doc": {
                    "brief": "Advance the LVGL tick and run one timer-handler pass.",
                    "maixpy": "maix_lvgl.timer_handler",
                },
                "args": [],
                "ret_type": "int",
                "static": False,
                "def": "int timer_handler()",
                "py_def": "def timer_handler()",
            },
            "process": {
                "type": "func",
                "name": "process",
                "doc": {"brief": "Alias of timer_handler().", "maixpy": "maix_lvgl.process"},
                "args": [],
                "ret_type": "int",
                "static": False,
                "def": "int process()",
                "py_def": "def process()",
            },
            "run": {
                "type": "func",
                "name": "run",
                "doc": {
                    "brief": "Run the LVGL loop until maix.app.need_exit() becomes true.",
                    "maixpy": "maix_lvgl.run",
                },
                "args": [["int", "fps", "60"]],
                "ret_type": "None",
                "static": False,
                "def": "void run(int fps)",
                "py_def": "def run(fps=60)",
            },
            "DisplayDriver": {
                "type": "class",
                "name": "DisplayDriver",
                "doc": {"brief": "Wrap a maix.display.Display and push LVGL frames to it.", "maixpy": "maix_lvgl.DisplayDriver"},
                "def": "class DisplayDriver",
                "members": {
                    "__init__": {
                        "type": "func",
                        "name": "__init__",
                        "doc": {"brief": "Create the LVGL display and its flush callback.", "maixpy": "maix_lvgl.DisplayDriver.__init__"},
                        "args": [["Display | None", "display", "None"], ["int | None", "width", "None"], ["int | None", "height", "None"]],
                        "ret_type": "None",
                        "static": False,
                        "def": "DisplayDriver(Display * display, int width, int height)",
                        "py_def": "def __init__(display=None, width=None, height=None)",
                    },
                    "deinit": {
                        "type": "func",
                        "name": "deinit",
                        "doc": {"brief": "Delete the LVGL display and close an internally opened display.", "maixpy": "maix_lvgl.DisplayDriver.deinit"},
                        "args": [],
                        "ret_type": "None",
                        "static": False,
                        "def": "void deinit()",
                        "py_def": "def deinit()",
                    },
                },
            },
            "TouchDriver": {
                "type": "class",
                "name": "TouchDriver",
                "doc": {"brief": "Feed maix.touchscreen.TouchScreen input into an LVGL pointer indev.", "maixpy": "maix_lvgl.TouchDriver"},
                "def": "class TouchDriver",
                "members": {
                    "__init__": {
                        "type": "func",
                        "name": "__init__",
                        "doc": {"brief": "Create the LVGL pointer indev.", "maixpy": "maix_lvgl.TouchDriver.__init__"},
                        "args": [["TouchScreen | None", "touchscreen", "None"], ["display_t | None", "display", "None"]],
                        "ret_type": "None",
                        "static": False,
                        "def": "TouchDriver(TouchScreen * touchscreen, display_t * display)",
                        "py_def": "def __init__(touchscreen=None, display=None)",
                    },
                    "deinit": {
                        "type": "func",
                        "name": "deinit",
                        "doc": {"brief": "Delete the LVGL indev and close an internally opened touchscreen.", "maixpy": "maix_lvgl.TouchDriver.deinit"},
                        "args": [],
                        "ret_type": "None",
                        "static": False,
                        "def": "void deinit()",
                        "py_def": "def deinit()",
                    },
                },
            },
        },
    }

    return {
        "type": "root",
        "members": {
            MODULE: {
                "type": "module",
                "doc": {
                    "brief": "LVGL 9.1.0 bindings for MaixPy on MaixCAM2 (MaixCDK project)",
                },
                "members": {
                    "lvgl": {
                        "type": "module",
                        "doc": {
                            "brief": "LVGL 9.1.0 CPython bindings, generated from MaixCDK's LVGL source with omnipython-lvgl",
                        },
                        "members": lvgl_members,
                    },
                    "maix_lvgl": backend,
                },
            }
        },
    }


# ---------------------------------------------------------------------------
# Markdown rendering (MaixPy doc_tool/gen_markdown.py layout)
# ---------------------------------------------------------------------------
def _escape(name: str) -> str:
    return name.replace("_", r"\_")


def _prefix(text: str, prefix: str = "> ") -> str:
    return "\n".join(prefix + line for line in text.splitlines())


def _doc_table(doc: dict) -> str:
    skip = {"maixpy", "maixcdk", "py_doc", "brief"}
    content = ""
    for key, value in doc.items():
        if key in skip:
            continue
        if isinstance(value, list):
            content += f"| **{key}** | "
            for index, item in enumerate(value):
                content += f"**{index + 1}**. {item.replace(chr(10), '<br>')}<br>"
            content += "|\n"
        elif isinstance(value, dict):
            content += f"| **{key}** | "
            for k, v in value.items():
                content += f"**{k}**: {str(v).replace(chr(10), '<br>')}<br>"
            content += "|\n"
        else:
            content += f"| **{key}** | {str(value).replace(chr(10), '<br>')} |\n"
    return content


def _has_doc_kv(doc: dict) -> bool:
    skip = {"maixpy", "maixcdk", "py_doc", "brief"}
    return any(key not in skip for key in doc)


class _Ids:
    def __init__(self):
        self.ids = {}

    def update(self, heading: str, name: str, anchor: str | None = None) -> str:
        anchor = anchor or name
        key = anchor.lower()
        if key not in self.ids:
            self.ids[key] = {"count": 1}
            return f"{heading} {_escape(name)} {{#{anchor}}}"
        self.ids[key]["count"] += 1
        return f"{heading} {_escape(name)} {{#{anchor}-{self.ids[key]['count']}}}"


def module_to_md(full_name: str, module: dict, start_comment: str, subpages=None) -> str:
    brief = module["doc"] if isinstance(module["doc"], str) else module["doc"].get("brief", "")
    content = f"---\ntitle: {full_name}\n---\n\n{brief}\n\n"
    content += start_comment
    ids = _Ids()

    def func_block(heading: str, name: str, item: dict) -> str:
        block = ids.update(heading, name) + "\n\n"
        block += item["doc"].get("brief", "") + "\n\n"
        if _has_doc_kv(item["doc"]):
            block += "| item | description |\n"
            block += "| --- | --- |\n"
            block += _doc_table(item["doc"])
        block += "\n> C++ defination code:\n> ```cpp\n{}\n> ```\n".format(
            _prefix(item.get("def", ""))
        )
        return block

    # Module
    content += ids.update("##", "Module") + "\n\n"
    if subpages:
        content += "| page | brief |\n| --- | --- |\n"
        for label, filename, brief in subpages:
            content += f"| [{label}]({filename}) | {brief} |\n"
    else:
        submodules = [
            (key, item)
            for key, item in module["members"].items()
            if item["type"] == "module"
        ]
        if submodules:
            content += "| module | brief |\n| --- | --- |\n"
            for key, item in submodules:
                content += f"| [{_escape(key)}](./{key}.md) | {item['doc'].get('brief', '')} |\n"
        else:
            content += "No module\n"
    content += "\n\n"

    # Enum
    content += ids.update("##", "Enum") + "\n\n"
    for key, item in module["members"].items():
        if item["type"] != "enum":
            continue
        content += ids.update("###", key) + "\n\n"
        content += item["doc"].get("brief", "") + "\n\n"
        content += "| item | describe |\n| --- | --- |\n"
        content += _doc_table(item["doc"])
        content += "| **values** | |\n| --- | --- |\n"
        for value in item["values"]:
            content += f"| **{value[0]}** | {value[2]} |\n"
        content += "\n> C++ defination code:\n> ```cpp\n{}\n> ```\n".format(
            _prefix(item.get("def", ""))
        )
    content += "\n\n"

    # Variable
    content += ids.update("##", "Variable") + "\n\n"
    for key, item in module["members"].items():
        if item["type"] != "var":
            continue
        content += ids.update("###", key) + "\n\n"
        content += item["doc"].get("brief", "") + "\n\n"
        content += "| item | description |\n| --- | --- |\n"
        content += _doc_table(item["doc"])
        if item.get("value"):
            content += f"| **value** | **{item['value']}** |\n"
        content += f"| **readonly**| {item.get('readonly', False)} |\n"
        content += "\n> C++ defination code:\n> ```cpp\n{}\n> ```\n".format(
            _prefix(item.get("def", ""))
        )
    content += "\n\n"

    # Function
    content += ids.update("##", "Function") + "\n\n"
    for key, item in module["members"].items():
        if item["type"] != "func":
            continue
        content += func_block("###", key, item)
    content += "\n\n"

    # Class
    content += ids.update("##", "Class") + "\n\n"
    for key, item in module["members"].items():
        if item["type"] != "class":
            continue
        content += ids.update("###", key) + "\n\n"
        content += item["doc"].get("brief", "") + "\n\n"
        if _has_doc_kv(item["doc"]):
            content += "| item | description |\n| --- | --- |\n"
            content += _doc_table(item["doc"])
        content += "\n> C++ defination code:\n> ```cpp\n{}\n> ```\n\n".format(
            _prefix(item.get("def", ""))
        )
        members = item.get("members", {})
        if members:
            content += "\n**Members**\n\n"
            for member_key, member in members.items():
                if member["type"] == "func":
                    content += f"- `{_escape(member_key)}` — `{member.get('def', '')}`\n"
                else:
                    content += f"- `{_escape(member_key)}`: `{member.get('value', '')}`\n"
            content += "\n"
        for nested in item.get("nested", []):
            content += ids.update("####", f"enum {nested['name']}", f"enum-{nested['name']}") + "\n\n"
            content += "| item | describe |\n| --- | --- |\n"
            content += "| **values** | |\n| --- | --- |\n"
            for value in nested["values"]:
                content += f"| **{value[0]}** | {value[2]} |\n"
            content += "\n"
    return content


def _start_comment(full_name: str) -> str:
    return (
        f"\n> You can use `{full_name}` to access this module with maix_lvgl\n"
        "> This module is generated from [MaixCDK](https://github.com/sipeed/MaixCDK) "
        "and [omnipython-lvgl](https://github.com/PyDevices/omnipython-lvgl)\n\n"
    )


def generate(pyi_path: Path, out_dir: Path, merge: bool = False) -> None:
    classes, functions, variables = parse_pyi(pyi_path.read_text(encoding="utf-8"))
    api_tree = build_modules(classes, functions, variables)

    out_dir.mkdir(parents=True, exist_ok=True)
    module_dir = out_dir / MODULE
    if module_dir.exists():
        shutil.rmtree(module_dir)
    module_dir.mkdir(parents=True)
    if not merge:
        for name in ("api.json", "config.json", "README.md", "README2.md", "sidebar.yaml"):
            (out_dir / name).unlink(missing_ok=True)

    # api.json
    api_path = out_dir / "api.json"
    if merge and api_path.is_file():
        try:
            existing = json.loads(api_path.read_text(encoding="utf-8"))
            existing.setdefault("members", {})[MODULE] = api_tree["members"][MODULE]
            api_path.write_text(
                json.dumps(existing, indent=4, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        except (OSError, json.JSONDecodeError):
            api_path.write_text(
                json.dumps(api_tree, indent=4, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    else:
        api_path.write_text(
            json.dumps(api_tree, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # config.json (MaixPy's own is kept in merge mode)
    config_path = out_dir / "config.json"
    if not config_path.is_file():
        config_path.write_text(
            json.dumps({"import": "config_en", "name": "maix_lvgl API Reference"}, indent=4) + "\n",
            encoding="utf-8",
        )

    # Module pages: split the large lvgl module into overview/functions/classes
    root = api_tree["members"][MODULE]
    lvgl = root["members"]["lvgl"]

    def subset(*types):
        return {k: v for k, v in lvgl["members"].items() if v["type"] in types}

    overview_subpages = [
        ("functions", "lvgl_functions.md", "Function reference"),
        ("classes", "lvgl_classes.md", "Class reference"),
    ]
    functions_subpages = [
        ("lvgl", "lvgl.md", "Module overview, enums and variables"),
        ("classes", "lvgl_classes.md", "Class reference"),
    ]
    classes_subpages = [
        ("lvgl", "lvgl.md", "Module overview, enums and variables"),
        ("functions", "lvgl_functions.md", "Function reference"),
    ]
    pages = [
        ("lvgl.md", "maix_lvgl.lvgl", {**lvgl, "members": subset("enum", "var")}, overview_subpages),
        ("lvgl_functions.md", "maix_lvgl.lvgl.functions", {**lvgl, "members": subset("func")}, functions_subpages),
        ("lvgl_classes.md", "maix_lvgl.lvgl.classes", {**lvgl, "members": subset("class")}, classes_subpages),
    ]
    for filename, full_name, module, subpages in pages:
        content = module_to_md(full_name, module, _start_comment(full_name), subpages)
        (module_dir / filename).write_text(content, encoding="utf-8")

    backend = root["members"]["maix_lvgl"]
    backend_name = f"{MODULE}.maix_lvgl"
    content = module_to_md(
        backend_name, backend, _start_comment(backend_name)
    )
    (module_dir / "maix_lvgl.md").write_text(content, encoding="utf-8")

    # README (Brief)
    readme = (
        "---\n"
        "title: maix_lvgl API -- LVGL bindings for MaixPy on MaixCAM2\n"
        "---\n\n"
        "**API documentation for maix_lvgl (LVGL 9.1.0 bindings for MaixPy).**\n\n"
        "If you want to **preview API doc offline**:\n"
        "1. Download the wheel from the [Releases page](https://github.com/Taoxuan-168/Maix_LVGL/releases).\n"
        "2. Build maix_lvgl; the API doc is generated in the `maix_lvgl/docs/api/` directory.\n\n"
        "> For maix_lvgl developer: This API documentation is generated from "
        "`binding/lvgl.pyi`, DO NOT edit this file manually!\n\n"
        "maix_lvgl API documentation, modules:\n\n"
        "| module | brief |\n"
        "| --- | --- |\n"
    )
    for name, module in root["members"].items():
        readme += f"|[maix_lvgl.{name}](./{MODULE}/{name}.md) | {module['doc'].get('brief', '')} |\n"
    readme_path = out_dir / "README.md"
    if merge and readme_path.is_file():
        existing = readme_path.read_text(encoding="utf-8")
        if not existing.endswith("\n"):
            existing += "\n"
        rows = [
            ("maix_lvgl.lvgl", f"./{MODULE}/lvgl.md",
             "Module overview, enums and variables"),
            ("maix_lvgl.lvgl.functions", f"./{MODULE}/lvgl_functions.md",
             "LVGL module functions"),
            ("maix_lvgl.lvgl.classes", f"./{MODULE}/lvgl_classes.md",
             "LVGL widget and struct classes"),
            ("maix_lvgl.maix_lvgl", f"./{MODULE}/maix_lvgl.md",
             "maix_lvgl backend: display/touchscreen, init/deinit/run"),
        ]
        for key, path, brief in rows:
            if key not in existing:
                existing += f"|[{key}]({path}) | {brief} |\n"
        readme_path.write_text(existing, encoding="utf-8")
    else:
        readme_path.write_text(readme, encoding="utf-8")

    # README2 (offline note; keep MaixPy's in merge mode)
    readme2_path = out_dir / "README2.md"
    if not (merge and readme2_path.is_file()):
        readme2_path.write_text(
            "Where is the API docs?\n"
            "=====\n\n"
            "API docs is generated from `binding/lvgl.pyi` during the build and can be\n"
            "read locally in `maix_lvgl/docs/api/`.\n\n"
            "If you want to preview API doc offline, there are two ways:\n"
            "1. Download the wheel from the [Releases page](https://github.com/Taoxuan-168/Maix_LVGL/releases).\n"
            "2. Build maix_lvgl project; API doc is generated in `maix_lvgl/docs/api/`.\n",
            encoding="utf-8",
        )

    # sidebar.yaml
    sidebar = (
        "items:\n"
        "-   file: README.md\n"
        "    label: Brief\n"
        "-   collapsed: false\n"
        "    items:\n"
    )
    for name in root["members"]:
        sidebar += (
            "    -   collapsed: false\n"
            f"        file: {MODULE}/{name}.md\n"
            f"        label: {name}\n"
        )
    sidebar += "    label: maix_lvgl\n"
    sidebar_path = out_dir / "sidebar.yaml"
    if merge and sidebar_path.is_file():
        existing = sidebar_path.read_text(encoding="utf-8")
        if "maix_lvgl/" not in existing:
            if not existing.endswith("\n"):
                existing += "\n"
            existing += (
                "-   collapsed: false\n"
                "    items:\n"
                "    -   collapsed: false\n"
                f"        file: {MODULE}/lvgl.md\n"
                "        label: lvgl\n"
                "    -   collapsed: false\n"
                f"        file: {MODULE}/maix_lvgl.md\n"
                "        label: maix_lvgl\n"
                "    label: maix_lvgl\n"
            )
            sidebar_path.write_text(existing, encoding="utf-8")
    else:
        sidebar_path.write_text(sidebar, encoding="utf-8")

    print(
        f"API docs: {out_dir} (modules {len(root['members'])}, "
        f"functions {len(functions)}, variables {len(variables)}, "
        f"classes {sum(1 for c in classes if classify(c) == 'class')}, "
        f"enums {sum(1 for c in classes if classify(c) == 'enum')})"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pyi", default=str(ROOT / "binding" / "lvgl.pyi"))
    parser.add_argument("--out", default=str(ROOT / "docs" / "api"))
    parser.add_argument("--merge", action="store_true", help="merge into an existing MaixPy docs/api")
    args = parser.parse_args()
    generate(Path(args.pyi), Path(args.out), merge=args.merge)


if __name__ == "__main__":
    main()
