"""LVGL drivers for MaixPy display and touchscreen.

The display driver renders LVGL into a Python ``bytearray`` (BGRA8888, which
matches LVGL's 32-bit ARGB8888 output on little-endian targets) and pushes it
to ``maix.display.Display`` with ``show()``. The touch driver feeds
``maix.touchscreen.TouchScreen`` events into an LVGL pointer indev.
"""
from __future__ import annotations

import time

import lvgl as lv

from maix import display as maix_display
from maix import image as maix_image
from maix import touchscreen as maix_touchscreen

_BGRA8888 = maix_image.Format.FMT_BGRA8888


class DisplayDriver:
    """Bind one LVGL display to a MaixPy display object."""

    def __init__(self, display=None, width=None, height=None):
        self._owned_display = display is None
        if display is None:
            if width is None or height is None:
                probe = maix_display.Display()
                size = probe.size()
                probe.close()
                width = size[0] if width is None else width
                height = size[1] if height is None else height
            display = maix_display.Display(width, height, _BGRA8888)
        self.display = display
        self.width = display.width()
        self.height = display.height()

        # LVGL paints directly into this buffer. It is full-screen so a flush
        # callback can hand the whole frame to MaixPy without stitching areas.
        self._buffer = bytearray(self.width * self.height * 4)
        self._disp = lv.display_create(self.width, self.height)
        self._disp.set_color_format(lv.COLOR_FORMAT.ARGB8888)
        self._disp.set_buffers(
            self._buffer, None, len(self._buffer), lv.DISPLAY_RENDER_MODE.FULL
        )
        self._disp.set_flush_cb(self._flush)
        # Input devices attach to the default display (LVGL sets it on
        # lv_indev_create); make this display the default explicitly.
        self._disp.set_default()

        # The LVGL tick is advanced from maix_lvgl.timer_handler() on the
        # main thread. lv_tick_set_cb can't be used here: that API takes no
        # user_data, so the generated CPython binding does not keep the
        # Python callback alive and the tick would stay at 0.

    def _flush(self, disp, area, px):
        if disp.flush_is_last():
            # ARGB8888 in LVGL is byte-ordered B,G,R,A on little-endian, which
            # is exactly MaixPy's FMT_BGRA8888.
            img = maix_image.from_bytes(
                self.width,
                self.height,
                _BGRA8888,
                bytes(self._buffer),
                True,
            )
            self.display.show(img, maix_image.Fit.FIT_FILL)
        disp.flush_ready()

    def deinit(self):
        if self._disp is not None:
            try:
                self._disp.delete()
            except Exception:
                pass
            self._disp = None
        if self._owned_display and self.display is not None:
            try:
                self.display.close()
            except Exception:
                pass
            self.display = None


class TouchDriver:
    """Bind a MaixPy touchscreen to an LVGL pointer indev."""

    def __init__(self, touchscreen=None, display=None):
        self._owned_touchscreen = touchscreen is None
        if touchscreen is None:
            touchscreen = maix_touchscreen.TouchScreen()
        self.touchscreen = touchscreen
        self._indev = lv.indev_create()
        self._indev.set_type(lv.INDEV_TYPE.POINTER)
        # LVGL skips an indev whose display is NULL, so bind it explicitly.
        if display is not None:
            self._indev.set_display(display)
        self._indev.set_read_cb(self._read)

    def _read(self, indev, data):
        # TouchScreen.read() returns [x, y, pressed] in display coordinates;
        # MaixCDK already applies the panel's axis mapping.
        values = None
        try:
            values = self.touchscreen.read()
        except Exception:
            values = None
        if values and len(values) >= 3:
            x, y, pressed = values[0], values[1], values[2]
        else:
            x, y, pressed = 0, 0, 0
        data.point.x = int(x)
        data.point.y = int(y)
        data.state = (
            lv.INDEV_STATE.PRESSED if pressed else lv.INDEV_STATE.RELEASED
        )

    def deinit(self):
        if self._indev is not None:
            try:
                self._indev.delete()
            except Exception:
                pass
            self._indev = None
        if self._owned_touchscreen and self.touchscreen is not None:
            try:
                self.touchscreen.close()
            except Exception:
                pass
            self.touchscreen = None
