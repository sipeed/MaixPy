---
title: MaixCAM MaixPy QR Code Recognition
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

| Parameter    | Description                                                  | Example                                                      |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| roi          | Sets the rectangular area for the algorithm to compute, where roi=[x, y, w, h], x and y denote the top-left coordinates of the rectangle, and w and h denote the width and height of the rectangle, defaulting to the entire image. | Compute the area with coordinates (50,50) and width and height of 100:<br />`img.find_qrcodes(roi=[50, 50, 100, 100])` |
| qrcoder_type | Set the QR code library decoder type; you can choose either `image.QRCodeDecoderType.QRCODE_DECODER_TYPE_ZBAR` or `image::QRCodeDecoderType::QRCODE_DECODER_TYPE_QUIRC`. `QRCODE_DECODER_TYPE_ZBAR` offers faster recognition speed and higher accuracy at lower resolutions. `QRCODE_DECODER_TYPE_QUIRC` is relatively faster at higher resolutions but with slightly lower accuracy. By default, `QRCODE_DECODER_TYPE_ZBAR` is used.<br />Effective in version 4.7.7 and later. | img.find_qrcodes(decoder_type=image.QRCodeDecoderType.QRCODE_DECODER_TYPE_ZBAR) |

This article introduces common methods. For more API details, refer to the [image](../../../api/maix/image.md) section of the API documentation.

## Using Hardware Acceleration for QR Code Detection

MaixPy includes a built-in `image.QRCodeDetector` object that can use hardware acceleration for QR code detection. At a resolution of 320x224, the maximum frame rate for a single-frame algorithm can reach 60+ fps.

> Note: This feature is supported in MaixPy v4.7.9 and later versions

### Usage

```python
from maix import camera, display, app, image

cam = camera.Camera(320, 224)
disp = display.Display()
detector = image.QRCodeDetector()

while not app.need_exit():
    img = cam.read()

    qrcodes = detector.detect(img)
    for q in qrcodes:
        img.draw_string(0, 0, "payload: " + q.payload(), image.COLOR_BLUE)

    disp.show(img)
```

Steps:

1. Import the `image`, `camera`, and `display` modules:

   ```python
   from maix import camera, display, app, image
   ```

2. Capture and display the image:

   ```python
   cam = camera.Camera(320, 224)
   disp = display.Display()
   
   while not app.need_exit():
       img = cam.read()
       disp.show(img)
   ```

   - Create `Camera` and `Display` objects. Use the `cam.read()` method to capture the image and the `disp.show()` method to display it.

3. Create a `QRCodeDetector` object for QR code detection:

   ```python
   detector = image.QRCodeDetector()
   ```

4. Use the `detect` method to detect QR codes, saving the results in the `qrcodes` variable:

   ```python
   qrcodes = detector.detect(img)
   for q in qrcodes:
       img.draw_string(0, 0, "payload: " + q.payload(), image.COLOR_BLUE)
   ```

   - Note: The detection process will utilize NPU resources. If other models are using the NPU at the same time, it may cause unexpected results.
   - The structure of the detection result is the same as the data returned by `find_qrcodes`. Refer to the `QRCode` object's methods to access the detection results. For example, calling `q.payload()` will retrieve the QR code's content string.
