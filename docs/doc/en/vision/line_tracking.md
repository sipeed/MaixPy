---
title: MaixCAM MaixPy Line Tracking
update:
  - date: 2024-05-09
    author: lxowalle
    version: 1.0.0
    content: Initial document
---


Before reading this article, make sure you already know how to develop MaixCAM. For details, please read [Quick Start](../README.md).

## Introduction

In vision applications, the function of tracking line is often required in applications such as line-following robot. In this article, we will describe:

- How to use MaixPy to tracking line.

- How to tracking line using MaixCam's default application


## How to use MaixPy to tracking line

The `maix.image.Image` module in MaixPy provides the `get_regression` method, which can conveniently tracking line.

### Code example

A simple example of finding and drawing a line.

```python
from maix import camera, display, image

cam = camera.Camera(320, 240)
disp = display.Display()

# thresholds = [[0, 80, 40, 80, 10, 80]] # red
thresholds = [[0, 80, -120, -10, 0, 30]] # green
# thresholds = [[0, 80, 30, 100, -120, -60]] # blue

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

Steps:

1. import image, camera, display modules

   ```python
   from maix import image, camera, display
   ```

2. Initialize camera and display

   ```python
   cam = camera.Camera(320, 240) # Initialise camera, output resolution 320x240 in RGB format.
   disp = display.Display()
   ```

3. Get the image from the camera and display it

   ```python
   while 1:
       img = cam.read()
       disp.show(img)
   ```

4. Call the `get_regression` method to find the straight line in the camera image and draw it to the screen

   ```python
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
   ```

   - `img` is the camera image read via `cam.read()`, when initialised as `cam = camera.Camera(320, 240)`, the `img` object is an RGB image with a resolution of 320x240.
   - `img.get_regression` is used to find straight lines, `thresholds` is a list of colour thresholds, each element is a colour threshold, multiple thresholds are passed in if multiple thresholds are found at the same time, and each colour threshold has the format `[L_MIN, L_MAX, A_MIN, A_MAX, B_MIN, B_MAX]`, where ` L`, `A`, `B` are the three channels of `LAB` colour space, `L` channel is the luminance, `A` channel is the red-green channel, `B` channel is the blue-yellow channel. `pixels_threshold` is a pixel area threshold used to filter some unwanted straight lines.
   - `for a in lines` is used to iterate through the returned `Line` objects, where `a` is the current `Line` object. Normally the `get_regression` function will only return one `Line` object, but if you need to find more than one line, try the `find_line` method.
   - Use `img.draw_line` to draw the found line, `a.x1(), a.y1(), a.x2(), a.y2()` represent the coordinates of the ends of the line.
   - Use `img.draw_string` to show the angle between the line and the x-axis in the upper left corner, and `a.theta()` is the angle between the line and the y-axis, which is converted to `theta` for easier understanding, `a.rho()` is the length of the vertical line from the origin to the line.

5. Run the code through the maixvision, you can find the line, look at the effect!

    ![image-20240509110204007](../../../static/image/line_tracking_demo.jpg)

### Common Parameter Explanations

Here are explanations of commonly used parameters. If you cannot find parameters that can implement your application, you may need to consider using other algorithms or extending the required functionality based on the current algorithm's results.

| Parameter        | Description                                                  | Example                                                      |
| ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| thresholds       | Thresholds based on the LAB color space, thresholds=[[l_min, l_max, a_min, a_max, b_min, b_max]], representing:<br/>Brightness range [l_min, l_max]<br/>Green to red component range [a_min, a_max]<br/>Blue to yellow component range [b_min, b_max]<br/>Multiple thresholds can be set simultaneously | Set two thresholds to detect red and green<br/>```img.find_blobs(thresholds=[[0, 80, 40, 80, 10, 80], [0, 80, -120, -10, 0, 30]])```<br/>Red threshold is [0, 80, 40, 80, 10, 80]<br/>Green threshold is [0, 80, -120, -10, 0, 30] |
| invert           | Enable threshold inversion, when enabled, the passed thresholds are inverted. Default is False. | Enable threshold inversion<br/>```img.find_blobs(invert=True)``` |
| roi              | Set the rectangular region for the algorithm to compute, roi=[x, y, w, h], where x and y represent the coordinates of the top-left corner of the rectangle, and w and h represent the width and height of the rectangle, respectively. The default is the entire image. | Compute the region at (50, 50) with a width and height of 100<br/>```img.find_blobs(roi=[50, 50, 100, 100])``` |
| area_threshold   | Filter out blobs with a pixel area smaller than area_threshold, in units of pixels. The default is 10. This parameter can be used to filter out some useless small blobs. | Filter out blobs with an area smaller than 1000<br/>```img.find_blobs(area_threshold=1000)``` |
| pixels_threshold | Filter out blobs with fewer valid pixels than pixels_threshold. The default is 10. This parameter can be used to filter out some useless small blobs. | Filter out blobs with fewer than 1000 valid pixels<br/>```img.find_blobs(pixels_threshold=1000)``` |

This article introduces commonly used methods. For more APIs, please see the [image](../../../api/maix/image.md) section of the API documentation.

### Increasing the speed of line tracking

Here are a few ways to increase the speed of line tracking

1. Choose a suitable resolution

   The larger the resolution, the slower the calculation speed, you can choose a more suitable resolution according to the recognition distance and accuracy requirements.

2. Use gray scale image

   When using gray scale recognition, the algorithm will only process one channel, there is a faster recognition speed, in the environment of a single color will be very useful. Note that only `l_min` and `l_max` are valid when passing `thresholds` to `get_regression` when using gray scale image recognition.

   Methods for get gray scale image:

   ```python
   # Example 1
   cam = camera.Camera(320, 240， image.Format.FMT_GRAYSCALE)    	# Support after MaixPy v4.2.1
   gray_img = cam.read()											# get gray scale image
   
   # Example 2
   cam = camera.Camera(320, 240)
   img = cam.read()
   gray_img = img.to_format(image.Format.FMT_GRAYSCALE)			# get gray scale image
   ```

## How to tracking line using MaixCam's default application

To quickly verify the line tracking functionality, you can use the `line_tracking` application provided by MaixCam to experience the line finding effect.

### How to use it

1. Select and open the `Line tracking` application.
2. Click on the line in the screen that needs to be identified and the colour of the line will be displayed on the left hand side
3. Click on the colour to be detected on the left (the colour below L A B in the screen)
4. The line will be identified and the coordinates and angle of the line will be output from the serial port.

### Demo

<video src="/static/video/line_tracking_app.mp4" controls="controls" width="100%" height="auto"></video>
### Advanced operations

#### Manual adjustment of LAB threshold to tracking line

The application provides manual setting of LAB threshold to tracking line accurately.

Steps:

1. `Click` the `options icon` in the bottom-left corner to enter configuration mode.
2. Point the `camera` at the `object` you need to `find`, `click` on the `target object` on the screen, and the `left side` will display a `rectangular frame` of the object's color and show the `LAB values` of that color.
3. Click on the bottom options `L Min`, `L Max`, `A Min`, `A Max`, `B Min`, `B Max`. After clicking, a slider will appear on the right side to set the value for that option. These values correspond to the minimum and maximum values of the L, A, and B channels in the LAB color format, respectively.
4. Referring to the `LAB values` of the object color calculated in step 2, adjust `L Min`, `L Max`, `A Min`, `A Max`, `B Min`, `B Max` to appropriate values to identify the corresponding color blobs. For example, if `LAB = (20, 50, 80)`, since `L=20`, to accommodate a certain range, set `L Min=10` and `L Max=30`. Similarly, since `A=50`, set `A Min=40` and `A Max=60`. Since `B=80`, set `B Min=70` and `B Max=90`.

#### Getting Detection Data via Serial Protocol

The line tracking application supports reporting detected straight line information via the serial port (default baud rate is 115200).

Since only one report message is sent, we can illustrate the content of the report message with an example.

For instance, if the report message is:

```shell
AA CA AC BB 0E 00 00 00 00 E1 09 FC 01 01 00 E9 01 6F 01 57 00 C1 C6
```

- `AA CA AC BB`: Protocol header, fixed content
- `0E 00 00 00`: Data length, the total length excluding the protocol header and data length, here means the length is 14.
- `E1`: Flag bit, used to identify the serial message flag
- `09`: Command type, for the line tracking application, this value is fixed at 0x09.

- `FC 01 01 00 E9 01 6F 01 57 00`: The coordinates and angle information for both ends of  line, with each value represented as a 2-byte value in little-end format. `FC 01` and `01 00` indicate that the coordinates of the first endpoint are (508, 1), `E9 01` and `6F 01` indicate that the coordinates of the second endpoint are (489, 367), and `57 00` indicates that the angle of the line to the x-axis is 87 degrees
- `C1 C6`: CRC checksum value, used to verify if the frame data has errors during transmission.