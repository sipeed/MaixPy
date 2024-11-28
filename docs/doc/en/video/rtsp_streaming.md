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

## Support for Streaming Audio

MaixPy supports streaming both audio and video simultaneously. By binding a `Recorder` object,

> Note: This method is supported in MaixPy v4.7.9 and later versions

The following is an example code:

```python
from maix import time, rtsp, camera, image, audio

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
audio_recorder = audio.Recorder()

server = rtsp.Rtsp()
server.bind_camera(cam)
server.bind_audio_recorder(audio_recorder)
server.start()

print(server.get_url())

while True:
    time.sleep(1)
```

In the code above, an `audio_recorder` object is created using `audio.Recorder()`, and the `bind_audio_recorder()` method of the `Rtsp` server is used to bind this object. You can use `ffplay rtsp://<device-ip>:8554/live` or `vlc 3.0.20` to receive the audio and video stream.