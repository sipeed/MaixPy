---
title: MaixCAM MaixPy Barcode Recognition
update:
  - date: 2024-12-16
    author: lxowalle
    version: 1.0.0
    content: Initial documentation
              
---

Before reading this article, make sure you know how to develop with MaixCAM. For details, please read [Quick Start](../README.md).

## Introduction

This article explains how to use MaixPy for Barcode recognition.


## Using MaixPy to Recognize Barodes

MaixPy's `maix.image.Image` includes the `find_barcodes` method for Barcode recognition.

### How to Recognize Barcodes

A simple example that recognizes Barcodes and draws a bounding box:

```python
from maix import image, camera, display

cam = camera.Camera(480, 320)
disp = display.Display()

while 1:
    img = cam.read()

    barcodes = img.find_barcodes()
    for b in barcodes:
        rect = b.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE, 2)
        img.draw_string(0, 0, "payload: " + b.payload(), image.COLOR_GREEN)

    disp.show(img)
```

Steps:

1. Import the image, camera, and display modules:

   ```python
   from maix import image, camera, display
   ```

2. Initialize the camera and display:

   ```python
   cam = camera.Camera(480, 320) # Initialize the camera with a resolution of 480x320 in RGB format
   disp = display.Display()
   ```

3. Capture and display images from the camera:

   ```python
   while 1:
       img = cam.read()
       disp.show(img)
   ```

4. Use the `find_barcodes` method to detect barcodes in the camera image:

   ```python
   barcodes = img.find_barcodes()
   ```

   - `img` is the camera image captured by `cam.read()`. When initialized as `cam = camera.Camera(480, 320)`, the `img` object is a 480x320 resolution RGB image.
   - `img.find_barcodes` searches for barcodes and saves the results in `barcodes` for further processing.
   - Note: The spacing of barcodes is small, and the width of barcodes is generally much larger than the height, so when adjusting the recognition rate and speed, you can try to make the width of the target image larger and the height smaller.

5. Process and display the results of barcode recognition on the screen:

   ```python
   for b in barcodes:
       rect = b.rect()
       img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE, 2)
       img.draw_string(0, 0, "payload: " + b.payload(), image.COLOR_GREEN)
   ```
   
   - `barcodes` is the result of querying barcodes by `img.find_barcodes()`, if no barcode is found then `barcodes` is empty.
   - `b.rect()` is used to get the position and size of the scanned barcode, `img.draw_rect()` uses the position information to draw the shape of the barcode.
   - `img.draw_string` is used to display the content and position of the barcode, `b.payload()` is used to get the content of the barcode.


### 常用参数说明

List common parameters and their explanations. If you cannot find parameters that fit your application, consider whether to use a different algorithm or extend the functionality based on the current algorithm's results.

| Parameter | Description                                                         | Example                                                         |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| roi  | Sets the rectangular area for the algorithm to compute, where roi=[x, y, w, h], x and y denote the top-left coordinates of the rectangle, and w and h denote the width and height of the rectangle, defaulting to the entire image. | Compute the area with coordinates (50,50) and width and height of 100:<br />`img.find_barcodes(roi=[50, 50, 100, 100])` |

This article introduces common methods. For more API details, refer to the [image](../../../api/maix/image.md) section of the API documentation.