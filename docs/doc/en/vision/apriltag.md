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

### Distance Measurement 1: The vertical distance between the object and the camera.

This section describes a method to estimate the distance using the formula `distance = k / width`, where:
`distance`: Distance between the camera and the object in millimeters (mm).
`k`: A constant.
`width`: Width of the object in the image, measured in pixels.

**Advantages**: Simple and easy to understand, convenient for measurement.

**Disadvantages**: It can only measure the vertical distance between the tag and the camera. When the tag is tilted, the error increases.

The process consists of two steps:

1. Measure the constant coefficient `k`.
2. Calculate the distance between the camera and the object using the constant and the object's `width`.

#### Preparation

1. AprilTag paper for calibration.
2. A ruler (or other measuring tool).

#### Measuring the Constant Coefficient `k`

- Fix the AprilTag in place and set the camera (maixcam) at a distance of 20 cm from the tag.

- Use `maixcam` to detect the `AprilTag` and calculate the tag's `width`. Refer to the following code:

  ```python
  from maix import camera, display
  import math

  '''
  x1, y1, x2, y2: Coordinates of two points defining the tag's width, typically obtained using the corners() method.
  Returns the width of the tag in pixels.
  '''
  def caculate_width(x1, y1, x2, y2):
      return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

  cam = camera.Camera(160, 120)
  disp = display.Display()

  while 1:
      img = cam.read()

      apriltags = img.find_apriltags()
      for a in apriltags:
          corners = a.corners()

          # Calculate width using two horizontal corner points
          width = caculate_width(corners[0][0], corners[0][1], corners[1][0], corners[1][1])
          # Print the detected width of the AprilTag
          print(f'apriltag width:{width}')
      disp.show(img)
  ```

- Calculate the constant `k`:

  ```python
  '''
  width: Width of the AprilTag detected at a known distance.
  distance: The actual distance to the AprilTag during detection, in mm.
  Returns the constant coefficient.
  '''
  def caculate_k(width, distance):
      return width * distance
  
  # Example: At a distance of 200 mm, the tag width is detected as 43 pixels
  k = caculate_k(43, 200)
  ```

#### Calculate Distance Between Camera and Object Using `k`

```python
'''
width: Width of the AprilTag in pixels.
k: Constant coefficient.
Returns the distance between the camera and the object in mm.
'''
def caculate_distance(width, k):
    return k / width

distance = caculate_distance(55, 8600)
```

#### 完整的代码参考:

```python
from maix import camera, display, image
import math

'''
x1, y1, x2, y2: Coordinates of two points defining the tag's width, typically obtained using the corners() method.
Returns the width of the tag in pixels.
'''
def caculate_width(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

'''
width: Width of the AprilTag detected at a known distance.
distance: The actual distance to the AprilTag during detection, in mm.
Returns the constant coefficient.
'''
def caculate_k(width, distance):
    return width * distance

'''
width: Width of the AprilTag in pixels.
k: Constant coefficient.
Returns the distance between the camera and the object in mm.
'''
def caculate_distance(width, k):
    return k / width


cam = camera.Camera(192, 108)
disp = display.Display()

# Example: At a distance of 200 mm, the tag width is detected as 43 pixels
k = caculate_k(43, 200)

while 1:
    img = cam.read()

    apriltags = img.find_apriltags()
    for a in apriltags:
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_GREEN)

        # Calculate width using two horizontal corner points
        width = caculate_width(corners[0][0], corners[0][1], corners[1][0], corners[1][1])

        # Calculate distance
        distance = caculate_distance(width, k)

        print(f'apriltag width:{width} distance:{distance} mm')

    disp.show(img)

```

This method uses the width of the `AprilTag` to calculate the distance. It can also be extended to use height for distance calculation. However, note that this approach provides an estimate of the distance, and slight inaccuracies may occur due to real-world factors.

### Distance Measurement 2: Measuring the distance from the object to the camera using the AprilTag

