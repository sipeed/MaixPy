---
title: Line tracking robot
update:
  - date: 2024-05-09
    author: lxowalle
    version: 1.0.0
    content: Initial documentation
---

Before starting, complete the [Quick Start](../README.md) for your device and make sure MaixVision can run a camera example.

## Introduction

This page covers the vision part of a line-tracking robot: finding the track in the camera image and calculating its direction and position. Motor wiring, driver boards, and steering control depend on the chassis, so this page only explains how to pass the vision result to a control program.

## Detect the Track Line

You can quickly find straight lines using the `get_regression` of the `image` module, see [Line tracking](../vision/line_tracking.md).

Code：

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

The above code implements the function of finding a straight line, note:

- Use `a.theta()` to get the angle of the line.
- Use `a.rho()` to get the distance between the line and the origin (the origin is in the upper left corner).

After find the straight line with reference to the above code, you can use `a.theta()` and `a.rho()` to control the direction of the cart.

## Connect the Result to Motor Control

The code produces two useful values:

- `theta`: the line angle in the image, which indicates whether the robot should steer left or right.
- `rho`: the line's distance from the top-left image origin, which helps determine whether the track is offset from the image center.

Convert these values into left and right motor speeds, then send them through UART, PWM, or a motor driver. During the first test, lift the wheels off the ground and limit the speed. Confirm that steering moves in the expected direction before placing the robot on the track. Follow the chassis, motor, and driver-board documentation for wiring and safe speed limits.
