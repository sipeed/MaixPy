---
title: MaixPy QR Code Recognition
update:
  - date: 2024-04-03
    author: lxowalle
    version: 1.0.0
    content: Initial document
---

Before reading this article, make sure you are familiar with how to develop with MaixCAM. For details, please read [Quick Start](../README.md).

## Introduction

This article explains how to use MaixPy for QR code recognition.

## Using MaixPy to Recognize QR Codes

MaixPy's `maix.image.Image` includes the `find_qrcodes` method for QR code recognition.

### How to Recognize QR Codes

A simple example that recognizes QR codes and draws a bounding box:

```python
from maix import image, camera, display

cam = camera.Camera(320, 240)
disp = display.Display()

while True:
    img = cam.read()
    qrcodes = img.find_qrcodes()
    for qr in qrcodes:
        corners = qr.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        img.draw_string(qr.x(), qr.y() - 15, qr.payload(), image.COLOR_RED)
    disp.show(img)
```

Steps:

1. Import the image, camera, and display modules:

   ```python
   from maix import image, camera, display
   ```

2. Initialize the camera and display:

   ```python
   cam = camera.Camera(320, 240)  # Initialize the camera with a resolution of 320x240 in RGB format
   disp = display.Display()
   ```

3. Capture and display images from the camera:

   ```python
   while True:
       img = cam.read()
       disp.show(img)
   ```

4. Use the `find_qrcodes` method to detect QR codes in the camera image:

   ```python
   qrcodes = img.find_qrcodes()
   ```

   - `img` is the camera image captured by `cam.read()`. When initialized as `cam = camera.Camera(320, 240)`, the `img` object is a 320x240 resolution RGB image.
   - `img.find_qrcodes` searches for QR codes and saves the results in `qrcodes` for further processing.

5. Process and display the results of QR code recognition on the screen:

   ```python
   for qr in qrcodes:
       corners = qr.corners()
       for i in range(4):
           img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
       img.draw_string(qr.x(), qr.y() - 15, qr.payload(), image.COLOR_RED)
   ```

   - `qrcodes` contains the results from `img.find_qrcodes()`. If no QR codes are found, `qrcodes` will be empty.
   - `qr.corners()` retrieves the coordinates of the four corners of the detected QR code. `img.draw_line()` uses these coordinates to draw the QR code outline.
   - `img.draw_string` displays information about the QR code content and position. `qr.x()` and `qr.y()` retrieve the x and y coordinates of the QR code's top-left corner, and `qr.payload()` retrieves the content of the QR code.

### Common Parameter Explanation

List common parameters and their explanations. If you cannot find parameters that fit your application, consider whether to use a different algorithm or extend the functionality based on the current algorithm's results.

| Parameter | Description                                                  | Example                                                      |
| --------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| roi       | Sets the rectangular area for the algorithm to compute, where roi=[x, y, w, h], x and y denote the top-left coordinates of the rectangle, and w and h denote the width and height of the rectangle, defaulting to the entire image. | Compute the area with coordinates (50,50) and width and height of 100:<br />`img.find_qrcodes(roi=[50, 50, 100, 100])` |

This article introduces common methods. For more API details, refer to the [image](../../../api/maix/image.md) section of the API documentation.
