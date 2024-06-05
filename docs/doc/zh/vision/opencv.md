---
title: Use OpenCV
---

## Introduction

For MaixCAM, since it uses Linux and the performance can support using the Python version of OpenCV, you can use the `cv2` module directly in addition to the `maix` module.

The examples in this article and more can be found in [MaixPy/examples/vision/opencv](https://github.com/sipeed/MaixPy/tree/main/examples/vision/opencv).

**Note that OpenCV functions are basically CPU-calculated. If you can use maix modules, try not to use OpenCV, because many maix functions are hardware-accelerated.**

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
    t = time.time_ms()
    edged = cv2.Canny(img, 180, 60)
    t2 = time.time_ms() - t

    # show by maix.display
    t = time.time_ms()
    img_show = image.cv2image(edged)
    print(f"edge time: {t2}ms, convert time: {time.time_ms() - t}ms")
    disp.show(img_show)
```

## Use Camera

On a PC, we use OpenCV's `VideoCapture` class to read from the camera. For MaixCAM, OpenCV does not support this directly, so we use the `maix.camera` module to read from the camera and then use it with OpenCV.

Convert a `maix.image.Image` object to a `numpy.ndarray` object using the `image.image2cv` function:

```python
from maix import image, display, app, time, camera
import cv2

disp = display.Display()
cam = camera.Camera(320, 240)

while not app.need_exit():
    img = cam.read()

    # convert maix.image.Image object to numpy.ndarray object
    t = time.time_ms()
    img = image.image2cv(img)
    print("time: ", time.time_ms() - t)

    # canny method
    edged = cv2.Canny(img, 180, 60)

    # show by maix.display
    img_show = image.cv2image(edged)
    disp.show(img_show)
```

