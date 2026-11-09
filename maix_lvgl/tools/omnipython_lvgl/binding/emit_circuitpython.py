# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""CircuitPython target entry: analyze → emit_c_micropython_style (target=circuitpython)."""

from __future__ import print_function

from . import emit_c_micropython_style as emit_c_mod
from . import runtime
from .analyze import analyze
from .emit_backend import prepare_target_lowering


def emit_circuitpython(ctx):
    """Run shared analysis and emit CircuitPython C source to ctx.emit_print."""
    prepare_target_lowering(ctx, target="circuitpython", max_phase=7)
    if not getattr(ctx, "_analysis_ready", False):
        analyze(ctx)
    runtime.activate(ctx)
    emit_c_mod.emit_c(ctx)


def run(ctx):
    ctx.init_patterns()
    runtime.activate(ctx)
    emit_circuitpython(ctx)
