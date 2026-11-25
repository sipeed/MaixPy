"""Validation and provenance helpers; packaging stays in the native scripts."""
import argparse
import ast
import email
import hashlib
from importlib import metadata
import platform
import json
import lzma
import tempfile
import os
from pathlib import Path
import re
import struct
import subprocess
import zipfile

PYTHONS = ("3.8", "3.9", "3.10", "3.11", "3.12", "3.13")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def version_from_text(text):
    values = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in (
                    "version_major", "version_minor", "version_patch"
                ):
                    values[target.id] = ast.literal_eval(node.value)
    return ".".join(str(values["version_" + part]) for part in ("major", "minor", "patch"))


def version(path="."):
    return version_from_text((Path(path) / "maix/version.py").read_text())


def tag_version(tag):
    match = re.fullmatch(r"v([0-9]+\.[0-9]+\.[0-9]+)", tag)
    if not match:
        raise ValueError("Expected a stable release tag such as v4.12.6")
    return match.group(1)


def prepare(tag, config):
    expected = tag_version(tag)  # Validate before passing the ref to git.
    subprocess.run(["git", "fetch", "--depth=1", "origin", "refs/tags/" + tag], check=True)
    source_sha = subprocess.check_output(
        ["git", "rev-parse", "FETCH_HEAD^{commit}"], text=True
    ).strip()
    text = subprocess.check_output(["git", "show", source_sha + ":maix/version.py"], text=True)
    if version_from_text(text) != expected:
        raise ValueError("Tag does not match maix/version.py")
    settings = json.loads(Path(config).read_text())
    if not re.fullmatch(r"[0-9a-f]{40}", settings["sdk_sha"]):
        raise ValueError("MaixCDK must be pinned to a full commit SHA")
    base = subprocess.check_output(
        ["git", "show", source_sha + ":maix/version_base_system_maixcam.txt"], text=True
    ).strip()
    if base != settings["inputs"]["base"]["tag"]:
        raise ValueError("Base image version differs from release-config.json")
    ci_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    outputs = dict(tag=tag, version=expected, source_sha=source_sha,
                   sdk_sha=settings["sdk_sha"], ci_sha=ci_sha)
    with open(os.environ["GITHUB_OUTPUT"], "a") as stream:
        for key, value in outputs.items():
            stream.write("{}={}\n".format(key, value))
    print(json.dumps(outputs, indent=2))


def wheel_info(path, expected_version=None, machine=None):
    with zipfile.ZipFile(path) as archive:
        bad = archive.testzip()
        if bad:
            raise ValueError("Damaged wheel member: " + bad)
        metadata = [n for n in archive.namelist() if n.endswith(".dist-info/METADATA")]
        modules = [n for n in archive.namelist() if n == "maix/_maix.so"]
        if len(metadata) != 1 or len(modules) != 1:
            raise ValueError("Wheel must contain one METADATA and maix/_maix.so")
        info = email.message_from_bytes(archive.read(metadata[0]))
        binary = archive.read(modules[0])
        if len(binary) < 20 or binary[:6] != b"\x7fELF\x02\x01":
            raise ValueError("Expected a little-endian ELF64 native module")
        actual = struct.unpack_from("<H", binary, 18)[0]
        if expected_version and info["Version"] != expected_version:
            raise ValueError("Wheel version mismatch")
        if machine and actual != machine:
            raise ValueError("Wheel native architecture mismatch")
        return {"name": Path(path).name, "version": info["Version"], "machine": actual,
                "sha256": sha256(path)}



def check_image(path, board, expected_version):
    panels = {"maixcam": "st7701_hd228001c31", "maixcam-pro": "st7701_lct024bsi20"}
    with lzma.open(path, "rb") as stream:
        mbr = stream.read(512)
        if len(mbr) != 512 or mbr[510:512] != b"\x55\xaa":
            raise ValueError("Image has no valid MBR")
        start, sectors = struct.unpack_from("<II", mbr, 454)
        if not start or not sectors or sectors * 512 > 64 * 1024 * 1024:
            raise ValueError("Invalid boot partition geometry")
        stream.seek(start * 512)
        boot = stream.read(sectors * 512)
        if len(boot) != sectors * 512:
            raise ValueError("Truncated boot partition")
    with tempfile.TemporaryDirectory() as directory:
        image = Path(directory) / "boot.fat"
        image.write_bytes(boot)
        text = subprocess.check_output(["mtype", "-i", str(image), "::board"], text=True)
        info = dict(line.strip().split("=", 1) for line in text.splitlines() if "=" in line)
        expected_id = board.replace("-", "_")
        if info.get("id") != expected_id or info.get("panel") != panels[board]:
            raise ValueError("Image board configuration mismatch")
        value = subprocess.check_output(["mtype", "-i", str(image), "::ver"], text=True).strip()
        pattern = re.escape(board) + r"-[0-9]{4}-[0-9]{2}-[0-9]{2}-maixpy-v" + re.escape(expected_version)
        if not re.fullmatch(pattern, value):
            raise ValueError("Image version mismatch")
    print("Verified image board, panel, and version:", path)


