---
title: 小车巡线
update:
  - date: 2024-05-09
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

开始前，请先完成对应设备的[快速开始](../README.md)，确保 MaixVision 能运行摄像头例程。

## 简介

本页先完成巡线小车中的视觉部分：从画面中找出轨迹线，并计算方向和位置。电机接线、驱动板和转向控制取决于具体底盘，本页只说明如何把识别结果交给控制程序。

## 识别轨迹线

使用`image`模块的`get_regression`可以快速寻找到直线，详情见[寻找直线](../vision/line_tracking.md)

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

## 接入小车控制

代码得到两个关键结果：

- `theta`：轨迹线相对画面的角度，可以用来判断车头应该向左还是向右修正。
- `rho`：轨迹线到画面左上角的距离，可以用来判断轨迹线是否偏离画面中心。

把这两个值换算成左右电机速度，再通过 UART、PWM 或电机驱动板输出。开始时应让轮子离地并限制最低速度，先确认转向方向正确，再把车放到地面测试。具体接线和速度范围请以底盘、电机和驱动板的说明书为准。
