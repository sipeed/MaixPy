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

## Setting the frame rate of the camera

Currently the camera supports `30fps`, `60fps` and `80fps` configurations, the frame rate is selected by the `width`, `height`, `fps` parameters passed when creating the `Camera` object, currently the maximum supported resolution is `1280x720` under `60/80fps`, and the maximum supported resolution is `2560x1440` under `30fps`.

### Setting the frame rate to 30 fps

```python
from maix import camera
cam = camera.Camera(640, 480, fps=30) # set the frame rate to 30 fps
# or
cam = camera.Camera(1920, 1280) # Frame rate is set to 30 fps when resolution is higher than 1280x720
```

### Set the frame rate to 60 fps

```python
from maix import camera
cam = camera.Camera(640, 480, fps=60) # Set frame rate to 60 fps
# or
cam = camera.Camera(640, 480) # Set frame rate to 60fps if resolution is less than or equal to 1280x720
```

### Set the frame rate to 80 fps

```python
from maix import camera
cam = camera.Camera(640, 480, fps=80) # Set frame rate to 60 fps
```

Notes:

1. if `Camera` is passed in a size larger than `1280x720`, for example written as `camera.Camera(1920, 1080, fps=60)`, then the `fps` parameter will be invalidated, and the frame rate will remain at `30fps`.
2. A `60/80fps` frame will be offset by a few pixels compared to a `30fps` frame, and the offset will need to be corrected if the viewing angle is critical.
3. Note that due to the fact that `60/80fps` and `30fps` share the same `isp` configuration, in some environments there will be some deviation in the quality of the screen at the two frame rates.

## Image correction

In case of distortion such as fisheye, you can use the `lens_corr` function under the `Image` object to correct the distortion of the image. In general, you just need to increase or decrease the value of `strength` to adjust the image to the right effect.

``python
from maix import camera, display

cam = camera.Camera(320, 240)
disp = display.Display()
while not app.need_exit():: t = time.
    t = time.ticks_ms()
    img = cam.read()
    img = img.lens_corr(strength=1.5) # Adjust the strength value until the image is no longer distorted.
    disp = display.Display()
``

TODO: Support for hardware distortion correction

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

```python
cam = camera.Camera()
cam.awb_mode(1)     # 0,turn on white balance;1,turn off white balance
```

### Setting brightness, contrast and saturation

```python
cam = camera.Camera()
cam.luma(50) # Set brightness, range [0, 100]
cam.constrast(50) # set contrast, range [0, 100]
cam.saturation(50) # Set the saturation, range [0, 100].
```