By using the `apriltag` for distance measurement, we can accurately determine the position of the tag in space. In this case, we also use the parameters returned by the `find_apriltag()` method to calculate the position of any `AprilTag` relative to the camera. Of course, the prerequisite is that you must detect the `apriltag`.

The process consists of two steps:

1. Calculate the constant coefficient `k`.
2. Use the position information returned by `find_apriltag()` to calculate the distance from the tag to the camera.

**Advantages**: This method allows you to measure the distance between the `apriltag` and the camera even if the tag is rotated or offset relative to the camera.

#### Preparations:

1. `apriltag` paper tag.
2. Ruler (or other distance measuring tools).

#### Measuring the Constant Coefficient `k`:

- Fix the `apriltag` paper tag and place the `MaixCAM` at a distance of `20cm` from the `apriltag`.

- Use `MaixCAM` to detect the `apriltag` and calculate the constant coefficient using the `z_translation`. Reference code:

  ```python
  from maix import camera, display
  
  '''
  z_trans: The value of z_translation() when the distance is 'distance' (actual distance in mm).
  distance: The actual distance to the AprilTag when detected, in mm.
  Returns the constant coefficient 'k'.
  '''
  def caculate_k(z_trans, distance):
      return distance / z_trans
  
  cam = camera.Camera(160, 120)
  disp = display.Display()
  
  while 1:
      img = cam.read()
  
      apriltags = img.find_apriltags()
      for a in apriltags:
          k = caculate_k(a.z_translation(), 200)
          print(f"k:{k}")
      disp.show(img)
  ```

#### Measuring the Distance from the Tag to the Object:

- Calculate the distance from the `apriltag` to the camera using `x_translation`, `y_translation`, and `z_translation` returned by the `apriltag`:

  ```python
  '''
  x_trans: The value of x_translation() returned by detecting the AprilTag.
  y_trans: The value of y_translation() returned by detecting the AprilTag.
  z_trans: The value of z_translation() returned by detecting the AprilTag.
  k: Constant coefficient.
  Returns the distance in mm.
  '''
  def calculate_distance(x_trans, y_trans, z_trans, k):
      return k * math.sqrt(x_trans * x_trans + y_trans * y_trans + z_trans * z_trans)
  ```

#### Complete Code Example:

```python
from maix import camera, display, image
import math

'''
z_trans: The value of z_translation() when the distance is 'distance' (actual distance in mm).
distance: The actual distance to the AprilTag when detected, in mm.
Returns the constant coefficient 'k'.
'''
def caculate_k(z_trans, distance):
    return distance / z_trans

'''
x_trans: The value of x_translation() returned by detecting the AprilTag.
y_trans: The value of y_translation() returned by detecting the AprilTag.
z_trans: The value of z_translation() returned by detecting the AprilTag.
k: Constant coefficient.
Returns the distance in mm.
'''
def calculate_distance(x_trans, y_trans, z_trans, k):
    return abs(k * math.sqrt(x_trans * x_trans + y_trans * y_trans + z_trans * z_trans))

cam = camera.Camera(160, 120)
disp = display.Display()

# When the distance is 200mm, the detected z_translation() of the AprilTag is -9.7
k = caculate_k(-9.7, 200)

while 1:
    img = cam.read()

    apriltags = img.find_apriltags()
    for a in apriltags:
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_GREEN)

        # Calculate the distance
        x_trans = a.x_translation()
        y_trans = a.y_translation()
        z_trans = a.z_translation()
        distance = calculate_distance(x_trans, y_trans, z_trans, k)
        print(f'apriltag k:{k} distance:{distance} mm')

    disp.show(img)
```

This code uses the `MaixCAM` to continuously read the camera feed, detect the `apriltag`, and calculate the distance from the tag to the camera using the constant coefficient and the tag's translations in all three axes. The calculated distance is printed out in millimeters. Note that this approach provides an estimate of the distance, and slight inaccuracies may occur due to real-world factors.