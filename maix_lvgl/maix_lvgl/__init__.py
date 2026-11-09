"""MaixPy + LVGL integration.

``maix_lvgl`` re-exports the generated LVGL bindings (``import lvgl as lv``)
and adds a thin MaixCAM2 backend:

.. code-block:: python

    from maix import app, display, touchscreen
    import maix_lvgl as lv

    lv.init(display.Display(), touchscreen.TouchScreen())

    scr = lv.screen_active()
    btn = lv.button(scr)
    btn.center()
    lv.label(btn).set_text("Hello MaixCAM2")

    while not app.need_exit():
        lv.timer_handler()
        time.sleep(0.005)

    lv.deinit()

The binding is generated from LVGL 9.1.0 (the version pinned by MaixCDK) with
the omnipython-lvgl generator. See README.md for build and regeneration notes.
"""
from __future__ import annotations

import ctypes
import os
import sys
import time

# The LVGL extension is built by MaixCDK's project.py and ships inside this
# package, together with the dynamic libraries MaixCDK's LVGL stack needs
# beyond the system ones (libdatachannel).
_pkg_dir = os.path.dirname(os.path.abspath(__file__))
_dl_dir = os.path.join(_pkg_dir, "dl_lib")
if os.path.isdir(_dl_dir):
    for _name in sorted(os.listdir(_dl_dir)):
        if ".so" in _name:
            try:
                ctypes.CDLL(os.path.join(_dl_dir, _name), mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass
if _pkg_dir not in sys.path:
    sys.path.insert(0, _pkg_dir)
try:
    import lvgl as _lvgl
finally:
    if _pkg_dir in sys.path:
        sys.path.remove(_pkg_dir)

from .driver import DisplayDriver, TouchDriver

__version__ = "0.1.0"

_display_driver = None
_touch_driver = None
_initialized = False
_last_tick = None


def init(display=None, touchscreen=None, width=None, height=None):
    """Initialize LVGL and attach MaixPy display/touchscreen.

    Args:
        display: a ``maix.display.Display`` instance. When omitted, a display
            is opened in ``FMT_BGRA8888`` using the panel size.
        touchscreen: a ``maix.touchscreen.TouchScreen`` instance. When omitted,
            a touchscreen is opened. Pass ``False`` to run without touch input.
        width/height: panel size used only when opening an internal display.

    Returns:
        The internal ``DisplayDriver``.
    """
    global _display_driver, _touch_driver, _initialized
    if _initialized:
        raise RuntimeError("maix_lvgl is already initialized")

    _lvgl.init()
    global _last_tick
    _last_tick = time.monotonic()
    _display_driver = DisplayDriver(display, width, height)
    if touchscreen is not False:
        _touch_driver = TouchDriver(touchscreen, _display_driver._disp)
    _initialized = True
    return _display_driver


def timer_handler():
    """Advance the LVGL tick and run one timer-handler pass.

    Use this instead of ``lvgl.timer_handler()``: the generated binding
    cannot keep the ``lv_tick_set_cb`` Python callback alive, so the tick is
    advanced here on the main thread.
    """
    global _last_tick
    now = time.monotonic()
    if _last_tick is None:
        _last_tick = now
    delta = int((now - _last_tick) * 1000)
    if delta > 0:
        _lvgl.tick_inc(delta)
        _last_tick = now
    return _lvgl.timer_handler()


def process():
    """Run one LVGL timer-handler pass and return its next delay (ms)."""
    return timer_handler()


def run(fps=60):
    """Run the LVGL loop until MaixPy asks the application to exit."""
    from maix import app

    period = 1.0 / fps
    while not app.need_exit():
        timer_handler()
        time.sleep(period)


def deinit():
    """Stop LVGL and release the display/touchscreen opened by :func:`init`."""
    global _display_driver, _touch_driver, _initialized
    if not _initialized:
        return
    if _touch_driver is not None:
        _touch_driver.deinit()
        _touch_driver = None
    if _display_driver is not None:
        _display_driver.deinit()
        _display_driver = None
    _lvgl.deinit()
    _last_tick = None
    _initialized = False


# Re-export every LVGL binding name so ``import maix_lvgl as lv`` behaves like
# ``import lvgl as lv`` (MicroPython-style API).
def __getattr__(name):
    return getattr(_lvgl, name)


def __dir__():
    return sorted(set(globals()) | set(dir(_lvgl)))


__all__ = [n for n in dir(_lvgl) if not n.startswith("_")] + [
    "init",
    "deinit",
    "run",
    "process",
    "timer_handler",
]
