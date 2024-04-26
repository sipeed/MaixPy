---
title: MaixPy Human Body Keypoint Detection for Pose Estimation
---

## Introduction

Using MaixPy, you can easily detect the coordinates of human joint keypoints, which can be used for pose estimation such as sitting posture detection, motion-controlled game input, and more.

## Usage

Using the `maix.nn.BodyKeyPoints` class in MaixPy, you can easily implement this functionality:

```python
from maix import nn, image, camera, display

detector = nn.BodyKeyPoints(model="/root/models/body_key_points.mud")
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    points = detector.detect(img)
    for point in points:
        img.draw_circle(point[0], point[1], 3, color=image.COLOR_RED, thickness=-1)
    dis.show(img)
```
