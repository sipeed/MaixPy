---
title: MaixCAM MaixPy Apriltag Recognition
update:
  - date: 2024-04-03
    author: lxowalle
    version: 1.0.0
    content: Initial documentation
---

Before reading this article, make sure you are familiar with how to develop with MaixCAM. For more details, please read [Quick Start](../README.md).

## Introduction

This article introduces how to use MaixPy to recognize Apriltag labels.

## Using MaixPy to Recognize Apriltag Labels

MaixPy's `maix.image.Image` provides the `find_apriltags` method, which can be used to recognize Apriltag labels.

### How to Recognize Apriltag Labels

A simple example of recognizing Apriltag labels and drawing bounding boxes:

```python
from maix import image, camera, display

cam = camera.Camera()
disp = display.Display()

families = image.ApriltagFamilies.TAG36H11
x_scale = cam.width() / 160
y_scale = cam.height() / 120

while 1:
    img = cam.read()

    new_img = img.resize(160, 120)
    apriltags = new_img.find_apriltags(families = families)
    for a in apriltags:
        corners = a.corners()

        for i in range(4):
            corners[i][0] = int(corners[i][0] * x_scale)
            corners[i][1] = int(corners[i][1] * y_scale)
        x = int(a.x() * x_scale)
        y = int(a.y() * y_scale)
        w = int(a.w() * x_scale)
        h = int(a.h() * y_scale)

        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        img.draw_string(x + w, y, "id: " + str(a.id()), image.COLOR_RED)
        img.draw_string(x + w, y + 15, "family: " + str(a.family()), image.COLOR_RED)

    disp.show(img)
```

Steps:

1. Import the image, camera, and display modules

   ```python
   from maix import image, camera, display
   ```

2. Initialize the camera and display

   ```python
   cam = camera.Camera()
   disp = display.Display()
   ```

3. Get the image from the camera and display it

   ```python
   while 1:
       img = cam.read()
       disp.show(img)
   ```

4. Call the `find_apriltags` method to recognize Apriltag labels in the camera image

   ```python
   new_img = img.resize(160, 120)
   apriltags = new_img.find_apriltags(families = families)
   ```

   - `img` is the camera image obtained through `cam.read()`
   - `img.resize(160, 120)` is used to scale down the image to a smaller size, allowing the algorithm to compute faster with a smaller image
   - `new_img.find_apriltags(families = families)` is used to find Apriltag labels, and the query results are saved in `apriltags` for further processing. The `families` parameter is used to select the Apriltag family, defaulting to `image.ApriltagFamilies.TAG36H11`

5. Process the recognized label results and display them on the screen

   ```python
   for a in apriltags:
       # Get position information (and map coordinates to the original image)
       x = int(a.x() * x_scale)
       y = int(a.y() * y_scale)
       w = int(a.w() * x_scale)
       corners = a.corners()
       for i in range(4):
           corners[i][0] = int(corners[i][0] * x_scale)
           corners[i][1] = int(corners[i][1] * y_scale)
   
       # Display
       for i in range(4):
           img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
           img.draw_string(x + w, y, "id: " + str(a.id()), image.COLOR_RED)
           img.draw_string(x + w, y + 15, "family: " + str(a.family()), image.COLOR_RED)
           img.draw_string(x + w, y + 30, "rotation : " + str(180 * a.rotation() // 3.1415), image.COLOR_RED)
   ```

   - Iterate through the members of `apriltags`, which is the result of scanning Apriltag labels through `img.find_apriltags()`. If no labels are found, the members of `apriltags` will be empty.
   - `x_scale` and `y_scale` are used to map coordinates. Since `new_img` is a scaled-down image, the coordinates of the Apriltag need to be mapped to be drawn correctly on the original image `img`.
   - `a.corners()` is used to get the coordinates of the four vertices of the detected label, and `img.draw_line()` uses these four vertex coordinates to draw the shape of the label.
   - `img.draw_string` is used to display the label content, where `a.x()` and `a.y()` are used to get the x and y coordinates of the top-left corner of the label, `a.id()` is used to get the label ID, `a.family()` is used to get the label family type, and `a.rotation()` is used to get the rotation angle of the label.

### Common Parameter Explanations

Here are explanations for common parameters. If you can't find parameters to implement your application, you may need to consider using other algorithms or extending the required functionality based on the current algorithm's results.

| Parameter | Description                                                  | Example                                                      |
| --------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| roi       | Set the rectangular region for the algorithm to compute. roi=[x, y, w, h], where x and y represent the coordinates of the top-left corner of the rectangle, and w and h represent the width and height of the rectangle. The default is the entire image. | Compute the region with coordinates (50,50) and a width and height of 100:<br />```img.find_apriltags(roi=[50, 50, 100, 100])``` |
| families  | Apriltag label family type                                   | Scan for labels from the TAG36H11 family:<br />```img.find_apriltags(families = image.ApriltagFamilies.TAG36H11)``` |

This article introduces common methods. For more API information, please refer to the [image](../../../api/maix/image.md) section of the API documentation.
