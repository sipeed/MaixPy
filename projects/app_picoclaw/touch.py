from __future__ import annotations

import logging

from maix import touchscreen

logger = logging.getLogger(__name__)


class Touch:
    def __init__(self) -> None:
        self._ts = touchscreen.TouchScreen()
        self._was_pressed = False
        self._last_x = 0
        self._last_y = 0

    def update(self) -> tuple[int, int, bool]:
        """Poll the touchscreen once. Returns (x, y, pressed)."""
        x, y, pressed = self._ts.read()
        if pressed:
            self._last_x, self._last_y = x, y
        self._was_pressed = pressed
        return x, y, pressed

    def consume_press(self) -> tuple[int, int] | None:
        """Poll once. On rising edge (released -> pressed), return (x, y)."""
        was = self._was_pressed
        x, y, pressed = self.update()
        if pressed and not was:
            return (x, y)
        return None

    def is_pressing(self) -> bool:
        """Return last-known pressed state without polling the device."""
        return self._was_pressed

    def position(self) -> tuple[int, int]:
        return self._last_x, self._last_y

    @staticmethod
    def in_rect(point: tuple[int, int], rect: tuple[int, int, int, int]) -> bool:
        px, py = point
        rx, ry, rw, rh = rect
        return rx <= px < rx + rw and ry <= py < ry + rh

    def close(self) -> None:
        try:
            self._ts.close()
        except Exception:
            pass
