# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Context-local state access for one binding generation run."""
from __future__ import print_function

from contextlib import contextmanager
from contextvars import ContextVar

from .context import BindingContext


_ACTIVE_CONTEXT = ContextVar("lvgl_binding_context", default=None)
_RUN_VALUES = ContextVar("lvgl_binding_run_values", default=None)


def current_context():
    """Return the context for the active generation run."""
    ctx = _ACTIVE_CONTEXT.get()
    if ctx is None:
        raise RuntimeError("no active binding generation context")
    return ctx

def export_names():
    return BindingContext.EXPORT_NAMES


def set_(name, value):
    """Assign state on the active context, or to run-local extra values."""
    ctx = _ACTIVE_CONTEXT.get()
    if ctx is not None:
        setattr(ctx, name, value)
        return
    values = _RUN_VALUES.get()
    if values is None:
        values = {}
        _RUN_VALUES.set(values)
    values[name] = value


def activate(ctx):
    """Activate a context for the current generation flow."""
    _ACTIVE_CONTEXT.set(ctx)
    _RUN_VALUES.set({})


@contextmanager
def scoped(ctx):
    """Activate one run and restore an enclosing run when it completes."""
    context_token = _ACTIVE_CONTEXT.set(ctx)
    values_token = _RUN_VALUES.set({})
    try:
        yield ctx
    finally:
        _RUN_VALUES.reset(values_token)
        _ACTIVE_CONTEXT.reset(context_token)


def reset():
    """Clear context-local generation state before an in-process run."""
    from .util import clear_memoized

    clear_memoized()

    _ACTIVE_CONTEXT.set(None)
    _RUN_VALUES.set({})


_MISSING = object()


def get(name, default=_MISSING):
    """Return state from the active context or run-local extra values."""
    ctx = _ACTIVE_CONTEXT.get()
    if ctx is not None and hasattr(ctx, name):
        return getattr(ctx, name)
    values = _RUN_VALUES.get() or {}
    if name in values:
        return values[name]
    if default is not _MISSING:
        return default
    raise NameError(name)


def emit(*args, **kwargs):
    """Write generated output through the active binding context explicitly."""
    ctx = _ACTIVE_CONTEXT.get()
    writer = ctx.emit_print if ctx is not None else get("print")
    return writer(*args, **kwargs)


class _Namespace(object):
    """Attribute access to binding globals (read/write through runtime)."""

    def __getattr__(self, name):
        try:
            return get(name)
        except NameError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        set_(name, value)


ns = _Namespace()
