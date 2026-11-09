# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""CPython target entry: analyze → emit_c_cpython."""

from __future__ import print_function

from . import emit_c_cpython as emit_c_mod
from . import runtime
from .analyze import analyze
from .emit_backend import prepare_target_lowering


def emit_cpython(ctx):
    prepare_target_lowering(ctx, target="cpython", max_phase=7)
    if not getattr(ctx, "_analysis_ready", False):
        analyze(ctx)
    runtime.activate(ctx)
    emit_c_mod.emit_c(ctx)


def run(ctx):
    from .emit_cpython_native import begin_emit_helpers, reset_emit_helpers

    ctx.init_patterns()
    runtime.activate(ctx)
    helper_token = begin_emit_helpers()
    try:
        emit_cpython(ctx)
    finally:
        reset_emit_helpers(helper_token)
