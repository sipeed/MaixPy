"""Locate MaixCDK, its pinned LVGL source/configuration and cross toolchain.

The project intentionally does not vendor LVGL. The build uses the LVGL source
and configuration that MaixCDK already manages under
``<maixcdk>/dl/extracted/lvgl_srcs/lvgl`` (downloaded from the version pinned
by ``components/3rd_party/lvgl/Kconfig``), so upgrading LVGL in MaixCDK makes
the next build pick it up automatically.
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import tarfile
import tempfile
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LVGL_COMPONENT = Path("components/3rd_party/lvgl")

# The generator artifacts bundled in tools/omnipython_lvgl.
GENERATOR_VERSION_FILE = PROJECT_ROOT / "tools" / "omnipython_lvgl" / "VERSION"


def find_maixcdk() -> Path:
    """Return the MaixCDK root, from MAIXCDK_PATH or the usual neighbors."""
    candidates = []
    env = os.environ.get("MAIXCDK_PATH")
    if env:
        candidates.append(Path(env))
    candidates.extend(
        [
            PROJECT_ROOT.parent / "MaixCDK",
            PROJECT_ROOT.parent.parent / "MaixCDK",
            Path.home() / "MaixCDK",
        ]
    )
    for candidate in candidates:
        if (candidate / LVGL_COMPONENT / "component.py").is_file():
            return candidate.resolve()
    raise RuntimeError(
        "MaixCDK not found. Set MAIXCDK_PATH to the MaixCDK checkout "
        "(e.g. export MAIXCDK_PATH=/path/to/MaixCDK)."
    )


def lvgl_version(sdk: Path) -> str:
    """Read the LVGL version pinned by MaixCDK's lvgl Kconfig defaults."""
    text = (sdk / LVGL_COMPONENT / "Kconfig").read_text(encoding="utf-8")

    def default(name: str, fallback: int) -> int:
        match = re.search(
            rf"config\s+{name}\b[\s\S]{{0,200}}?default\s+(\d+)", text
        )
        return int(match.group(1)) if match else fallback

    return "{}.{}.{}".format(
        default("LVGL_VERSION_MAJOR", 9),
        default("LVGL_VERSION_MINOR", 1),
        default("LVGL_VERSION_PATCH", 0),
    )


def _download_info(sdk: Path) -> dict:
    """Extract the version -> sha256 map from MaixCDK's lvgl component.py."""
    text = (sdk / LVGL_COMPONENT / "component.py").read_text(encoding="utf-8")
    return {
        version: sha
        for version, sha in re.findall(
            r'if\s+version\s*==\s*"([^"]+)"\s*:\s*\n\s*sha256sum\s*=\s*"([0-9a-f]{64})"',
            text,
        )
    }


def lvgl_source_dir(sdk: Path) -> Path:
    """Path MaixCDK uses for extracted LVGL sources (contains lvgl.h)."""
    return sdk / "dl" / "extracted" / "lvgl_srcs" / "lvgl"


def ensure_lvgl_source(sdk: Path, version: str, log=print) -> Path:
    """Return the LVGL source tree, downloading it into MaixCDK if needed."""
    target = lvgl_source_dir(sdk)
    if (target / "lvgl.h").is_file():
        return target

    # Older MaixCDK layouts may have left lvgl-<version>/ behind.
    legacy = target.parent / f"lvgl-{version}"
    if (legacy / "lvgl.h").is_file():
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(legacy), str(target))
        return target

    sha_map = _download_info(sdk)
    if version not in sha_map:
        raise RuntimeError(
            f"MaixCDK's lvgl component does not support version {version} "
            f"(supported: {', '.join(sha_map) or 'none'})"
        )
    url = f"https://github.com/lvgl/lvgl/archive/refs/tags/v{version}.tar.gz"
    log(f"downloading LVGL {version} into {target} ...")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / f"lvgl-{version}.tar.gz"
        urllib.request.urlretrieve(url, archive)
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        if digest != sha_map[version]:
            raise RuntimeError(
                f"LVGL {version} sha256 mismatch: {digest} != {sha_map[version]}"
            )
        with tarfile.open(archive) as tar:
            tar.extractall(tmp, filter="data")
        extracted = Path(tmp) / f"lvgl-{version}"
        if not (extracted / "lvgl.h").is_file():
            raise RuntimeError(f"unexpected LVGL archive layout: {extracted}")
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(extracted), str(target))
    log(f"LVGL source ready: {target}")
    return target


def lv_conf_path(sdk: Path) -> Path:
    return sdk / LVGL_COMPONENT / "conf" / "lv_conf.h"


def generator_version() -> str:
    if GENERATOR_VERSION_FILE.is_file():
        return GENERATOR_VERSION_FILE.read_text(encoding="utf-8").strip()
    return "unknown"


def stamp(sdk: Path, version: str, lvgl_dir: Path, conf: Path) -> dict:
    """Inputs that decide whether the generated binding is still current."""
    header = lvgl_dir / "lvgl.h"
    return {
        "lvgl_version": version,
        "lvgl_header": str(header),
        "lvgl_header_mtime_ns": header.stat().st_mtime_ns,
        "lvgl_header_size": header.stat().st_size,
        "lv_conf_sha256": hashlib.sha256(conf.read_bytes()).hexdigest(),
        "generator_version": generator_version(),
    }
