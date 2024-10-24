---
title: MaixCAM MaixPy Use OpenCV
---

## Introduction

For MaixCAM, since it uses Linux and the performance can support using the Python version of OpenCV, you can use the `cv2` module directly in addition to the `maix` module.

The examples in this article and more can be found in [MaixPy/examples/vision/opencv](https://github.com/sipeed/MaixPy/tree/main/examples/vision/opencv).

**Note that OpenCV functions are basically CPU-calculated. If you can use maix modules, try not to use OpenCV, because many maix functions are hardware-accelerated.**

## Converting between Numpy/OpenCV and maix.image.Image Formats

You can convert `maix.image.Image` object to a `numpy` array, which can then be used by libraries such as `numpy` and `opencv`:

```python
from maix import image, time, display, app

disp = display.Display()

while not app.need_exit():
    img = image.Image(320, 240, image.Format.FMT_RGB888)
    img.draw_rect(0, 0, 100, 100, image.COLOR_RED, thickness=-1)
    t = time.ticks_ms()
    img_bgr = image.image2cv(img, ensure_bgr=True, copy=True)
    img2   = image.cv2image(img_bgr, bgr=True, copy=True)
    print("time:", time.ticks_ms() - t)
    print(type(img_bgr), img_bgr.shape)
    print(type(img2), img2)
    print("")
    disp.show(img2)
```

The previous program is slower because each conversion involves a memory copy. Below is an optimized version for better performance. However, it is not recommended to use this unless you are aiming for extreme speed, as it is prone to errors:

```python
from maix import image, time, display, app

disp = display.Display()

while not app.need_exit():
    img = image.Image(320, 240, image.Format.FMT_RGB888)
    img.draw_rect(0, 0, 100, 100, image.COLOR_RED, thickness=-1)

    t = time.ticks_ms()
    img_rgb = image.image2cv(img, ensure_bgr=False, copy=False)
    img2 = image.cv2image(img_rgb, bgr=False, copy=False)
    print("time:", time.ticks_ms() - t)
    print(type(img_rgb), img_rgb.shape)
    print(type(img2), img2)

    disp.show(img2)
```

* In `img_rgb = image.image2cv(img, ensure_bgr=False, copy=False)`, `img_rgb` directly uses the data from `img` without creating a memory copy. Note that the obtained `img_rgb` is an `RGB` image. Since OpenCV APIs assume the image is `BGR`, you need to be careful when using OpenCV APIs to process the image. If you are not sure, set `ensure_bgr` to `True`.
* In `img2 = image.cv2image(img_rgb, bgr=False, copy=False)`, setting `copy` to `False` means `img2` directly uses the memory of `img_rgb` without creating a new memory copy, resulting in faster performance. However, be cautious because `img_rgb` must not be destroyed before `img2` finishes using it; otherwise, the program will crash.
* Note that since memory is borrowed, modifying the converted image will also affect the original image.


## Load an Image

```python
import cv2

file_path = "/maixapp/share/icon/detector.png"
img = cv2.imread(file_path)
print(img)
```

Since the `cv2` module is quite large, `import cv2` may take some time.

## Display Image on Screen

To display an image on the screen, convert it to a `maix.image.Image` object and then use `display` to show it:

```python
from maix import display, image, time
import cv2

disp = display.Display()

file_path = "/maixapp/share/icon/detector.png"
img = cv2.imread(file_path)

img_show = image.cv2image(img)
disp.show(img_show)

while not app.need_exit():
    time.sleep(1)
```

## Use OpenCV Functions

For example, edge detection:

Based on the code above, use the `cv2.Canny` function:

```python
from maix import image, display, app, time
import cv2

file_path = "/maixapp/share/icon/detector.png"
img0 = cv2.imread(file_path)

disp = display.Display()

while not app.need_exit():
    img = img0.copy()

    # canny method
    t = time.ticks_ms()
    edged = cv2.Canny(img, 180, 60)
    t2 = time.ticks_ms() - t

    # show by maix.display
    t = time.ticks_ms()
    img_show = image.cv2image(edged)
    print(f"edge time: {t2}ms, convert time: {time.ticks_ms() - t}ms")
    disp.show(img_show)
```

## Use Camera

On a PC, we use OpenCV's `VideoCapture` class to read from the camera. For MaixCAM, OpenCV does not support this directly, so we use the `maix.camera` module to read from the camera and then use it with OpenCV.

Convert a `maix.image.Image` object to a `numpy.ndarray` object using the `image.image2cv` function:

```python
from maix import image, display, app, time, camera
import cv2

disp = display.Display()
cam = camera.Camera(320, 240, image.Format.FMT_BGR888)

while not app.need_exit():
    img = cam.read()

    # convert maix.image.Image object to numpy.ndarray object
    t = time.ticks_ms()
    img = image.image2cv(img, ensure_bgr=False, copy=False)
    print("time: ", time.ticks_ms() - t)

    # canny method
    edged = cv2.Canny(img, 180, 60)

    # show by maix.display
    img_show = image.cv2image(edged, bgr=True, copy=False)
    disp.show(img_show)
```


## Read USB camera

First, in the development board settings, select `USB Mode` under `USB Settings` and set it to `HOST` mode. If there is no screen available, you can use the `examples/tools/maixcam_switch_usb_mode.py` script to set it.

```python
from maix import image, display, app
import cv2
import sys

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

disp = display.Display()

if not cap.isOpened():
    print("无法打开摄像头")
    sys.exit(1)
print("开始读取")
while not app.need_exit():
    ret, frame = cap.read()
    if not ret:
        print("无法读取帧")
        break
    img = image.cv2image(frame, bgr=True, copy=False)
    disp.show(img)
```

