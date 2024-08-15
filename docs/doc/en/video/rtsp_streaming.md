---
title: MaixCAM MaixPy Video Streaming RTSP Push Streaming
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: Initial documentation
---

## Introduction

This document provides methods for pushing streaming camera image via RTSP

## How to use

```python
from maix import time, rtsp, camera, image

server = rtsp.Rtsp()
cam = camera.Camera(2560, 1440, image.Format.FMT_YVU420SP)
server.bind_camera(cam)
server.start()

print(server.get_url())

while True:
    time.sleep(1)
```

Steps:

1. Import the image、camera、image and rtsp modules:

   ```python
   from maix import time, rtsp, camera, image
   ```

2. Initialize the camera:

   ```python
   cam = camera.Camera(2560, 1440, image.Format.FMT_YVU420SP) # Initialise camera, output resolution 2560x1440 NV21 format
   ```
   - Note that the RTSP module currently only supports the NV21 format, so the camera needs to be configured to output in NV21 format.

3. Initialise and start the Rtsp object

   ```python
   server = rtsp.Rtsp()
   server.bind_camera(cam)
   server.start()
   ```

   - ``server = rtsp.Rtsp()`` used to create an ``Rtsp`` object
   - `server.bind_camera(cam)` is used to bind a `Camera` object, after which the original `Camera` object can no longer be used.
   - `server.start()` is used to start the `rtsp` push stream.

4. Print the URL of the current RTSP stream

   ``python
   print(server.get_url())
   ``

   - ``server.get_url()`` is used to get the ``playback address`` of ``RTSP``.

6. Finished, after running the above code, you can play the video stream through [VLC](https://www.videolan.org/vlc/) software, the tested version of `VLC` is `3.0.20`. The default playback address is `rtsp://device ip:8554/live`.

## OSD

Drawing lines and frames via OSD

TODO