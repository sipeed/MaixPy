# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Hash and compare generated binding artifacts."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Dict, Iterable, Mapping


DEFAULT_ARTIFACTS = (
    "api.json",
    "lvgl.pp",
    "lvgl.pyi",
    "lvgl_circuitpython.c",
    "lvgl_circuitpython.h",
    "lvgl_micropython.c",
    "lvgl_python.c",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_for_directory(
    directory: Path,
    filenames: Iterable[str] = DEFAULT_ARTIFACTS,
) -> Dict[str, object]:
    """Return deterministic sizes and SHA-256 hashes for generated files."""

    directory = Path(directory)
    files: Dict[str, Dict[str, object]] = {}
    for filename in sorted(set(filenames)):
        path = directory / filename
        if not path.is_file():
            continue
        files[filename] = {
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
    return {"schema": 1, "files": files}


def compare_manifests(
    expected: Mapping[str, object], actual: Mapping[str, object]
) -> Dict[str, object]:
    """Return missing, unexpected, and changed artifact names."""

    expected_files = expected.get("files", {})
    actual_files = actual.get("files", {})
    if not isinstance(expected_files, Mapping) or not isinstance(actual_files, Mapping):
        raise ValueError("artifact manifests must contain mapping-valued files")

    expected_names = set(expected_files)
    actual_names = set(actual_files)
    changed = sorted(
        name
        for name in expected_names & actual_names
        if expected_files[name] != actual_files[name]
    )
    return {
        "missing": sorted(expected_names - actual_names),
        "unexpected": sorted(actual_names - expected_names),
        "changed": changed,
        "equal": not (
            expected_names - actual_names
            or actual_names - expected_names
            or changed
        ),
    }
