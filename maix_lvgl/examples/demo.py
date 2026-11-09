"""Minimal MaixPy + LVGL demo.

Run on a MaixCAM2 while the launcher is stopped (development mode):

    python demo.py

The LVGL API is re-exported by maix_lvgl, so widgets are created exactly like
in the MicroPython LVGL binding (``import lvgl as lv``).
"""
import time

from maix import app, display, touchscreen

import maix_lvgl as lv


def main():
    disp = display.Display()
    ts = touchscreen.TouchScreen()

    lv.init(disp, ts)

    scr = lv.screen_active()

    btn = lv.button(scr)
    btn.set_size(240, 120)
    btn.center()
    label = lv.label(btn)
    label.set_text("Click me")
    label.center()

    counter = [0]

    def on_clicked(event):
        counter[0] += 1
        label.set_text(f"Clicked {counter[0]}")

    btn.add_event_cb(on_clicked, lv.EVENT.CLICKED, None)

    while not app.need_exit():
        lv.timer_handler()
        time.sleep(0.005)

    lv.deinit()


if __name__ == "__main__":
    main()
