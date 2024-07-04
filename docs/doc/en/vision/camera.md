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

```python
from maix import camera, image
cam = camera.Camera(640, 480, image.Format.FMT_GRAYSCALE) # Set the output greyscale image
```
Also get the NV21 image
```python
from maix import camera, image
cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP) # set to output NV21 image
```

Note: You need to disable MaixVision's online browsing function if you set a very high resolution (e.g. `2560x1440`), otherwise the code may run abnormally due to lack of memory.
You can also get greyscale images

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

## Setting the camera parameters

### Set exposure time

Note that after setting the exposure time, the camera will switch to manual exposure mode, if you want to switch back to automatic exposure mode you need to run `cam.exp_mode(0)`.

```python
cam = camera.Camera()
cam.exposure(1000)
```

### Setting the gain

Note that after setting the gain, the camera will switch to manual exposure mode, to switch back to auto exposure mode you need to run `cam.exp_mode(0)`. Customised gain values will only work in manual exposure mode.

```python
cam = camera.Camera()
cam.gain(100)
```

### Setting the white balance

TODO

### Setting brightness, contrast and saturation

```python
cam = camera.Camera()
cam.luma(50) # Set brightness, range [0, 100]
cam.constrast(50) # set contrast, range [0, 100]
cam.saturation(50) # Set the saturation, range [0, 100].
```