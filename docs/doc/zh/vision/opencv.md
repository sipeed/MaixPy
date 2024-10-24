---
title: MaixCAM MaixPy 使用 OpenCV
---

## 简介

对于 MaixCAM，因为使用了 Linux， 并且性能基本能够支撑使用`Python`版本的`OpenCV`，所以除了使用`maix`模块，你也可以直接使用`cv2`模块。

本文例程以及更多可以在[MaixPy/examples/vision/opencv](https://github.com/sipeed/MaixPy/tree/main/examples/vision/opencv) 中找到。

**注意 OpenCV 的函数基本都是 CPU 计算的，能使用 maix 的模块尽量不使用 OpenCV，因为 maix 有很多函数都是经过硬件加速过的。**

## maix.image.Image 对象和 Numpy/OpenCV 格式互相转换

`maix.image.Image`对象可以转换成`numpy`数组，这样就能给`numpy`和`opencv`等库使用：

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

前面的程序因为每次转换都要拷贝一次内存，所以速度会比较慢，下面为优化速度版本，如果不是极限追求速度不建议使用，容易出错：

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

* `img_rgb = image.image2cv(img, ensure_bgr=False, copy=False)`中`img_rgb` 会直接使用 `img` 的数据，不会产生内存拷贝，注意此时得到的`img_rgb` 是 `RGB` 图，`opencv`的 API 都是认为图是 `BGR` 的，所以用`opencv`的 API 操作图像时要注意，如果你无法掌控请设置`ensure_bgr`为`True`。
* `img2 = image.cv2image(img_rgb, bgr=False, copy=False)`中设置了`copy`为`False`，即直接使用`img_rgb`的内存，不会新拷贝一份内存，所以速度更快了，但是需要小心，在 `img2` 使用结束前`img_bgr`不能被销毁，否则程序会崩溃。
* 注意因为借用了内存，所以更改转换后的图像也会影响到转换前的图像。


## 加载一张图片

```python
import cv2

file_path = "/maixapp/share/icon/detector.png"
img = cv2.imread(file_path)
print(img)
```

因为`cv2`模块比较臃肿，`import cv2`可能会需要一点时间。


## 显示图像到屏幕

但是由于直接使用了官方的 OpenCV，没有对接显示，所以要显示到屏幕上需要转换成`maix.image.Image`对象后再用`display`来显示：
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

## 使用 OpenCV 函数

以边缘检测为例：

基于上面的代码，使用`cv2.Canny`函数即可：

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

## 使用摄像头

在 PC 上， 我们使用 `OpenCV` 的`VideoCapture`类来读取摄像头，对于 `MaixCAM`, `OpenCV` 没有适配，我们可以用`maix.camera` 模块来读取摄像头，然后给`OpenCV`使用。

通过`image.image2cv`函数将`maix.image.Image`对象转为`numpy.ndarray`对象给`OpenCV`使用：

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

## 读取 USB 摄像头

先在开发板设置里面`USB设置`中选择`USB 模式`为`HOST`模式。如果没有屏幕，可以用`examples/tools/maixcam_switch_usb_mode.py`脚本进行设置。

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
