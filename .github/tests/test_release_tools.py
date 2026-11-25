import importlib.util
import json
import lzma
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location(
    "release_tools", Path(__file__).resolve().parents[1] / "scripts/release_tools.py"
)
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


def make_wheel(directory, name, machine, version="4.12.6"):
    path = Path(directory) / name
    binary = bytearray(20)
    binary[:6] = b"\x7fELF\x02\x01"
    struct.pack_into("<H", binary, 18, machine)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("maix/_maix.so", binary)
        archive.writestr("maixpy-{}.dist-info/METADATA".format(version),
                         "Name: MaixPy\nVersion: " + version + "\n")
    return path


class ReleaseToolsTest(unittest.TestCase):
    def test_tag_and_version_match_source_constants(self):
        self.assertEqual(tools.tag_version("v4.12.6"), "4.12.6")
        for invalid in ("main", "v4.12.6; touch x", "v4.12.6/../main", "v4.12.6-rc1"):
            with self.assertRaises(ValueError):
                tools.tag_version(invalid)
        self.assertEqual(tools.version_from_text(
            "version_major=4\nversion_minor=12\nversion_patch=6\n"), "4.12.6")

    def test_image_rejects_invalid_partition_table(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "invalid.img.xz"
            image.write_bytes(lzma.compress(b"\x00" * 512))
            with self.assertRaises(ValueError):
                tools.check_image(image, "maixcam", "4.12.6")

    def test_image_rejects_wrong_board_and_version(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "boot.img.xz"
            mbr = bytearray(512)
            mbr[510:512] = bytes([0x55, 0xaa])
            struct.pack_into("<II", mbr, 454, 1, 1)
            image.write_bytes(lzma.compress(bytes(mbr) + bytes(512)))
            cases = [
                ("id=maixcam_pro\npanel=st7701_lct024bsi20\n", "unused"),
                ("id=maixcam\npanel=st7701_hd228001c31\n", "maixcam-2026-11-10-maixpy-v4.12.5"),
            ]
            for board, version in cases:
                with self.subTest(board=board, version=version):
                    with patch.object(tools.subprocess, "check_output", side_effect=[board, version]):
                        with self.assertRaises(ValueError):
                            tools.check_image(image, "maixcam", "4.12.6")

    def test_image_accepts_matching_board_and_version(self):
        with tempfile.TemporaryDirectory() as directory:
            image = Path(directory) / "boot.img.xz"
            mbr = bytearray(512)
            mbr[510:512] = bytes([0x55, 0xaa])
            struct.pack_into("<II", mbr, 454, 1, 1)
            image.write_bytes(lzma.compress(bytes(mbr) + bytes(512)))
            board = "id=maixcam\npanel=st7701_hd228001c31\n"
            version = "maixcam-2026-11-10-maixpy-v4.12.6"
            with patch.object(tools.subprocess, "check_output", side_effect=[board, version]):
                tools.check_image(image, "maixcam", "4.12.6")

    def test_wheel_rejects_wrong_architecture_and_version(self):
        with tempfile.TemporaryDirectory() as directory:
            wheel = make_wheel(directory, "maixpy.whl", 243)
            self.assertEqual(tools.wheel_info(wheel, "4.12.6", 243)["machine"], 243)
            with self.assertRaises(ValueError):
                tools.wheel_info(wheel, "4.12.6", 62)
            with self.assertRaises(ValueError):
                tools.wheel_info(wheel, "4.12.5", 243)

    def test_wheel_rejects_missing_native_module(self):
        with tempfile.TemporaryDirectory() as directory:
            wheel = Path(directory) / "invalid.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("x.dist-info/METADATA", "Version: 4.12.6\n")
            with self.assertRaises(ValueError):
                tools.wheel_info(wheel)

    def release_fixture(self, directory):
        files = []
        for py in tools.PYTHONS:
            abi = "cp" + py.replace(".", "")
            files.append(make_wheel(directory,
                "maixpy-4.12.6-{}-{}-manylinux2014_x86_64.whl".format(abi, abi), 62))
        files.append(make_wheel(directory, "MaixPy-4.12.6-py3-none-any.whl", 243))
        for board in ("maixcam", "maixcam-pro"):
            p = directory / (board + "-2026-11-10-maixpy-v4.12.6.img.xz")
            p.write_bytes(lzma.compress(b"test image"))
        with zipfile.ZipFile(directory / "maixpy_v4.12.6_doc.zip", "w") as archive:
            archive.writestr("index.html", "documentation")
        for name in ("maixcam_builtin_files.tar.xz", "release-inputs.json"):
            (directory / name).write_text("input")
        file_map = {p.name: tools.sha256(p) for p in directory.iterdir()}
        for kind in ["linux-" + p for p in tools.PYTHONS] + ["maixcam", "docs"]:
            (directory / ("build-info-" + kind + ".json")).write_text(json.dumps({
                "source_sha": "a" * 40, "sdk_sha": "b" * 40, "ci_sha": "d" * 40, "files": file_map,
            }))
        return files

    def test_collect_checks_completeness_and_all_checksums(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            self.release_fixture(directory)
            tools.collect(directory, "4.12.6", "a" * 40, "b" * 40, "d" * 40)
            lines = (directory / "sha256sum_files.txt").read_text().splitlines()
            self.assertEqual(len(lines), len(list(directory.iterdir())) - 1)
            self.assertTrue(any("py3-none-any.whl" in line for line in lines))
            self.assertTrue(any("maixcam-pro-" in line for line in lines))
            self.assertTrue(any("cp38-" in line for line in lines))

    def test_collect_rejects_missing_matrix_member(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            wheels = self.release_fixture(directory)
            wheels[0].unlink()
            with self.assertRaises(ValueError):
                tools.collect(directory, "4.12.6", "a" * 40, "b" * 40, "d" * 40)

    def test_collect_rejects_mixed_sdk_revisions(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            self.release_fixture(directory)
            with self.assertRaises(ValueError):
                tools.collect(directory, "4.12.6", "a" * 40, "c" * 40, "d" * 40)

    def test_collect_rejects_mixed_ci_revisions(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            self.release_fixture(directory)
            with self.assertRaises(ValueError):
                tools.collect(directory, "4.12.6", "a" * 40, "b" * 40, "e" * 40)

    def test_collect_rejects_modified_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            self.release_fixture(directory)
            (directory / "release-inputs.json").write_text("modified after build")
            with self.assertRaises(ValueError):
                tools.collect(directory, "4.12.6", "a" * 40, "b" * 40, "d" * 40)

    def test_download_rejects_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            config = directory / "config.json"
            config.write_text(json.dumps({"inputs": {
                "base": {"url": "https://example.invalid/image", "sha256": "0" * 64}
            }}))
            def fake_download(command, check):
                Path(command[command.index("--output") + 1]).write_text("wrong file")
            with patch.object(tools.subprocess, "run", side_effect=fake_download):
                with self.assertRaises(ValueError):
                    tools.download(config, directory / "downloads")


if __name__ == "__main__":
    unittest.main()
