# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Generate the shared lvgl.pyi from the canonical API model."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional, Sequence

from .emit_pyi_canonical import CanonicalPyiEmitter, load_canonical_api

ALL_TARGETS = ("cpython", "micropython", "circuitpython")

_LV_VERSION_DEFINE_RE = re.compile(
    r"^#define\s+(LVGL_VERSION_MAJOR|LVGL_VERSION_MINOR|LVGL_VERSION_PATCH)\s+(\d+)",
    re.MULTILINE,
)


def read_lvgl_version_major_minor(repo_root: Optional[Path] = None) -> str:
    """Read the major/minor version from the pinned LVGL submodule."""

    repo_root = (repo_root or Path(__file__).resolve().parent.parent).resolve()
    for version_file in (
        repo_root / "lvgl" / "lv_version.h",
        repo_root / "lvgl" / "lvgl.h",
    ):
        if not version_file.is_file():
            continue
        text = version_file.read_text(encoding="utf-8")
        parts = {
            name: int(value)
            for name, value in _LV_VERSION_DEFINE_RE.findall(text)
        }
        if "LVGL_VERSION_MAJOR" in parts and "LVGL_VERSION_MINOR" in parts:
            return "{}.{}".format(
                parts["LVGL_VERSION_MAJOR"],
                parts["LVGL_VERSION_MINOR"],
            )
    raise FileNotFoundError(
        "could not read LVGL version from lvgl/lv_version.h under {}".format(repo_root)
    )


def default_api_path(generated_dir: Path) -> Path:
    return generated_dir.resolve() / "api.json"


def default_output_path(generated_dir: Path) -> Path:
    return generated_dir.resolve() / "lvgl.pyi"


def write_pyi(
    api_path: Path,
    output_path: Path,
    *,
    target: str = "all",
    lvgl_version: Optional[str] = None,
    repo_root: Optional[Path] = None,
) -> None:
    """Render one common or target-specific stub from ``api.json``."""

    data = load_canonical_api(api_path)
    repo_root = repo_root or api_path.resolve().parent.parent
    emitter = CanonicalPyiEmitter(
        data,
        target=target,
        lvgl_version=lvgl_version or read_lvgl_version_major_minor(repo_root),
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        emitter.emit(handle)


def generate_pyi(
    generated_dir: Path,
    *,
    api_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    api_path = api_path or default_api_path(generated_dir)
    output_path = output_path or default_output_path(generated_dir)
    if not api_path.is_file():
        raise FileNotFoundError("canonical API file not found: {}".format(api_path))
    write_pyi(api_path, output_path, target="all")
    return output_path


def generate_all_pyis(
    generated_dir: Path,
    *,
    api_path: Optional[Path] = None,
) -> list[Path]:
    return [generate_pyi(generated_dir, api_path=api_path)]


def generate_pyi_for_target(
    generated_dir: Path,
    target: str,
    *,
    api_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Path:
    api_path = api_path or default_api_path(generated_dir)
    output_path = output_path or default_output_path(generated_dir)
    if not api_path.is_file():
        raise FileNotFoundError("canonical API file not found: {}".format(api_path))
    write_pyi(api_path, output_path, target=target)
    return output_path


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate lvgl.pyi stubs from the canonical api.json."
    )
    parser.add_argument(
        "--target",
        choices=list(ALL_TARGETS) + ["all"],
        default="all",
        help="Emit the common API or one target's available symbols",
    )
    parser.add_argument(
        "--api",
        type=Path,
        help="Canonical API JSON (default: generated/api.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output .pyi path (default: generated/lvgl.pyi)",
    )
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "generated",
        help="Directory containing canonical API artifacts",
    )
    args = parser.parse_args(argv)
    api_path = args.api or default_api_path(args.generated_dir)
    output_path = args.output or default_output_path(args.generated_dir)
    write_pyi(
        api_path,
        output_path,
        target=args.target,
    )
    print("Wrote {}".format(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
