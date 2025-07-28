---
title: MaixCAM MaixPy Camera Usage
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: Initial version of the document
  - date: 2024-08-21
    author: YWJ
    version: 1.0.1
    content: Fixed some bugs in the document, added some content
  - date: 2024-10-24
    author: neucrack
    version: 1.1.0
    content: Added USB camera support instructions
  - date: 2025-07-28
    author: neucrack & lxo
    version: 1.2.0
    content: Add AWB and lens usage doc.
---

## Introduction

MaixCAM comes with a default GC4653 camera or optional OS04A10 camera, global shutter camera, or even HDMI to MIPI module, all of which can be used directly through simple API calls.

## API Documentation

This document introduces commonly used methods. For more API usage, please refer to the documentation of the [maix.camera](/api/maix/camera.html) module.

## Camera Switching

Currently supported cameras:

* **GC4653**: M12 universal lens, 1/3" sensor, clear image quality, 4M pixels. Suitable for common scenarios such as AI recognition and image processing.
* **OS04A10**: M12 universal lens, 1/1.8" large sensor, ultra-high image quality, 4M pixels. Suitable for scenarios that require high image quality, such as photography and video recording. Note that it generates more heat.
* **OV2685**: Lens is not replaceable, 1/5" sensor, 2M pixels, lowest image quality and cost. Generally not recommended.
* **SC035HGS**: Monochrome global shutter camera, 0.3M monochrome pixels, suitable for capturing fast-moving objects.

The system will switch automatically; just replace the hardware to use.

## Lens Cap

The lens cap is for dust protection. **Please remove the lens cap!!** before use.

## Adjusting Camera Focus

MaixCAM is equipped with a **manual focus lens** by default. You can physically rotate the lens to adjust focus.
If you find the **image is blurry**, try rotating the lens (clockwise and counterclockwise) to focus until the image is clear.

## Getting Image from the Camera

Use MaixPy to easily acquire images:

```python
from maix import camera

cam = camera.Camera(640, 480)

while 1:
    img = cam.read()
    print(img)
```

Here we import the `camera` module from `maix`, create a `Camera` object with specified width and height, and then continuously read images in a loop. The default image format is `RGB`. For `BGR` or other formats, see the API documentation.

You can also get grayscale images:

```python
from maix import camera, image
cam = camera.Camera(640, 480, image.Format.FMT_GRAYSCALE)	# Set output to grayscale image
```

Or get NV21 images:

```python
from maix import camera, image
cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)	# Set output to NV21 image
```

## Set Camera Resolution

Specify width and height directly in the code:

```python
from maix import camera
cam = camera.Camera(width=640, height=480)
```

or

```python
from maix import camera
cam = camera.Camera()
cam.set_resolution(width=640, height=480)
```

### Choosing Resolution Size

Different boards and camera modules support different resolutions. Make sure to use **even number values**.

It’s important to understand that **higher resolution is not always better**—choose the right resolution based on your scenario:

* Photography/Video/Monitoring: Higher resolution can give clearer images.
  GC4653 and OS04A10 support up to `2560x1440` resolution (i.e. `2K/4M pixels`). But high resolution demands more programming skill and memory. You may consider smaller resolutions such as `1920x1080`, `1280x720`, `640x480`, etc.
  Note: When running code in **MaixVision**, if you set high resolution (e.g., `2560x1440`), disable the image preview feature in MaixVision to avoid errors due to insufficient memory.
* AI Recognition / Image Processing: For faster performance, reduce resolution as much as possible while still ensuring recognizability.

  * `640x480`: VGA resolution; large enough for most AI recognition and clear image processing. Demands more from MaixCAM; easier for MaixCAM2.
  * `320x320`: Square resolution; suitable for some AI models, but will have black borders on rectangle screens.
  * `320x240`: QVGA resolution; easy for algorithms, and still meets clarity needs.
  * `320x224`: Both width and height are multiples of 32; suitable for small resolution AI input and displays well on `552x368` screen.
  * `224x224`: Square, both dimensions are multiples of 32; fits small resolution AI models like `MobileNetV2`, `MobileNetV3`.

### Aspect Ratio of Resolution

Aspect ratio affects field of view. For example, sensor max is `2560x1440` (16:9). Using `640x480` changes to 4:3, reducing field of view. To maximize view, choose resolution matching sensor's aspect ratio, e.g., `1280x720`, `2560x1440`.

Different ratios will result in center cropping.

## Set Camera Frame Rate

The camera operates at specific frame rates. MaixPy supports frame rate settings. Supported frame rates vary by module:

| GC4653                                                 | OS04A10                             | OV2685           | SC035HGS        |
| ------------------------------------------------------ | ----------------------------------- | ---------------- | --------------- |
| 2560x1440\@30fps<br>1280x720\@60fps<br>1280x720\@80fps | 2560x1440\@30fps<br>1280x720\@80fps | 1920x1080\@30fps | 640x480\@180fps |

Frame rate is set via `width`, `height`, and `fps` when creating `Camera`.

