---
title: 使用 OpenCV
---

## 简介

对于 MaixCAM，因为使用了 Linux， 并且性能基本能够支撑使用`Python`版本的`OpenCV`，所以除了使用`maix`模块，你也可以直接使用`cv2`模块。

本文例程以及更多可以在[MaixPy/examples/vision/opencv](https://github.com/sipeed/MaixPy/tree/main/examples/vision/opencv) 中找到。

**注意 OpenCV 的函数基本都是 CPU 计算的，能使用 maix 的模块尽量不使用 OpenCV，因为 maix 有很多函数都是经过硬件加速过的。**

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
    t = time.time_ms()
    edged = cv2.Canny(img, 180, 60)
    t2 = time.time_ms() - t

    # show by maix.display
    t = time.time_ms()
    img_show = image.cv2image(edged)
    print(f"edge time: {t2}ms, convert time: {time.time_ms() - t}ms")
    disp.show(img_show)
```

## 使用摄像头

在 PC 上， 我们使用 `OpenCV` 的`VideoCapture`类来读取摄像头，对于 `MaixCAM`, `OpenCV` 没有适配，我们可以用`maix.camera` 模块来读取摄像头，然后给`OpenCV`使用。

通过`image.image2cv`函数将`maix.image.Image`对象转为`numpy.ndarray`对象给`OpenCV`使用：

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
