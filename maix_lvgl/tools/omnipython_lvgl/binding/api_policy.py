# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Auditable visibility and target-availability policy for the API model."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, Tuple

from .api_model import TARGETS


@dataclass(frozen=True)
class PolicyRecord:
    name: str
    reason: str
    test: str


@dataclass(frozen=True)
class TargetException:
    name: str
    target: str
    reason: str
    test: str


@dataclass(frozen=True)
class PolicyDecision:
    visibility: str
    available_on: Tuple[str, ...] = TARGETS
    reason: Optional[str] = None


class ApiPolicy:
    """Policy applied after parsing and before target lowering.

    The policy is intentionally independent of any emitter.  A symbol may be
    present in the declaration IR while being private to the binding or
    unavailable on one target; those facts remain visible in the model.
    """

    def __init__(
        self,
        *,
        module_prefix: str = "lv",
        private_functions: Sequence[PolicyRecord] = (),
        unsupported_functions: Sequence[PolicyRecord] = (),
        private_structs: Sequence[PolicyRecord] = (),
        private_enums: Sequence[PolicyRecord] = (),
        private_variables: Sequence[PolicyRecord] = (),
        target_exceptions: Sequence[TargetException] = (),
    ) -> None:
        self.module_prefix = module_prefix
        private_functions = tuple(private_functions)
        unsupported_functions = tuple(unsupported_functions)
        private_structs = tuple(private_structs)
        private_enums = tuple(private_enums)
        private_variables = tuple(private_variables)
        target_exceptions = tuple(target_exceptions)
        self.private_functions = {record.name: record for record in private_functions}
        self.unsupported_functions = {
            record.name: record for record in unsupported_functions
        }
        self.private_structs = {record.name: record for record in private_structs}
        self.private_enums = {record.name: record for record in private_enums}
        self.private_variables = {record.name: record for record in private_variables}
        self.target_exceptions = {
            (record.name, record.target): record
            for record in target_exceptions
        }
        if len(self.private_functions) != len(private_functions):
            raise ValueError("duplicate private function in API policy")
        if len(self.unsupported_functions) != len(unsupported_functions):
            raise ValueError("duplicate unsupported function in API policy")
        overlap = set(self.private_functions) & set(self.unsupported_functions)
        if overlap:
            raise ValueError(
                "functions cannot be both private and unsupported: %s"
                % ", ".join(sorted(overlap))
            )
        if len(self.private_structs) != len(private_structs):
            raise ValueError("duplicate private struct in API policy")
        if len(self.private_enums) != len(private_enums):
            raise ValueError("duplicate private enum in API policy")
        if len(self.private_variables) != len(private_variables):
            raise ValueError("duplicate private variable in API policy")
        if len(self.target_exceptions) != len(target_exceptions):
            raise ValueError("duplicate target exception in API policy")
        self._validate()

    @classmethod
    def from_file(cls, path: Path, *, module_prefix: str = "lv") -> "ApiPolicy":
        with Path(path).open(encoding="utf-8") as handle:
            data = json.load(handle)
        if data.get("schema_version") != 1:
            raise ValueError("unsupported API policy schema")

        def records(key: str) -> Tuple[PolicyRecord, ...]:
            return tuple(
                PolicyRecord(
                    name=item["name"],
                    reason=item["reason"],
                    test=item["test"],
                )
                for item in data.get(key, ())
            )

        exceptions = tuple(
            TargetException(
                name=item["name"],
                target=item["target"],
                reason=item["reason"],
                test=item["test"],
            )
            for item in data.get("target_exceptions", ())
        )
        return cls(
            module_prefix=module_prefix,
            private_functions=records("private_functions"),
            unsupported_functions=records("unsupported_functions"),
            private_structs=records("private_structs"),
            private_enums=records("private_enums"),
            private_variables=records("private_variables"),
            target_exceptions=exceptions,
        )

    @classmethod
    def default(cls, *, module_prefix: str = "lv") -> "ApiPolicy":
        return cls.from_file(
            Path(__file__).with_name("api_policy.json"),
            module_prefix=module_prefix,
        )

    def _validate(self) -> None:
        if not self.module_prefix:
            raise ValueError("API policy requires a module prefix")
        for target in (record.target for record in self.target_exceptions.values()):
            if target not in TARGETS:
                raise ValueError("unknown API policy target: %s" % target)
        for record in tuple(self.private_functions.values()) + tuple(
            self.unsupported_functions.values()
        ) + tuple(
            self.private_structs.values()
        ) + tuple(
            self.private_enums.values()
        ) + tuple(self.private_variables.values()):
            if not record.reason or not record.test:
                raise ValueError("API policy records require reason and test: %s" % record.name)
        for record in self.target_exceptions.values():
            if not record.reason or not record.test:
                raise ValueError(
                    "API target exceptions require reason and test: %s" % record.name
                )

    def function(self, name: str) -> PolicyDecision:
        private = self.private_functions.get(name)
        if private is not None:
            return PolicyDecision("private", reason=private.reason)
        unsupported = self.unsupported_functions.get(name)
        if unsupported is not None:
            return PolicyDecision("private", reason=unsupported.reason)
        if not name.startswith(self.module_prefix + "_"):
            return PolicyDecision("private", reason="outside module prefix")
        return PolicyDecision(
            "public",
            available_on=self._available_on(name),
        )

    def struct(self, names: Sequence[Optional[str]]) -> PolicyDecision:
        candidates = {name for name in names if name}
        private = next(
            (self.private_structs[name] for name in candidates if name in self.private_structs),
            None,
        )
        if private is not None:
            return PolicyDecision("private", reason=private.reason)
        if any(
            name.startswith(self.module_prefix + "_")
            or name.startswith("_" + self.module_prefix + "_")
            for name in candidates
        ):
            return PolicyDecision("public")
        return PolicyDecision("private", reason="outside module prefix")

    def enum(self, names: Sequence[Optional[str]]) -> PolicyDecision:
        candidates = {name for name in names if name}
        private = next(
            (self.private_enums[name] for name in candidates if name in self.private_enums),
            None,
        )
        if private is not None:
            return PolicyDecision("private", reason=private.reason)
        if any(
            name.startswith(self.module_prefix + "_")
            or name.startswith("_" + self.module_prefix + "_")
            for name in candidates
        ):
            return PolicyDecision("public")
        return PolicyDecision("private", reason="outside module prefix")

    def typedef(self, name: str) -> PolicyDecision:
        if name.startswith(self.module_prefix + "_"):
            return PolicyDecision("public")
        return PolicyDecision("private", reason="outside module prefix")

    def variable(self, name: str) -> PolicyDecision:
        private = self.private_variables.get(name)
        if private is not None:
            return PolicyDecision("private", reason=private.reason)
        if name.startswith(self.module_prefix + "_"):
            return PolicyDecision("public")
        return PolicyDecision("private", reason="outside module prefix")

    def _available_on(self, name: str) -> Tuple[str, ...]:
        unavailable = {
            record.target
            for (record_name, _), record in self.target_exceptions.items()
            if record_name == name
        }
        return tuple(target for target in TARGETS if target not in unavailable)


def validate_policy_against_declarations(policy: ApiPolicy, declarations: Any) -> None:
    """Fail when a policy names a symbol absent from the parsed translation unit."""

    function_names = {function.name for function in declarations.functions}
    struct_names = {
        name
        for struct in declarations.structs
        for name in (struct.name,) + tuple(struct.typedef_names)
        if name
    }
    missing = []
    for name in policy.private_functions:
        if name not in function_names:
            missing.append("function " + name)
    for name in policy.unsupported_functions:
        if name not in function_names:
            missing.append("function " + name)
    for name in policy.private_structs:
        if name not in struct_names:
            missing.append("struct " + name)
    enum_names = {
        name
        for enum in declarations.enums
        for name in (enum.name,) + tuple(enum.typedef_names)
        if name
    }
    for name in policy.private_enums:
        if name not in enum_names:
            missing.append("enum " + name)
    variable_names = {variable.name for variable in declarations.variables}
    for name in policy.private_variables:
        if name not in variable_names:
            missing.append("variable " + name)
    for name, _target in policy.target_exceptions:
        if name not in function_names:
            missing.append("function " + name)
    if missing:
        raise ValueError("API policy names missing declarations: %s" % ", ".join(sorted(missing)))
