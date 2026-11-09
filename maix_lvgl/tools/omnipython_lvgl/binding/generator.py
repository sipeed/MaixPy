# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Shared analysis and target-backend orchestration."""

from __future__ import print_function

import copy
from dataclasses import dataclass
from importlib import import_module

from .context import BindingContext


@dataclass(frozen=True)
class Backend:
    """Target-specific lowering entry point behind the common generator flow."""

    name: str
    emitter_module: str


@dataclass
class BackendRun:
    """Completed lowering run for one target."""

    context: BindingContext
    emitted: bool = True


BACKENDS = {
    "micropython": Backend("micropython", "binding.emit_micropython"),
    "circuitpython": Backend("circuitpython", "binding.emit_circuitpython"),
    "cpython": Backend("cpython", "binding.emit_cpython"),
}


_ANALYSIS_STATE_NAMES = (
    "obj_metadata",
    "func_metadata",
    "callback_metadata",
    "func_prototypes",
    "parser",
    "gen",
    "parsed_ast",
    "ast",
    "declaration_ir",
    "declaration_index",
    "api_model",
    "lvgl_json",
    "forward_struct_decls",
    "typedefs",
    "synonym",
    "struct_typedefs",
    "structs_without_typedef",
    "structs",
    "explicit_structs",
    "opaque_structs",
    "func_defs",
    "func_decls",
    "all_funcs",
    "funcs",
    "obj_ctors",
    "obj_names",
    "parent_obj_names",
    "enum_defs",
    "func_typedefs",
    "blobs",
    "int_constants",
    "mp_to_lv",
    "lv_to_mp",
    "lv_mp_type",
    "lv_to_mp_byref",
    "lv_to_mp_funcptr",
)


def prepare_analysis(args, source, pp_cmd, cmd_line, emit_print):
    """Parse and analyze one translation unit for reuse by every target."""
    from pycparser import c_generator, c_parser

    from . import runtime
    from .api_model import build_api_model
    from .api_policy import ApiPolicy
    from .analyze import analyze

    runtime.reset()
    ctx = BindingContext(args, source, pp_cmd, cmd_line, emit_print)
    ctx.init_patterns()
    ctx.parser = c_parser.CParser()
    ctx.gen = c_generator.CGenerator()
    ctx.parsed_ast = ctx.parser.parse(source, filename="<none>")
    runtime.activate(ctx)
    analyze(ctx)
    runtime.activate(ctx)
    policy = ApiPolicy.default(module_prefix=ctx.module_prefix)
    ctx.api_model = build_api_model(
        ctx.declaration_ir,
        module_prefix=ctx.module_prefix,
        base_obj_type=ctx.base_obj_type,
        policy=policy,
    )
    runtime.set_("api_model", ctx.api_model)
    return ctx


def analysis_snapshot(ctx):
    """Return an isolated, internally consistent copy of analysis state."""
    values = {
        name: getattr(ctx, name)
        for name in _ANALYSIS_STATE_NAMES
        if hasattr(ctx, name)
    }
    snapshot = copy.deepcopy(values)
    # DeclarationIR is frozen and target-neutral.  Preserve the same object so
    # every backend receives the exact canonical declaration set, not a copy.
    if hasattr(ctx, "declaration_ir"):
        snapshot["declaration_ir"] = ctx.declaration_ir
    if hasattr(ctx, "api_model"):
        snapshot["api_model"] = ctx.api_model
    return snapshot


def _new_context(args, source, pp_cmd, cmd_line, emit_print, analysis_state=None):
    from .util import clear_memoized

    clear_memoized()
    ctx = BindingContext(args, source, pp_cmd, cmd_line, emit_print)
    ctx.init_patterns()
    if analysis_state is not None:
        values = copy.deepcopy(analysis_state)
        if "declaration_ir" in analysis_state:
            values["declaration_ir"] = analysis_state["declaration_ir"]
        if "api_model" in analysis_state:
            values["api_model"] = analysis_state["api_model"]
        for name, value in values.items():
            setattr(ctx, name, value)
        ctx._analysis_ready = True
    return ctx


def run_backend(target, args, source, pp_cmd, out, cmd_line, analysis_state=None):
    """Lower one shared analysis snapshot through a named target backend."""
    import builtins

    try:
        backend = BACKENDS[target]
    except KeyError:
        raise ValueError("unsupported backend: %s" % target)

    def emit_print(*a, **k):
        k.setdefault("file", out)
        builtins.print(*a, **k)

    ctx = _new_context(
        args, source, pp_cmd, cmd_line, emit_print, analysis_state=analysis_state
    )
    from . import runtime

    with runtime.scoped(ctx):
        import_module(backend.emitter_module).run(ctx)
    return BackendRun(ctx)
