---
title: LVGL GUI
update:
  - date: 2026-11-09
    author: Tao
    version: 1.0.0
    content: Initial document
---

## Introduction

MaixPy provides the [LVGL](https://lvgl.io/) 9.1.0 Python bindings through the `maix_lvgl` module. The API is close to the MicroPython `lvgl` binding:

```python
import maix_lvgl as lv
```

`maix_lvgl` is built by MaixCDK's LVGL component and is already installed with the MaixPy wheel, so **no separate installation is needed**.

API documentation:

- [lvgl module](/api/maix_lvgl/lvgl.html)
- [lvgl functions](/api/maix_lvgl/lvgl_functions.html)
- [lvgl classes](/api/maix_lvgl/lvgl_classes.html)
- [maix_lvgl backend](/api/maix_lvgl/maix_lvgl.html)

## Quick start

```python
import time
from maix import app, display, touchscreen
import maix_lvgl as lv

disp = display.Display()
ts = touchscreen.TouchScreen()

try:
    lv.init(disp, ts)                 # pass MaixPy display and touchscreen

    scr = lv.screen_active()
    btn = lv.button(scr)
    btn.set_size(240, 120)
    btn.center()

    label = lv.label(btn)
    label.set_text("Hello MaixCAM2")

    def on_click(event):
        label.set_text("Clicked!")

    btn.add_event_cb(on_click, lv.EVENT.CLICKED, None)

    while not app.need_exit():
        lv.timer_handler()            # advances the LVGL tick
        time.sleep(0.005)
finally:
    lv.deinit()
    ts.close()
    disp.close()
```

A button is shown in the center of the screen. Tapping it changes the label to `Clicked!`.

## Initialization and main loop

`lv.init(display, touchscreen)` accepts the MaixPy `maix.display.Display` and `maix.touchscreen.TouchScreen` objects:

- `lv.init()` opens the display and touchscreen automatically.
- `lv.init(disp, False)` uses the display without touch input.

Call `lv.timer_handler()` in the main loop. This is the `maix_lvgl` version: it advances `lv_tick_inc()` using the monotonic clock before running LVGL's timer handler. **Do not use the raw `lvgl.timer_handler()`**, otherwise the tick never advances and clicks/animations stop working.

Call `lv.deinit()` when finished. If you created `display`/`touchscreen` yourself, close them separately.

## Widgets

```python
scr = lv.screen_active()

# Label
label = lv.label(scr)
label.set_text("Hello")
label.center()

# Button with a label
btn = lv.button(scr)
btn.set_size(240, 120)
btn.center()
btn_label = lv.label(btn)
btn_label.set_text("Click me")
btn_label.center()

# Slider
slider = lv.slider(scr)
slider.set_size(200, 20)
slider.center()

# Switch
sw = lv.switch(scr)
sw.center()
```

Event callbacks use the same style as LVGL:

```python
def on_click(event):
    print("clicked")

btn.add_event_cb(on_click, lv.EVENT.CLICKED, None)
```

## Display and touch

- The display driver renders LVGL into a BGRA8888 buffer and shows it with `display.show()`.
- Touch coordinates are processed by the MaixPy touch driver and already use the 640×480 screen coordinate system.
- Only one `maix.display.Display` user is allowed at a time. Stop the launcher or other apps before running.
- Tap targets must be large enough; very small buttons are easy to miss.

## Notes

- **JPEG images**: jpegio is not compiled in (it depends on LVGL 9.5 internals, which are not available in 9.1.0), so `lv.image` JPEG decoding is unavailable.
- **Chinese text**: only Montserrat fonts are enabled (matching MaixCDK's LVGL configuration). Chinese glyphs require a CJK bitmap font or FreeType.
- **Version**: LVGL 9.1.0, generated with [omnipython-lvgl](https://github.com/PyDevices/omnipython-lvgl).
- When building MaixPy yourself, `setup.py` builds `maix_lvgl` and packages it into the MaixPy wheel.
