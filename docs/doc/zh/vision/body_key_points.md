---
title: MaixPy 检测人体关键点姿态检测
---


## 简介

使用 MaixPy 可以轻松检测人体关节的关键点的坐标，用在姿态检测比如坐姿检测，体感游戏输入等。

## 使用

使用 MaixPy 的 maix.nn.BodyKeyPoints 类可以轻松实现：

```python
from maix import nn, image, display

detector = nn.BodyKeyPoints(model="/root/models/body_key_points.mud")
cam = camera.Camera(recognizer.input_width(), recognizer.input_height(), recognizer.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    points = detector.detect(img)
    for point in points:
        img.draw_circle(point[0], point[1], 3, color = image.COLOR_RED, thickness=-1)
    dis.show(img)
```


