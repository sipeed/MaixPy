# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Established upstream-compatible Python export names."""

from __future__ import annotations

def _established_name(name: str, kind: str) -> str:
    from .analyze import get_enum_member_name
    from . import helpers
    from .helpers import get_enum_name, sanitize

    def _simplify(name: str) -> str:
        try:
            return helpers.simplify_identifier(name)
        except RuntimeError:
            return name

    def _enum_name(name: str) -> str:
        try:
            return sanitize(get_enum_name(name))
        except RuntimeError:
            return sanitize(name)

    if kind == "object":
        return sanitize(name)
    if kind == "enum":
        return _enum_name(name)
    if kind == "enum_member":
        return sanitize(get_enum_member_name(name))
    if kind == "function":
        return sanitize(_simplify(name))
    if kind == "struct":
        return sanitize(_simplify(name))
    if kind == "blob":
        return sanitize(_simplify(name))
    if kind == "constant":
        return _enum_name(name)
    return sanitize(name)


def export_name(name: str, kind: str) -> str:
    """Return the Python-facing export identifier for ``name``."""
    return _established_name(name, kind)
