---
title: MaixPy 找色块
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
---

## 简介

在视觉应用中，找色块是一个非常常见的需求，比如机器人找色块，自动化生产线找色块等等。
即需要识别画面中的特定的颜色区域，获取这个区域的位置和大小等信息。


## 使用设备自带的找色块应用

打开设备，选择`找色块`应用，然后在下方选择要识别的颜色，或者自定义颜色，即可以识别到对应的颜色了，同时串口也会输出识别到的坐标和颜色信息。

<video src="/static/video/find_blobs.mp4" controls="controls" width="100%" height="auto"></video>

### 自定义颜色的方法

TODO：

### 串口协议

TODO：

## 使用 MaixPy 找色块

`maix.image.Image`中提供了`find_blobs`方法，可以方便的找色块。

```python
from maix import image, camera, display

cam = camera.Camera(320, 240)
disp = display.Display()

thresholds = [[0, 100, -120, -10, 0, 30]]

while 1:
    img = cam.read()
    blobs = img.find_blobs(thresholds)
    for blob in blobs:
        img.draw_rectangle(blob[0], blob[1], blob[2], blob[3], color=(255, 0, 0))
    disp.show(img)
```

这里的 `thresholds` 是一个颜色阈值列表，每个元素是一个颜色阈值，同时找到多个阈值就传入多个，每个颜色阈值的格式为 `[L_MIN, L_MAX, A_MIN, A_MAX, B_MIN, B_MAX]`，这里的 `L`、`A`、`B` 是`LAB`颜色空间的三个通道，`L` 通道是亮度，`A` 通道是红绿通道，`B` 通道是蓝黄通道。
可以在上面使用`找色块`应用中找到被检测物体对应的颜色阈值。

更多参数和用法请参考 API 文档。