def manifest(directory, kind):
    destination = Path(directory)
    versions = {"python": platform.python_version()}
    for package in ("cmake", "setuptools", "wheel", "PyYAML", "requests", "maixtool", "teedoc"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            pass
    info = {
        "tool_versions": versions,
        "compatibility_patch_sha256": sha256(
            Path(__file__).resolve().parents[1] / "patches/maixcdk-yaml-cstdint.patch"
        ),
        "kind": kind, "source_sha": os.environ["SOURCE_SHA"],
        "sdk_sha": os.environ["SDK_SHA"], "ci_sha": os.environ["CI_SHA"],
        "version": version(), "files": {
            p.name: sha256(p) for p in sorted(destination.iterdir()) if p.is_file()
        },
    }
    (destination / ("build-info-" + kind + ".json")).write_text(json.dumps(info, indent=2) + "\n")


def download(config, directory):
    settings = json.loads(Path(config).read_text())
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, filename in (("base", "base_os.img.xz"), ("builtin", "maixcam_builtin_files.tar.xz")):
        item = settings["inputs"][name]
        target = directory / filename
        subprocess.run(["curl", "--fail", "--location", "--retry", "3",
                        "--output", str(target), item["url"]], check=True)
        if sha256(target) != item["sha256"]:
            raise ValueError("SHA-256 mismatch for release input: " + name)
    (directory / "release-inputs.json").write_text(json.dumps(settings, indent=2) + "\n")


def collect(directory, expected_version, source_sha, sdk_sha, ci_sha):
    directory = Path(directory)
    wheels = sorted(directory.glob("*.whl"))
    if len(wheels) != len(PYTHONS) + 1:
        raise ValueError("Expected six Linux wheels and one MaixCAM wheel")
    infos = [wheel_info(p, expected_version) for p in wheels]
    linux = [p for p, i in zip(wheels, infos) if i["machine"] == 62]
    riscv = [i for i in infos if i["machine"] == 243]
    if len(linux) != 6 or len(riscv) != 1:
        raise ValueError("Release wheel architectures do not match the build matrix")
    for py in PYTHONS:
        abi = "cp" + py.replace(".", "")
        if sum(("-" + abi + "-") in p.name for p in linux) != 1:
            raise ValueError("Missing or duplicate Linux wheel for Python " + py)
    for board in ("maixcam", "maixcam-pro"):
        images = list(directory.glob(board + "-????-??-??-maixpy-v" + expected_version + ".img.xz"))
        if len(images) != 1:
            raise ValueError("Missing or duplicate image for " + board)
        subprocess.run(["xz", "--test", str(images[0])], check=True)
    for name in ("maixpy_v" + expected_version + "_doc.zip", "maixcam_builtin_files.tar.xz",
                 "release-inputs.json"):
        if not (directory / name).is_file():
            raise ValueError("Missing release artifact: " + name)
    kinds = ["linux-" + p for p in PYTHONS] + ["maixcam", "docs"]
    for kind in kinds:
        data = json.loads((directory / ("build-info-" + kind + ".json")).read_text())
        if data["source_sha"] != source_sha or data["sdk_sha"] != sdk_sha or data.get("ci_sha") != ci_sha:
            raise ValueError("Mixed source, SDK, or CI revisions in artifacts")
        for name, digest in data["files"].items():
            if Path(name).name != name or sha256(directory / name) != digest:
                raise ValueError("Artifact integrity mismatch: " + name)
    with zipfile.ZipFile(directory / ("maixpy_v" + expected_version + "_doc.zip")) as archive:
        if archive.testzip():
            raise ValueError("Corrupt documentation archive")
    summary = dict(version=expected_version, source_sha=source_sha, sdk_sha=sdk_sha,
                   ci_sha=ci_sha, wheels=infos)
    (directory / "release-manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (directory / "sha256sum_files.txt").open("w") as stream:
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.name != "sha256sum_files.txt":
                stream.write("{}  {}\n".format(sha256(path), path.name))


def main():
    parser = argparse.ArgumentParser()
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("prepare")
    p.add_argument("--tag", required=True)
    p.add_argument("--config", required=True)
    p = subs.add_parser("verify-wheel")
    p.add_argument("path")
    p.add_argument("--machine", type=int, required=True)
    p = subs.add_parser("check-image")
    p.add_argument("path")
    p.add_argument("--board", required=True, choices=["maixcam", "maixcam-pro"])
    p = subs.add_parser("manifest")
    p.add_argument("directory")
    p.add_argument("kind")
    p = subs.add_parser("download")
    p.add_argument("config")
    p.add_argument("directory")
    p = subs.add_parser("collect")
    p.add_argument("directory")
    p.add_argument("--version", required=True)
    p.add_argument("--source-sha", required=True)
    p.add_argument("--sdk-sha", required=True)
    p.add_argument("--ci-sha", required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        prepare(args.tag, args.config)
    elif args.command == "verify-wheel":
        print(json.dumps(wheel_info(args.path, version(), args.machine), indent=2))
    elif args.command == "check-image":
        check_image(args.path, args.board, version())
    elif args.command == "manifest":
        manifest(args.directory, args.kind)
    elif args.command == "download":
        download(args.config, args.directory)
    elif args.command == "collect":
        collect(args.directory, args.version, args.source_sha, args.sdk_sha, args.ci_sha)


if __name__ == "__main__":
    main()
