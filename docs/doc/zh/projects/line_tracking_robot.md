---
title: MaixCAM MaixPy 小车巡线
update:
  - date: 2024-05-09
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

阅读本文前，确保已经知晓如何开发MaixCAM，详情请阅读[快速开始](../README.md)

## 简介

本文将介绍如何使用MaixPy实现寻线小车

## 如何使用MaixPy实现寻线小车

1. 准备MaixCAM与小车
2. 实现寻线功能
3. 实现小车控制功能

### 准备MaixCAM与小车

TODO

### 实现寻线功能

使用`image`模块的`get_regression`可以快速寻找到直线，详情见[寻找直线](./line_tracking.md)

代码实现：

```python
from maix import camera, display, image

cam = camera.Camera(320, 240)
disp = display.Display()

# thresholds = [[0, 80, 40, 80, 10, 80]]      # red
thresholds = [[0, 80, -120, -10, 0, 30]]    # green
# thresholds = [[0, 80, 30, 100, -120, -60]]  # blue

while 1:
    img = cam.read()

    lines = img.get_regression(thresholds, area_threshold = 100)
    for a in lines:
        img.draw_line(a.x1(), a.y1(), a.x2(), a.y2(), image.COLOR_GREEN, 2)
        theta = a.theta()
        rho = a.rho()
        if theta > 90:
            theta = 270 - theta
        else:
            theta = 90 - theta
        img.draw_string(0, 0, "theta: " + str(theta) + ", rho: " + str(rho), image.COLOR_BLUE)

    disp.show(img)

```

上述代码实现了寻线功能， 上述参数中需注意：

- 设置合适的thresholds值来寻找到对应的直线
- 设置合适的area_threshold值来过滤环境干扰，可以过滤一些面积小的直线
- 使用`a.theta()`获取直线的角度
- 使用`a.rho()`获取直线与原点(原点在左上角)的距离

根据实际环境调试好寻线参数后， 就可以利用`a.theta()`和`a.rho()`控制小车方向了。

### 实现小车控制功能

TODO
