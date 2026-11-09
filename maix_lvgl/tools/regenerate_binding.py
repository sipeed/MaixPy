"""Regenerate the CPython binding from MaixCDK's LVGL source.

Called automatically by setup.py. The binding is only regenerated when the
LVGL source, MaixCDK's lv_conf.h or the bundled generator changes (tracked in
``binding/.binding_stamp.json``).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import maixcdk_lvgl as mk

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools" / "omnipython_lvgl"
BINDING_DIR = PROJECT_ROOT / "binding"
WORK_DIR = PROJECT_ROOT / ".build" / "bindgen"
STAMP_FILE = BINDING_DIR / ".binding_stamp.json"

_PRUNE_KEYS = {
    "function": ["private_functions", "unsupported_functions"],
    "enum": ["private_enums"],
    "struct": ["private_structs"],
    "variable": ["private_variables"],
}


def adjust_lv_conf(text: str) -> str:
    """Adapt MaixCDK's lv_conf.h for a single-threaded CPython binding."""
    text = text.replace('#include "global_config.h"\n', "")
    text = re.sub(r"extern bool lv_ui_mutex_lock\(int timeout\);\n?", "", text)
    text = re.sub(r"extern void lv_ui_mutex_unlock\(\);\n?", "", text)
    # Keep LV_USE_OS / LV_USE_RLOTTIE as MaixCDK configures them: the binding
    # links against the LVGL library that MaixCDK's lvgl component builds, so
    # both sides must agree on struct layouts (pthread mutex fields, rlottie).
    return text



def _hide_pthread_structs(policy_path: Path) -> None:
    """Hide structs whose pthread fields cannot be represented in Python."""
    data = json.loads(policy_path.read_text(encoding="utf-8"))
    existing = {item.get("name") for item in data.get("private_structs", [])}
    changed = False
    for name in ("lv_thread_sync_t", "lv_draw_global_info_t"):
        if name not in existing:
            data.setdefault("private_structs", []).append(
                {
                    "name": name,
                    "reason": (
                        "Contains pthread_mutex_t/cond fields, which have no "
                        "Python representation; the binding links against the "
                        "LVGL library built by MaixCDK (LV_USE_OS=PTHREAD)."
                    ),
                    "test": "tools/regenerate_binding.py::_hide_pthread_structs",
                }
            )
            changed = True
    if changed:
        policy_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")



def _patch_generated_c(path: Path) -> None:
    """Drop getattro/setattro branches for pthread-typed struct fields."""
    text = path.read_text(encoding="utf-8")
    functions = (
        "py_lv_thread_sync_t_getattro",
        "py_lv_thread_sync_t_setattro",
        "py_lv_draw_global_info_t_getattro",
        "py_lv_draw_global_info_t_setattro",
        "py_lv_cache_t_getattro",
        "py_lv_cache_t_setattro",
    )
    for func in functions:
        start = text.find(func + "(")
        if start < 0:
            continue
        end = text.find("\n}\n", start)
        if end < 0:
            continue
        block = text[start:end]
        block = re.sub(
            r'^\s*if \(strcmp\(attr, "(?:mutex|cond|circle_cache_mutex|lock)"\) == 0\).*$\n',
            "",
            block,
            flags=re.M,
        )
        text = text[:start] + block + text[end:]
    # Field name lists: remove the pthread-typed names.
    text = re.sub(
        r'(py_lv_thread_sync_t_field_names\[\] = \{)[^}]*?(\};)',
        r'\1NULL\2',
        text,
        flags=re.S,
    )
    text = re.sub(
        r'(py_lv_draw_global_info_t_field_names\[\] = \{[^}]*?)"circle_cache_mutex",\s*',
        r'\1',
        text,
    )
    text = re.sub(
        r'(py_lv_cache_t_field_names\[\] = \{[^}]*?)"lock",\s*',
        r'\1',
        text,
    )
    path.write_text(text, encoding="utf-8")


def _prune_policy(policy_path: Path, missing: str) -> int:
    keymap = _PRUNE_KEYS
    data = json.loads(policy_path.read_text(encoding="utf-8"))
    entries = re.findall(r"(enum|function|struct|variable) ([A-Za-z0-9_]+)", missing)
    removed = 0
    for kind, name in entries:
        for key in keymap[kind]:
            items = data.get(key, [])
            before = len(items)
            data[key] = [item for item in items if item.get("name") != name]
            removed += before - len(data[key])
    policy_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return removed


