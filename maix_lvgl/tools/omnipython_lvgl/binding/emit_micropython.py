# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""MicroPython target entry: analyze → emit_c_micropython_style."""
from __future__ import print_function

import builtins

from . import emit_c_micropython_style as emit_c_mod
from . import runtime
from .analyze import analyze
from .emit_backend import prepare_target_lowering

print = builtins.print


def run(ctx):
    ctx.init_patterns()
    runtime.activate(ctx)
    # The MP-style object/enum pass has a full-generation dependency that is
    # intentionally represented by an unbounded phase. CircuitPython and
    # CPython use their finite lifecycle phases below.
    prepare_target_lowering(ctx, target="micropython", max_phase=None)
    if not getattr(ctx, "_analysis_ready", False):
        analyze(ctx)
        runtime.activate(ctx)
    emit_c_mod.emit_c(ctx)
