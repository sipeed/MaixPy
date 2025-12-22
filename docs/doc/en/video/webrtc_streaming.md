---
title: MaixCAM MaixPy Video Streaming WebRTC Push Streaming
update:
  - date: 2025-12-12
    author: 916BGAI
    version: 1.0.0
    content: Initial documentation
---

<br/>

> WebRTC streaming requires a browser that supports the WebRTC protocol. Please use the latest version of Chrome for testing.

## Introduction

This document explains how to push camera video using WebRTC.

## Usage

```python
from maix import time, webrtc, camera, image

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
server = webrtc.WebRTC()
server.bind_camera(cam)
server.start()

print(server.get_url())

while True:
    time.sleep(1)
```

Steps:

1. Import the `time`, `webrtc`, `camera`, and `image` modules

   ```python
   from maix import time, webrtc, camera, image
   ```

2. Initialize the camera

   ```python
   # Initialize the camera with output resolution 640x480 and NV21 format

   cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
   ```

   - Note: The WebRTC module currently only supports NV21 format, so the camera must be configured to output NV21.

3. Initialize and start the WebRTC server

   ```python
   server = webrtc.WebRTC()
   server.bind_camera(cam)
   server.start()
   ```

   - `server = webrtc.WebRTC()` creates a `WebRTC` instance.
   - `server.bind_camera(cam)` binds a `Camera` instance to the WebRTC server. After binding, the original `Camera` object should no longer be used directly.
   - `server.start()` starts the WebRTC streaming service.

4. Print the WebRTC stream URL

   ```python
   print(server.get_url())
   ```

   - `server.get_url()` returns the playback URL for the WebRTC stream.

5. Done — after running the script above, open the printed URL in your browser to view the camera stream.
