---
title: MaixPy Camera Usage
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: Initial documentation
---

## Introduction

For the MaixCAM, it comes with a pre-installed GC4653 camera, or an optional OS04A10 camera or global shutter camera, and even an HDMI to MIPI module, all of which can be directly used with simple API calls.

## API Documentation

This article introduces common methods. For more API usage, refer to the documentation of the [maix.camera](/api/maix/camera.html) module.

## Camera Switching

Different cameras use different drivers, and the correct driver needs to be selected in the system.

TODO: How to switch between cameras, such as between GC4653 and OS04A10.

## Getting Images from the Camera

Using MaixPy to easily get images:
```python
from maix import camera

cam = camera.Camera(640, 480)

while 1:
    img = cam.read()
    print(img)
```

Here we import the `camera` module from the `maix` module, then create a `Camera` object, specifying the width and height of the image. Then, in a loop, we continuously read the images. The default output is in `RGB` format. If you need `BGR` format or other formats, please refer to the API documentation.

## Skipping Initial Frames

During the brief initialization period of the camera, the image acquisition may not be stable, resulting in strange images. You can use the `skip_frames` function to skip the initial few frames:
```python
cam = camera.Camera(640, 480)
cam.skip_frames(30)           # Skip the first 30 frames
```

## Displaying Images

MaixPy provides the `display` module, which can conveniently display images:
```python
from maix import camera, display

cam = camera.Camera(640, 480)
disp = display.Display()

while 1:
    img = cam.read()
    disp.show(img)
```
