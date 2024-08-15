---
title: MaixCAM MaixPy Video Record
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: Initial document
---

## Introduction

This document provides instructions on how to use the video recording feature


## Example 1

An example of recording a video in `h265` format.

```python
from maix import video, image, camera, app, time

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
e = video.Encoder()
f = open('/root/output.h265', 'wb')

record_ms = 2000
start_ms = time.ticks_ms()
while not app.need_exit():
    img = cam.read()
    frame = e.encode(img)

    print(frame.size())
    f.write(frame.to_bytes())

    if time.ticks_ms() - start_ms > record_ms:
        app.set_exit_flag(True)
```

步骤：

1. import module and Initialize the camera

   ```python
   from maix import video, image, camera, app, time
   cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
   ```

   - `camera.Camera()` is used to initialise the camera, here the camera resolution is initialised to `640x480`, currently the `Encoder` only supports the `NV21` format, so set the image format to `image.Format.FMT_YVU420SP`.

2. Initialise the `Encoder` module

   ```python
   e = video.Encoder()
   ```

   - The `video.Encoder()` module currently only supports processing `image.Format.FMT_YVU420SP` format images, which supports `h265` and `h264` encoding, and defaults to `h265` encoding. If you want to use `h264` encoding, then you can change the initialisation parameter to ` video.Encoder(type=video.VideoType.VIDEO_H264_CBR)`.
   - Note that only one encoder can exist at the same time

3. Encoding the camera image

   ```python
   img = cam.read()
   frame = e.encode(img)
   ```

   - `img = cam.read()` read camera image and save to `img`
   - `frame = e.encode(img)` encode `img` and save result to `frame`

4. Save the encoded result to file

   ```python
   f = open('/root/output.h265', 'wb')
   f.write(frame.to_bytes(False))
   ```

   - `f = open(xxx)` opens and creates a file
   - `f.write(frame.to_bytes(False))` converts the encoding result `frame` to type `bytes` and then calls `f.write()` to write the data to the file

5. Timed 2s exit

   ```python
   record_ms = 2000
   start_ms = time.ticks_ms()
   while not app.need_exit():
       if time.ticks_ms() - start_ms > record_ms:
       app.set_exit_flag(True)
   ```

    - Here is the application logic for the timed exit, see the code for yourself

6. Done

## Example 2

An example of recording a video in `h265` format.

```python
from maix import video, time, image, camera, app

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
e = video.Encoder(capture = True)
e.bind_camera(cam)

f = open('/root/output.h265', 'wb')

record_ms = 2000
start_ms = time.ticks_ms()
while not app.need_exit():
    frame = e.encode()
    img = e.capture()

    print(frame.size())
    f.write(frame.to_bytes(True))

    if time.ticks_ms() - start_ms > record_ms:
        app.set_exit_flag(True)
```

Similar to example 1, the difference is that the `Encoder` object's `bind_camera` method is called, and the `Encoder` takes the initiative to get the camera image, which has the advantage of using the hardware features to increase the encoding speed.

```
e = video.Encoder(capture = True)
e.bind_camera(cam)
frame = e.encode()
img = e.capture()
```

- `e = video.Encoder(capture = True)` enables the `capture` parameter to allow encoding to capture encoded images when encoding
- `e.bind_camera(cam)` binds the camera to the `Encoder` object
- `frame = e.encode()` Instead of passing in `img` when encoding, fetch the image from the camera internally
- `img = e.capture()` captures the encoded image from the `Encoder` object, which can be used for image processing



## Convert to MP4 format

If you want to record video in `mp4` format, you can record `H265` video first, and then use the `ffmpeg` tool in the system to convert to `mp4` format.

```python
import os

# Pack h265 to mp4
# /root/output.h265 is the h265 file path
# /root/output.mp4 is the mp4 file path
os.system('ffmpeg -loglevel quiet -i /root/output.h265 -c:v copy -c:a copy /root/output.mp4 -y')
```

