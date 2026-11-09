# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Report canonical API inventory, target parity, and baseline compatibility.

The report is deliberately observational.  It validates the canonical model,
then makes target availability and remaining legacy-baseline differences
explicit without silently turning either into a backend-specific contract.
"""

from __future__ import annotations

import argparse
import fnmatch
import gzip
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from .api_model import TARGETS
from .verify_api import validate_api_data

REPORT_SCHEMA_VERSION = 2

TARGET_ARTIFACTS = {
    "micropython": "lvgl_micropython.c",
    "circuitpython": "lvgl_circuitpython.c",
    "cpython": "lvgl_python.c",
}


def load_json(path: Path) -> Any:
    """Load a JSON artifact, including the compact ``.json.gz`` baseline."""

    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as stream:
            return json.load(stream)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    """Write deterministic JSON, optionally with reproducible gzip encoding."""

    rendered = json.dumps(data, separators=(",", ":"), sort_keys=True) + "\n"
    if path.suffix == ".gz":
        with path.open("wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as stream:
                stream.write(rendered.encode("utf-8"))
        return
    path.write_text(rendered, encoding="utf-8")


def target_artifact_hashes(generated_dir: Path) -> dict[str, dict[str, str]]:
    """Hash each generated target C artifact for an auditable report."""

    result = {}
    for target in TARGETS:
        path = generated_dir / TARGET_ARTIFACTS[target]
        result[target] = {
            "file": path.name,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    return result


def _available(record: Mapping[str, Any], target: str) -> bool:
    return (
        record.get("visibility") == "public"
        and target in record.get("available_on", ())
    )


def _entry(section: str, name: str) -> str:
    return "%s.%s" % (section, name)


def _effective_methods(objects: list[Mapping[str, Any]]) -> dict[str, set[str]]:
    """Return direct plus inherited object methods, detecting bad cycles."""

    by_name = {item["python_name"]: item for item in objects}
    cache: dict[str, set[str]] = {}

    def visit(name: str, active: tuple[str, ...] = ()) -> set[str]:
        if name in cache:
            return set(cache[name])
        if name in active:
            cycle = " -> ".join(active + (name,))
            raise ValueError("object inheritance cycle: %s" % cycle)
        item = by_name.get(name)
        if item is None:
            raise ValueError("object has unknown parent: %s" % name)
        methods = set(item.get("methods", ()))
        parent = item.get("parent")
        if parent is not None:
            methods.update(visit(parent, active + (name,)))
        cache[name] = methods
        return set(methods)

    for name in by_name:
        visit(name)
    return cache


def public_export_sets(data: Mapping[str, Any]) -> dict[str, set[str]]:
    """Build qualified public exports for each target from ``api.json``.

    Object methods are expanded through the canonical inheritance graph.  A
    method is reported in the namespace of every object that inherits it,
    matching the effective Python-facing API rather than only its declaring
    C type.
    """

    functions = data.get("functions", ())
    objects = data.get("objects", ())
    function_by_object_method = {
        (item.get("receiver"), item.get("python_name")): item
        for item in functions
        if item.get("role") == "object_method"
    }
    function_by_struct_method = {
        (item.get("receiver"), item.get("python_name")): item
        for item in functions
        if item.get("role") == "struct_method"
    }
    effective_methods = _effective_methods(list(objects))
    object_by_name = {item["python_name"]: item for item in objects}
    type_names = {
        item.get("python_name")
        for section in ("structs", "enums")
        for item in data.get(section, ())
        if item.get("visibility") == "public"
    }

    result = {target: set() for target in TARGETS}
    for target in TARGETS:
        for function in functions:
            if not _available(function, target):
                continue
            role = function.get("role")
            name = function.get("python_name")
            if role == "module":
                result[target].add(_entry("module.function", name))
            elif role == "constructor":
                receiver = function.get("receiver")
                result[target].add(_entry("object", "%s.create" % receiver))
            elif role == "struct_method":
                receiver = function.get("receiver")
                result[target].add(
                    _entry("struct", "%s.%s" % (receiver, name))
                )

        for object_ in objects:
            if not _available(object_, target):
                continue
            object_name = object_["python_name"]
            result[target].add(_entry("object", object_name))
            for method_name in effective_methods[object_name]:
                declaring = function_by_object_method.get(
                    (object_name, method_name)
                )
                if declaring is None:
                    parent = object_.get("parent")
                    while parent is not None and declaring is None:
                        declaring = function_by_object_method.get(
                            (parent, method_name)
                        )
                        parent = object_by_name.get(parent, {}).get("parent")
                if declaring is not None and _available(declaring, target):
                    result[target].add(
                        _entry("object", "%s.%s" % (object_name, method_name))
                    )

        for struct in data.get("structs", ()):
            if not _available(struct, target):
                continue
            result[target].add(_entry("struct", struct["python_name"]))
        for (receiver, name), function in function_by_struct_method.items():
            if _available(function, target):
                result[target].add(
                    _entry("struct", "%s.%s" % (receiver, name))
                )

        for enum in data.get("enums", ()):
            if not _available(enum, target):
                continue
            member_names = [member["name"] for member in enum.get("members", ())]
            module_name = enum.get("module_name")
            if module_name is not None:
                result[target].add(_entry("enum", module_name))
                result[target].update(
                    _entry("enum", "%s.%s" % (module_name, member_name))
                    for member_name in member_names
                )
            for owner_name, nested_name in (
                (item.get("object"), item.get("name"))
                for item in enum.get("owners", ())
            ):
                if owner_name not in object_by_name:
                    continue
                for object_record in objects:
                    if not _available(object_record, target):
                        continue
                    current = object_record
                    inherits_from_owner = False
                    while current is not None:
                        if current["python_name"] == owner_name:
                            inherits_from_owner = True
                            break
                        parent = current.get("parent")
                        current = object_by_name.get(parent) if parent else None
                    if inherits_from_owner:
                        result[target].add(
                            _entry(
                                "object",
                                "%s.%s" % (
                                    object_record["python_name"],
                                    nested_name,
                                ),
                            )
                        )
        for typedef in data.get("typedefs", ()):
            if not _available(typedef, target):
                continue
            if (
                typedef.get("name") in type_names
                and typedef.get("type", {}).get("kind")
                in {"struct", "union", "enum"}
            ):
                continue
            result[target].add(_entry("typedef", typedef["name"]))
        for variable in data.get("variables", ()):
            if _available(variable, target):
                result[target].add(
                    _entry("variable", variable.get("python_name") or variable["c_name"])
                )
        for constant in data.get("constants", ()):
            if _available(constant, target):
                result[target].add(_entry("constant", constant["python_name"]))
    return result


def _record_inventory(data: Mapping[str, Any]) -> dict[str, dict[str, int]]:
    sections = (
        "functions",
        "objects",
        "structs",
        "enums",
        "typedefs",
        "variables",
        "constants",
    )
    inventory = {}
    for section in sections:
        counts: dict[str, int] = {}
        for item in data.get(section, ()):
            visibility = item.get("visibility", "unknown")
            counts[visibility] = counts.get(visibility, 0) + 1
        inventory[section] = dict(sorted(counts.items()))
    return inventory


def _parity(exports: Mapping[str, set[str]]) -> dict[str, Any]:
    sets = [set(exports[target]) for target in TARGETS]
    union = set().union(*sets)
    intersection = set(sets[0]).intersection(*sets[1:])
    return {
        "union_count": len(union),
        "intersection_count": len(intersection),
        "common_coverage": len(intersection) / float(len(union) or 1),
        "all_targets_equal": all(item == sets[0] for item in sets[1:]),
        "coverage_of_union": {
            target: len(exports[target]) / float(len(union) or 1)
            for target in TARGETS
        },
        "missing_for_target": {
            target: sorted(union - exports[target]) for target in TARGETS
        },
        "target_unique": {
            target: sorted(exports[target] - intersection) for target in TARGETS
        },
        "availability_exceptions": sorted(
            union - intersection
        ),
    }


def _expand_manifest(manifest: Mapping[str, Any]) -> set[str]:
    signatures = manifest.get("signatures", ())

    def signature(index: int) -> Mapping[str, Any]:
        return signatures[index]

    entries: set[str] = set()
    for name in manifest.get("functions", {}):
        entries.add(_entry("module.function", name))
    for name, value in manifest.get("objects", {}).items():
        entries.add(_entry("object", name))
        entries.update(
            _entry("object", "%s.%s" % (name, member))
            for member in value.get("members", {})
        )
    for name, value in manifest.get("enums", {}).items():
        enum = signature(value)
        entries.add(_entry("enum", name))
        entries.update(
            _entry("enum", "%s.%s" % (name, member))
            for member in enum.get("members", ())
        )
    entries.update(_entry("struct", name) for name in manifest.get("structs", ()))
    entries.update(_entry("blob", name) for name in manifest.get("blobs", ()))
    entries.update(
        _entry("constant", name) for name in manifest.get("int_constants", ())
    )
    for name, members in manifest.get("struct_functions", {}).items():
        entries.update(
            _entry("struct_function", "%s.%s" % (name, member))
            for member in members
        )
    return entries


def _model_compatibility_entries(data: Mapping[str, Any]) -> set[str]:
    """Project the model into the sections used by the historical baseline."""

    exports = public_export_sets(data)[TARGETS[0]]
    result = set()
    for value in exports:
        if value.startswith("object.") and value.rsplit(".", 1)[-1] == "create":
            continue
        if value.startswith("variable."):
            result.add(_entry("blob", value.split(".", 1)[1]))
        elif value.startswith("constant."):
            result.add(_entry("constant", value.split(".", 1)[1]))
        elif value.startswith("struct."):
            result.add(value)
        elif value.startswith("enum."):
            result.add(value)
        elif value.startswith("module.function."):
            result.add(value)
        elif value.startswith("object."):
            result.add(value)
    return result


def _classify_differences(
    differences: Mapping[str, list[str]], classification: Mapping[str, Any] | None
) -> Mapping[str, Any]:
    """Classify historical-baseline differences with an auditable rule file."""

    if classification is None:
        return {"classified": [], "unexplained": {key: list(value) for key, value in differences.items()}}
    if classification.get("schema_version") != 1:
        raise ValueError("unsupported baseline classification schema")
    rules = classification.get("rules", ())
    buckets: dict[str, dict[str, Any]] = {}
    used = set()
    unexplained = {side: [] for side in differences}
    for side, entries in differences.items():
        for entry in entries:
            matches = [
                rule for rule in rules
                if rule.get("side") == side
                and any(fnmatch.fnmatchcase(entry, pattern) for pattern in rule.get("patterns", ()))
            ]
            if len(matches) > 1:
                raise ValueError("overlapping baseline classification rules for %s" % entry)
            if not matches:
                unexplained[side].append(entry)
                continue
            rule = matches[0]
            rule_id = rule.get("id")
            if not rule_id or not rule.get("classification") or not rule.get("reason"):
                raise ValueError("baseline classification rules require id, classification, and reason")
            used.add(rule_id)
            bucket = buckets.setdefault(
                rule_id,
                {key: rule[key] for key in ("id", "classification", "reason")},
            )
            bucket.setdefault("entries", []).append(entry)
    stale = sorted(rule.get("id") for rule in rules if rule.get("id") not in used)
    if stale:
        raise ValueError("stale baseline classification rules: %s" % ", ".join(stale))
    return {"classified": [buckets[key] for key in sorted(buckets)], "unexplained": unexplained}


def _baseline_report(
    data: Mapping[str, Any], baseline: Mapping[str, Any] | None,
    classification: Mapping[str, Any] | None = None,
) -> Mapping[str, Any] | None:
    if baseline is None:
        return None
    base = baseline.get("baseline")
    if not isinstance(base, Mapping):
        raise ValueError("baseline must contain a compact baseline manifest")
    expected = _expand_manifest(base)
    actual = _model_compatibility_entries(data)
    common = expected & actual
    differences = {"missing": sorted(expected - actual), "extra": sorted(actual - expected)}
    classifications = _classify_differences(differences, classification)
    explained = not any(classifications["unexplained"].values())
    return {
        "baseline_schema": baseline.get("schema"),
        "baseline_entries": len(expected),
        "candidate_entries": len(actual),
        "name_location_matches": len(common),
        "coverage": len(common) / float(len(expected) or 1),
        **differences,
        "classification": classifications,
        "historical_target_comparisons": {
            target: {
                "coverage": baseline.get("targets", {})
                .get(target, {})
                .get("comparison", {})
                .get("coverage")
            }
            for target in TARGETS
        },
        "interpretation": (
            "Every historical difference is classified by the audited policy."
            if explained
            else "The candidate projection is diagnostic while canonical lowering "
            "is still under construction; it is not a release gate."
        ),
    }


def build_report(
    data: Mapping[str, Any], baseline: Mapping[str, Any] | None = None,
    classification: Mapping[str, Any] | None = None,
    target_artifacts: Mapping[str, Mapping[str, str]] | None = None,
) -> Mapping[str, Any]:
    """Build a deterministic report from canonical model JSON data."""

    errors = validate_api_data(data)
    if errors:
        raise ValueError("invalid canonical API model: %s" % "; ".join(errors))
    exports = public_export_sets(data)
    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "api_hash": data["api_hash"],
        "inventory": _record_inventory(data),
        "target_exports": {
            target: {"count": len(exports[target])} for target in TARGETS
        },
        "target_parity": _parity(exports),
        "baseline_compatibility": _baseline_report(data, baseline, classification),
    }
    if target_artifacts is not None:
        report["target_artifacts"] = {
            target: dict(target_artifacts[target]) for target in TARGETS
        }
    return report


def _markdown(report: Mapping[str, Any]) -> str:
    lines = [
        "# LVGL canonical API report",
        "",
        "- API hash: `%s`" % report["api_hash"],
        "- Report schema: `%s`" % report["schema_version"],
        "",
        "## Target exports",
        "",
        "| Target | Qualified exports | Coverage of union |",
        "| --- | ---: | ---: |",
    ]
    parity = report["target_parity"]
    for target in TARGETS:
        lines.append(
            "| %s | %d | %.2f%% |"
            % (
                target,
                report["target_exports"][target]["count"],
                parity["coverage_of_union"][target] * 100.0,
            )
        )
    lines.extend(
        [
            "",
            "- Shared exports: %d" % parity["intersection_count"],
            "- Union exports: %d" % parity["union_count"],
            "- Common-target API coverage: %.2f%%"
            % (parity["common_coverage"] * 100.0),
            "- Availability exceptions: %d" % len(parity["availability_exceptions"]),
            "",
            "## Record inventory",
            "",
            "| Section | Visibility counts |",
            "| --- | --- |",
        ]
    )
    for section, counts in report["inventory"].items():
        rendered = ", ".join(
            "%s=%d" % (visibility, count)
            for visibility, count in counts.items()
        )
        lines.append("| `%s` | %s |" % (section, rendered or "none"))
    artifacts = report.get("target_artifacts")
    if artifacts is not None:
        lines.extend(
            [
                "",
                "## Generated target artifacts",
                "",
                "| Target | File | SHA-256 |",
                "| --- | --- | --- |",
            ]
        )
        for target in TARGETS:
            artifact = artifacts[target]
            lines.append(
                "| %s | `%s` | `%s` |"
                % (target, artifact["file"], artifact["sha256"])
            )
    baseline = report.get("baseline_compatibility")
    if baseline is not None:
        lines.extend(
            [
                "",
                "## Historical baseline projection",
                "",
                "- Candidate coverage: %.2f%% (%d/%d)"
                % (
                    baseline["coverage"] * 100.0,
                    baseline["name_location_matches"],
                    baseline["baseline_entries"],
                ),
                "- Missing: %d" % len(baseline["missing"]),
                "- Extra: %d" % len(baseline["extra"]),
                "- Classified differences: %d"
                % len(baseline["classification"]["classified"]),
                "- Unexplained differences: %d"
                % sum(
                    len(entries)
                    for entries in baseline["classification"]["unexplained"].values()
                ),
                "",
                baseline["interpretation"],
            ]
        )
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("api", type=Path, help="generated/api.json")
    parser.add_argument(
        "--baseline",
        type=Path,
        help="optional normalized upstream baseline JSON",
    )
    parser.add_argument(
        "--classification", type=Path,
        help="optional audited historical-baseline difference classifications",
    )
    parser.add_argument(
        "--format", choices=("json", "markdown"), default="json"
    )
    parser.add_argument("--output", type=Path, help="write report to this path")
    args = parser.parse_args(argv)

    data = load_json(args.api)
    baseline = (
        load_json(args.baseline)
        if args.baseline is not None
        else None
    )
    classification = (
        load_json(args.classification)
        if args.classification is not None
        else None
    )
    report = build_report(
        data,
        baseline,
        classification,
        target_artifact_hashes(args.api.parent),
    )
    rendered = (
        json.dumps(report, indent=2, sort_keys=True) + "\n"
        if args.format == "json"
        else _markdown(report)
    )
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
