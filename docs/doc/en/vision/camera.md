---
title: MaixCAM MaixPy Camera Usage
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

Currently supported cameras:
* **GC4653**: M12 universal lens, 1/3" sensor, clear image quality, 4MP.
* **OS04A10**: M12 universal lens, 1/1.8" large sensor, ultra-clear image quality, 4MP.
* **OV2685**: Does not support lens replacement, lowest image quality, and lowest cost; generally not recommended for use.
* **SC035HGS**: Monochrome global shutter camera, 0.3MP black-and-white, suitable for capturing high-speed objects.

The system will automatically switch; simply replace the hardware to use.

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

The GC4653 supports a maximum of three configurations: `2560x1440 30fps`, `1280x720 60fps`, and `1280x720 80fps`. The frame rate is selected based on the width, height, and fps parameters passed when creating the Camera object.

The OS04A10 supports a maximum of two configurations: `2560x1440 30fps` and `1280x720 90fps`. The `1280x720` resolution is achieved by center-cropping the `2560x1440` image.

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
4. The camera's performance depends on the system. Some systems may not support setting the camera to 80fps, which can result in strange patterns appearing on the screen. In such cases, please switch back to the normal 60fps setting.

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

Note that since the correction is done through software, it takes some time. Alternatively, you can use a distortion-free lens (inquire with the vendor) to solve the issue from a hardware perspective.

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

### Reading Raw Images

Note that the output `raw` image is the original `Bayer` image, and the format of the `Bayer` image may vary depending on the camera module.

```python
cam = camera.Camera(raw=true)
raw_img = cam.read_raw()
print(raw_img)
```

If you need to open the `raw` image in third-party software, additional conversion on the PC side is required. You can refer to the example code in [bayer_to_tiff](https://github.com/sipeed/MaixPy/blob/dev/examples/tools/bayer_to_tiff.py).



## Using a USB Camera

In addition to using the MIPI interface camera that comes with the development board, you can also use an external USB camera.
Method:
* First, in the development board settings, select `USB Mode` under `USB Settings` and set it to `HOST` mode. If there is no screen available, you can use the `examples/tools/maixcam_switch_usb_mode.py` script to set it.
* Currently (as of 2024.10.24), the `maix.camera` module does not yet support USB cameras, but you can use `OpenCV` for this.

```python
from maix import image, display
import cv2
import sys

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

disp = display.Display()

if not cap.isOpened():
    print("Unable to open camera")
    sys.exit(1)
print("Starting to read")
while True:
    ret, frame = cap.read()
    if not ret:
        print("Unable to read frame")
        return
    img = image.cv2image(frame, bgr=True, copy=False)
    disp.show(img)
```

