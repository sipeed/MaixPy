"""Build the maix_lvgl wheel through MaixCDK's project.py.

Like MaixPy, this is a standard MaixCDK project: ``main/`` is the entry
component and ``components/lvgl_binding`` holds the LVGL CPython extension.
``python3 setup.py bdist_wheel`` runs ``python project.py build -p maixcam2``
so MaixCDK downloads and compiles its pinned LVGL together with the rest of
the stack, then packages the resulting ``lvgl`` extension plus the
``maix_lvgl`` Python package (and the non-system shared libraries it needs).
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import Distribution, Extension, setup
from setuptools.command.build_ext import build_ext

try:
    from setuptools.command.bdist_wheel import bdist_wheel as _bdist_wheel
except ImportError:  # older setuptools
    from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

ROOT = Path(__file__).resolve().parent
BOARD = "maixcam2"
EXT_NAME = "lvgl.cpython-313-aarch64-linux-gnu.so"
BUILT_LIB = ROOT / "build" / "lvgl_binding" / "liblvgl_binding.so"
BUILT_DL_LIB = ROOT / "build" / "dl_lib"
PLATFORM = "manylinux2014_aarch64"


class BinaryDistribution(Distribution):
    def has_ext_modules(self):
        return True


def _check_cmake():
    try:
        out = subprocess.check_output(["cmake", "--version"], text=True)
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit("cmake is required (MaixCDK builds with CMake).")
    match = re.search(r"version (\d+)\.", out)
    if match and int(match.group(1)) >= 4:
        print(
            "-- WARNING: cmake 4.x is not compatible with some third-party "
            "projects bundled by MaixCDK (e.g. freetype requires cmake >= 3.0). "
            "Use cmake 3.x (e.g. 3.31) on PATH for this build.",
            file=sys.stderr,
        )


def _check_pycparser():
    try:
        import pycparser  # noqa: F401
    except ImportError:
        raise SystemExit(
            "pycparser is required to generate the LVGL binding. "
            "Install it with: python3 -m pip install 'pycparser>=3.0'"
        )


class MaixCDKBuildExt(build_ext):
    """Build through MaixCDK, then stage the extension for the wheel."""

    def run(self):
        if "--skip-build" not in sys.argv:
            sdk = os.environ.get("MAIXCDK_PATH")
            if not sdk:
                raise SystemExit(
                    "Please set MAIXCDK_PATH to the MaixCDK checkout, e.g.\n"
                    "  export MAIXCDK_PATH=/path/to/MaixCDK"
                )
            _check_cmake()
            _check_pycparser()
            # The repository does not track generated binding files; create
            # them (from MaixCDK's LVGL source) before CMake configures.
            gen = [
                sys.executable,
                str(ROOT / "tools" / "regenerate_binding.py"),
                "--sdk-path",
                sdk,
            ]
            print("-- generating LVGL binding from MaixCDK source")
            subprocess.check_call(gen, cwd=ROOT)

            docs = [
                sys.executable,
                str(ROOT / "tools" / "gen_api_docs.py"),
                "--pyi",
                str(ROOT / "binding" / "lvgl.pyi"),
                "--out",
                str(ROOT / "docs" / "api"),
            ]
            print("-- generating API documentation")
            subprocess.check_call(docs, cwd=ROOT)
            cmd = [
                sys.executable,
                "project.py",
                "build",
                "-p",
                BOARD,
                "--release",
                "--config-file",
                f"configs/config_platform_{BOARD}.mk",
            ]
            print("-- building with MaixCDK:", " ".join(cmd))
            subprocess.check_call(cmd, cwd=ROOT)

        if not BUILT_LIB.is_file():
            raise SystemExit(
                f"MaixCDK build did not produce {BUILT_LIB}. "
                "Run `python3 project.py build -p maixcam2 --release` to see why."
            )

        pkg_dir = Path(self.build_lib) / "maix_lvgl"
        pkg_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(BUILT_LIB, pkg_dir / EXT_NAME)

        dl_dir = pkg_dir / "dl_lib"
        dl_dir.mkdir(exist_ok=True)
        # libdatachannel is the only shared library in MaixCDK's dl_lib that
        # MaixCAM2 firmware does not already provide; opencv/ffmpeg/AX/ssl are
        # in the system search path.
        datachannel = BUILT_DL_LIB / "libdatachannel.so"
        if datachannel.is_file():
            shutil.copy2(datachannel, dl_dir / "libdatachannel.so")


class MaixLvglWheel(_bdist_wheel):
    def finalize_options(self):
        super().finalize_options()
        if not getattr(self, "plat_name_supplied", False):
            self.plat_name = PLATFORM
            self.plat_name_supplied = True


setup(
    name="maix-lvgl",
    version="0.1.0",
    description=(
        "LVGL bindings for MaixPy (MaixCAM2), generated from MaixCDK's LVGL "
        "source with the omnipython-lvgl generator."
    ),
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="Sipeed",
    license="MIT",
    python_requires=">=3.11",
    packages=["maix_lvgl"],
    package_dir={"maix_lvgl": "maix_lvgl"},
    package_data={"maix_lvgl": ["*.so", "dl_lib/*.so*"]},
    include_package_data=True,
    ext_modules=[Extension("lvgl", sources=[])],
    cmdclass={"build_ext": MaixCDKBuildExt, "bdist_wheel": MaixLvglWheel},
    distclass=BinaryDistribution,
)
