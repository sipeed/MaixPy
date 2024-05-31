---
title: MaixPy / MaixCAM Touchscreen Usage Guide
---

## Introduction

MaixCAM comes equipped with a touchscreen, which, when used in conjunction with applications, can facilitate numerous engaging functionalities. We can utilize APIs to detect touch interactions on the touchscreen.

## Reading Touch Input with MaixPy

MaixPy offers a straightforward `maix.touchscreen.TouchScreen` class for reading touch inputs. Here's an example:

```python
from maix import touchscreen, app, time

ts = touchscreen.TouchScreen()

pressed_already = False
last_x = 0
last_y = 0
last_pressed = False
while not app.need_exit():
    x, y, pressed = ts.read()
    if x != last_x or y != last_y or pressed != last_pressed:
        print(x, y, pressed)
        last_x = x
        last_y = y
        last_pressed = pressed
    if pressed:
        pressed_already = True
    else:
        if pressed_already:
            print(f"clicked, x: {x}, y: {y}")
            pressed_already = False
    time.sleep_ms(1)  # sleep some time to free some CPU usage
```

## Interactivity with the Screen

Integrating the screen can enable various interactive user experiences. More examples can be found in the [MaixPy/examples/vision/touchscreen](https://github.com/sipeed/MaixPy) directory.

As previously described, to display content on the screen, typically, a `maix.image.Image` object is created and displayed using `disp.show(img)`. Implementing a button is as simple as drawing one on the image and then detecting touches within its area, ensuring that the image's dimensions match those of the screen:

```python
from maix import touchscreen, app, time, display, image

ts = touchscreen.TouchScreen()
disp = display.Display()

img = image.Image(disp.width(), disp.height())

# draw exit button
exit_label = "< Exit"
size = image.string_size(exit_label)
exit_btn_pos = [0, 0, 8*2 + size.width(), 12 * 2 + size.height()]
img.draw_string(8, 12, exit_label, image.COLOR_WHITE)
img.draw_rect(exit_btn_pos[0], exit_btn_pos[1], exit_btn_pos[2], exit_btn_pos[3], image.COLOR_WHITE, 2)

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

while not app.need_exit():
    x, y, pressed = ts.read()
    if is_in_button(x, y, exit_btn_pos):
        app.set_exit_flag(True)
    img.draw_circle(x, y, 1, image.Color.from_rgb(255, 255, 255), 2)
    disp.show(img)
```

## Handling Different Screen and Image Sizes

In the example above, the `img` matches the screen size. If your `img` and screen sizes differ (e.g., using `img = image.Image(240, 240)` on a `640x480` screen), the default behavior of `disp.show(img)` is `image.Fit.FIT_CONTAIN`, which scales the image to `480x480` and fills the sides with black. If a button is drawn on the `240x240` image, such as at coordinates `(0, 0, 60, 40)`, the button will also be scaled up. Thus, the coordinates for touch detection should be adjusted to `((640 - 480) / 2, 0, 480/240*60, 480/240*40)`, which translates to `(80, 0, 120, 80)`.

For convenience in scaling images and quickly calculating the positions and sizes of points or rectangles in the scaled image, the `image.resize_map_pos` function is provided:

```python
from maix import touchscreen, app, time, display, image

ts = touchscreen.TouchScreen()
disp = display.Display()

img = image.Image(240, 240)
img.draw_rect(0, 0, img.width(), img.height(), image.COLOR_WHITE)

# draw exit button
exit_label = "< Exit"
size = image.string_size(exit_label)
exit_btn_pos = [0, 0, 8*2 + size.width(), 12 * 2 + size.height()]
img.draw_string(8, 12, exit_label, image.COLOR_WHITE)
img.draw_rect(exit_btn_pos[0], exit_btn_pos[1], exit_btn_pos[2], exit_btn_pos[3],  image.COLOR_WHITE, 2)
# 图像按键坐标映射到屏幕上的坐标
exit_btn_disp_pos = image.resize_map_pos(img.width(), img.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, exit_btn_pos[0], exit_btn_pos[1], exit_btn_pos[2], exit_btn_pos[3])

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

while not app.need_exit():
    x, y, pressed = ts.read()
    if is_in_button(x, y, exit_btn_disp_pos):
        app.set_exit_flag(True)
    # 屏幕的坐标映射回图像上对应的坐标，然后在图像上画点
    x, y = image.resize_map_pos_reverse(img.width(), img.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, x, y)
    img.draw_circle(x, y, 1, image.Color.from_rgb(255, 255, 255), 2)
    disp.show(img, fit=image.Fit.FIT_CONTAIN)
```