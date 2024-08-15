---
title: MaixCAM MaixPy Line Tracking Robot (/Car)
update:
  - date: 2024-05-09
    author: lxowalle
    version: 1.0.0
    content: Initial documentation
---

Before reading this article, make sure you know how to develop with MaixCAM. For details, please read [Quick Start](../README.md).

## Introduction

This article describes how to implement a line tracking robot using MaixPy.

## How to implement line tracking robot using MaixPy

1. Preparation of MaixCAM and trolley
2. Implementing the line tracking function
3. Implement the trolley control function

### Preparation of MaixCAM and trolley

TODO

### Implementing the line tracking function

You can quickly find straight lines using the `get_regression` of the `image` module, see [Line tracking](. /line_tracking.md).

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

### Implement the trolley control function

TODO

