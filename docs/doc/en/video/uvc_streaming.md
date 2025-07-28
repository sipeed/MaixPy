---
title: MaixCAM MaixPy Video Streaming UVC Streaming / As a UVC camera to display custom image
update:
  - date: 2024-12-20
    author: taorye
    version: 1.0.0
    content: 初版文档
---

## Introduction

`MaixCAM` as a `UVC camera`, where `UVC` stands for `USB video(device) class`.

Here, two methods are provided to display custom content:

- Refresh the target image using the `show` method of `maix.uvc.UvcStreamer` (supports YUYV and MJPEG).
- Refresh the target image by registering a custom image refresh callback function with `maix.uvc.UvcServer` (only supports MJPEG). Much more complex than the method above.


## Example

**First, you need to enable the `UVC` function in the `USB settings` section of the `Settings` app.**

After connecting the USB cable:

- Windows users can go to Settings → Bluetooth & devices → Cameras, and see the UVC Camera device. Clicking on it will preview a static image of a small cat.

- Linux users need to download the `guvcview` software, select the resolution of 320x240 and the format as MJPG. You will see two cats with some garbled characters in between (this happens because the actual resolution of the cat image is 224x224, and the software automatically tries to fill the remaining space with another thing). Simply use the correct resolution normally.

Note: The version of guvcview used in Ubuntu 22 and earlier systems is `2.0.7`, which is known that the colors are displayed incorrectly, with a strong green tint. To fix it, please upgrade to a higher version. The version currently in use by the author is `2.2.1`. Ubuntu/Debian users can try to find a relevant PPA (Personal Package Archive) to install a newer version of guvcview.

**Note:**  
Once the `UVC` function is enabled, due to Linux's implementation of the `UVC Gadget`, a user program is still required to handle `UVC` device events.  
Otherwise, the entire `USB` functionality will pause and wait, affecting other simultaneously enabled `Gadget` features like `Rndis` and `NCM`, which may cause network disconnection.  
Therefore, for users who also need other `USB` functionalities, it is recommended to use the `UvcStreamer` method when developing UVC display functionality based on `MaixPy`.  
Otherwise, ensure that the `MaixCAM` device has other network access methods, such as `WIFI`, to ensure proper development and debugging.

<video controls autoplay src="../../assets/maixcam-pro_uvcdemo.mp4" type="video/mp4"> Your browser does not support video playback. </video>

### UvcStreamer

This method does not affect normal USB functionality. The underlying principle is to split the task into two processes. The official implementation uses a `server` process to handle `UVC` device events and encapsulates an easy-to-use, unified image refresh interface `show(img)` for users. You can treat it as a simple `display` linear logic operation.

**Reference example source code path:**  
`MaixPy/examples/vision/streaming/uvc_stream.py`

### **Example Source (Usage Instructions):**

1. **Initialize the UvcStreamer object**

```python
uvcs = uvc.UvcStreamer()
```

- (Optional) Switch to MJPEG streaming mode (YUYV default)

```python
uvcs.use_mjpg(1)
```

2. Refresh the image (automatically handles the format, medium performance loss for MJPEG, and high loss for YUYV)

```python
uvcs.show(img)
```

### UvcServer

This approach offers high performance with a single-process implementation, but USB functionality will only be available when the process is running. Therefore, when stopping this process, it's important to note that the enabled `Rndis` and `NCM` functionalities will temporarily become inactive, causing a network disconnection.

**Reference example source code path:**  
`MaixPy/examples/vision/streaming/uvc_server.py`

**Also packaged as an app source code path:**  
`MaixCDK/projects/app_uvc_camera/main/src/main.cpp`

### **Example Source (Usage Instructions):**

1. **Initialize the UvcServer object (requires a callback function for image refresh)**

A helper function `helper_fill_mjpg_image` is provided to assist in placing more general `Image` objects into the `UVC` buffer.

```python
cam = camera.Camera(640, 360, fps=60)   # Manually set resolution
                                        # | 手动设置分辨率

def fill_mjpg_img_cb(buf, size):
    img = cam.read()
    return uvc.helper_fill_mjpg_image(buf, size, img)

uvcs = uvc.UvcServer(fill_mjpg_img_cb)
```
The reference implementation will `fill_mjpg_img_cb` only trigger a buffer refresh when it returns `0`.  
Therefore, it is recommended to use the helper function in the last line:
`return uvc.helper_fill_mjpg_image(buf, size, img)`

2. Start the UVC, which launches a background thread, non-blocking operation:

```python
uvcs.run()
```

3. Stop the UVC when it's no longer needed. This will restore the background process from the `UvcStreamer` method implementation to ensure normal USB functionality.

Currently, there is a **BUG** in the MaixPy framework where it forcibly terminates processes upon exit, preventing the functions after the `while not app.need_exit():` loop from being executed, meaning the `stop()` method may not run as expected.  
Therefore, for users who require **normal USB functionality**, it is recommended to switch to the `UvcStreamer` method or use the original C++ API from **MaixCDK**.  

**Reference example:**  
`MaixCDK/examples/uvc_demo/main/src/main.cpp`

```python
uvcs.stop()
```