def _run_generator(work: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(work)
    for attempt in range(40):
        proc = subprocess.run(
            [sys.executable, "-m", "binding.generate", "--target", "cpython"],
            cwd=work,
            env=env,
            capture_output=True,
            text=True,
        )
        out = proc.stdout + proc.stderr
        if proc.returncode == 0:
            return
        # Match the exception line, not the traceback's source line that also
        # contains "API policy names missing declarations: %s".
        matches = re.findall(
            r"ValueError: API policy names missing declarations: (.*)", out
        )
        if not matches:
            raise RuntimeError(
                "omnipython-lvgl binding generation failed:\n" + out[-6000:]
            )
        removed = _prune_policy(work / "binding" / "api_policy.json", matches[-1])
        print(
            f"  binding policy: pruned {removed} entries (round {attempt + 1})",
            flush=True,
        )
    raise RuntimeError("binding generation did not converge after 40 prune rounds")


def _generate(lvgl_dir: Path, conf: Path, inputs: dict, log=print) -> None:
    try:
        import pycparser  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "pycparser is required to regenerate the LVGL binding. "
            "Install it with: python3 -m pip install 'pycparser>=3.0'"
        ) from exc

    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    shutil.copytree(TOOLS_DIR / "binding", WORK_DIR / "binding")
    shutil.copytree(TOOLS_DIR / "fake_libc_include", WORK_DIR / "fake_libc_include")
    # Copy rather than symlink: lv_conf_internal.h includes "../../lv_conf.h"
    # relative to lvgl/src, so the LVGL tree must physically sit next to the
    # adjusted lv_conf.h inside the work directory.
    shutil.copytree(lvgl_dir, WORK_DIR / "lvgl")

    adjusted = adjust_lv_conf(conf.read_text(encoding="utf-8"))
    (WORK_DIR / "lv_conf.h").write_text(adjusted, encoding="utf-8")
    _hide_pthread_structs(WORK_DIR / "binding" / "api_policy.json")

    log("generating CPython binding from MaixCDK's LVGL sources ...")
    _run_generator(WORK_DIR)
    _patch_generated_c(WORK_DIR / "generated" / "lvgl_python.c")

    BINDING_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(WORK_DIR / "generated" / "lvgl_python.c", BINDING_DIR / "lvgl_python.c")
    shutil.copy2(WORK_DIR / "generated" / "lvgl.pyi", BINDING_DIR / "lvgl.pyi")
    shutil.copy2(WORK_DIR / "lv_conf.h", BINDING_DIR / "lv_conf.h")
    STAMP_FILE.write_text(json.dumps(inputs, indent=2) + "\n", encoding="utf-8")
    log("binding updated: binding/lvgl_python.c")


def ensure_binding(force: bool = False, log=print, sdk_path=None):
    """Return (lvgl_source_dir, lv_conf_for_build), regenerating if stale."""
    sdk = Path(sdk_path).resolve() if sdk_path else mk.find_maixcdk()
    version = mk.lvgl_version(sdk)
    lvgl_dir = mk.ensure_lvgl_source(sdk, version, log)
    conf = mk.lv_conf_path(sdk)
    inputs = mk.stamp(sdk, version, lvgl_dir, conf)

    current = None
    if STAMP_FILE.is_file() and (BINDING_DIR / "lvgl_python.c").is_file():
        try:
            current = json.loads(STAMP_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            current = None

    if not force and current == inputs:
        log(f"binding is up to date (LVGL {version})")
        return lvgl_dir, BINDING_DIR / "lv_conf.h"

    _generate(lvgl_dir, conf, inputs, log)
    return lvgl_dir, BINDING_DIR / "lv_conf.h"


if __name__ == "__main__":
    force = "--force" in sys.argv
    sdk_path = None
    if "--sdk-path" in sys.argv:
        index = sys.argv.index("--sdk-path")
        if index + 1 < len(sys.argv):
            sdk_path = sys.argv[index + 1]
    ensure_binding(force=force, sdk_path=sdk_path)
