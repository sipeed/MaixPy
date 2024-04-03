---
title: MaixPy 摄像头使用
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
---


## 简介

对于 MaixCAM 默认搭载了 GC4653 摄像头，或者可选的 OS04A10 摄像头或者全局快门摄像头，甚至是 HDMI 转 MIPI 模块，都可以直接用简单的 API 调用。

## API 文档

本文介绍常用方法，更多 API 使用参考 [maix.camera](/api/maix/camera.html) 模块的文档。

## 摄像头切换

不同的摄像头使用不同的驱动，需要在系统中选择正确的驱动。

TODO：如何切换摄像头，比如 GC4653 和 OS04A10 之间的切换。


## 从摄像头获取图像

使用 MaixPy 轻松获取：
```python
from maix import camera

cam = camera.Camera(640, 480)

while 1:
    img = cam.read()
    print(img)
```

这里我们从`maix`模块导入`camera`模块，然后创建一个`Camera`对象，指定图像的宽度和高度。然后在一个循环中不断读取图像， 默认出的图为`RGB`格式，如果需要`BGR`格式，其它格式请看 API 文档。

## 跳过 开头的帧

摄像头初始化的一小段时间，可能图像采集还没稳定出现奇怪的画面，可以通过`skip_frames`函数跳过开头的几帧：
```python
cam = camera.Camera(640, 480)
cam.skip_frames(30)           # 跳过开头的30帧
```

## 显示图像

MaixPy 提供了`display`模块，可以方便的显示图像：
```python
from maix import camera, display

cam = camera.Camera(640, 480)
disp = display.Display()

while 1:
    img = cam.read()
    disp.show(img)
```


