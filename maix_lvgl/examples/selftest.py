"""Render one LVGL frame through MaixPy and save it as a PNG.

Useful for hardware smoke tests without a long-running UI:

    python selftest.py

The PNG is written to /tmp/maix_lvgl_selftest.png.
"""
import time

from maix import display, image, touchscreen

import maix_lvgl as lv

OUTPUT = "/tmp/maix_lvgl_selftest.png"


def main():
    disp = display.Display()
    ts = touchscreen.TouchScreen()
    driver = lv.init(disp, ts)

    scr = lv.screen_active()
    btn = lv.button(scr)
    btn.center()
    label = lv.label(btn)
    label.set_text("maix_lvgl 9.1.0")

    lv.timer_handler()
    lv.refr_now(driver._disp)

    img = image.from_bytes(
        driver.width,
        driver.height,
        image.Format.FMT_BGRA8888,
        bytes(driver._buffer),
        True,
    )
    img.save(OUTPUT)
    print("saved:", OUTPUT, img.width(), img.height())

    lv.deinit()


if __name__ == "__main__":
    main()