### Set Frame Rate to 30fps

```python
from maix import camera
cam = camera.Camera(640, 480, fps=30)
# or
cam = camera.Camera(1920, 1280)  # Above 1280x720 will auto use 30fps
```

### Set Frame Rate to 60fps

```python
from maix import camera
cam = camera.Camera(640, 480, fps=60)
# or
cam = camera.Camera(640, 480)  # ≤1280x720 defaults to 80fps
```

### Set Frame Rate to 80fps

```python
from maix import camera
cam = camera.Camera(640, 480, fps=80)
```

Notes:

1. If size > `1280x720`, e.g., `camera.Camera(1920, 1080, fps=60)`, then `fps` param is ignored and stays at 30fps.
2. 60/80fps images may shift by a few pixels compared to 30fps—consider correcting this if precise alignment is needed.
3. 60/80fps and 30fps share ISP config—image quality may vary slightly.
4. Some camera setups can't handle 80fps—may show visual artifacts. Switch back to 60fps if needed.

## Image Correction

For fisheye or distortion, use `lens_corr` under `Image` to correct. Adjust the `strength` value for best results.

```python
from maix import camera, display, app, time

cam = camera.Camera(320, 240)
disp = display.Display()
while not app.need_exit():
    t = time.ticks_ms()
    img = cam.read() 
    img = img.lens_corr(strength=1.5)  # Adjust strength until distortion is gone
    disp.show(img)
```

Note: This is software-based correction and consumes time. You may also use non-distorted lenses (ask vendor).

## Skip Initial Frames

During initialization, camera may output unstable images. Skip first few frames using `skip_frames`:

```python
cam = camera.Camera(640, 480)
cam.skip_frames(30)           # Skip first 30 frames
```

## Display Camera Image

MaixPy provides the `display` module for easy image display:

```python
from maix import camera, display

cam = camera.Camera(640, 480)
disp = display.Display()

while 1:
    img = cam.read()
    disp.show(img)
```

## Set Camera Parameters

### Set Exposure Time

Note: Setting exposure time switches to manual exposure. To revert to auto mode, run `cam.exp_mode(camera.AeMode.Auto)`

```python
from maix import camera
cam = camera.Camera()
cam.exposure(1000)
```

### Set Gain

Note: Setting gain switches to manual exposure. Custom gain only works in manual mode.

```python
from maix import camera
cam = camera.Camera()
cam.gain(100)
```

### Set White Balance

Usually auto white balance suffices. For color-sensitive scenarios, manually set it:

Set `awb_mode` to `Manual`, then set gain for `R`, `Gr`, `Gb`, `B` channels. Range: `[0.0, 1.0]`.

Default gain values:

* `MaixCAM`: `[0.134, 0.0625, 0.0625, 0.1239]`
* `MaixCAM2`: `[0.0682, 0, 0, 0.04897]`

Usually only `R` and `B` need adjustment.

```python
from maix import camera
cam = camera.Camera()
cam.awb_mode(camera.AwbMode.Manual)
cam.set_wb_gain([0.134, 0.0625, 0.0625, 0.1239])
```

### Setting Lower Capture Latency
You can reduce image capture latency by setting the buff_num parameter. However, note that changing this parameter affects the image buffer size, and setting it too low may lead to image loss.

For MaixCam, due to limitations in the internal software framework, even if buff_num is set to 1, there will still be at least a double-buffering mechanism in place. In testing, the minimum achievable capture latency is around 30+ ms.

```python
from maix import camera
cam = camera.Camera(buff_num=1)         # Use only 1 buffer
```

### Set Brightness, Contrast, Saturation

```python
from maix import camera
cam = camera.Camera()
cam.luma(50)		    # Brightness [0, 100]
cam.constrast(50)		# Contrast [0, 100]
cam.saturation(50)		# Saturation [0, 100]
```

### Read Raw Image

To read raw `bayer` image data for processing or debugging:

```python
from maix import camera
cam = camera.Camera(raw=true)
raw_img = cam.read_raw()
print(raw_img)
```

For viewing on PC, use script like [bayer\_to\_tiff](https://github.com/sipeed/MaixPy/blob/dev/examples/tools/bayer_to_tiff.py).

## Change Lens

MaixCAM uses M12 lens by default and supports lens replacement. Notes:

1. Ensure new lens is M12.
2. Different lenses have different flange back distances. Default lens mount has fixed height—check compatibility.
3. Avoid scratching sensor surface. Blow dust gently, clean with lens paper only if necessary.
4. Want a zoom lens? Buy M12 zoom lens.
5. Default is manual focus. Auto-focus lenses require driver support; MaixCAM lacks AF circuit—you may need to write control program.

## Use USB Camera

Besides built-in MIPI camera, you can use USB camera.

Steps:

* Set `USB Mode` to `HOST` in system settings. Without screen, use script `examples/tools/maixcam_switch_usb_mode.py`.
* As of 2024.10.24, `maix.camera` module **does not** support USB camera. Refer to [Using USB Camera with OpenCV](./opencv.md).

