---
title: MaixPy Playback Video
update:
  - date: 2024-08-19
    author: lxowalle
    version: 1.0.0
    content: Initial document
---

## Introduction

This document provides instructions for using the Play Video feature.

`MaixPy` supports playing `h264`, `mp4` and `flv` video formats, note that currently only `avc` encoded `mp4` and `flv` files are supported. Additionally, due to hardware encoder limitations, if you encounter issues decoding the video during playback, try re-encoding it with `ffmpeg` and then play it again. Refer to the following command:

```shell
ffmpeg -i input_video.mp4 -c:v libx264 -x264opts "bframes=0" -c:a aac -strict experimental output_video.mp4
```



## Play `MP4` video

An example of playing an `mp4` video, the path to the video file is `/root/output.mp4`.

```python
from maix import video, display, app, time

disp = display.Display()
d = video.Decoder('/root/output.mp4')
print(f'resolution: {d.width()}x{d.height()} bitrate: {d.bitrate()} fps: {d.fps()}')
d.seek(0)
while not app.need_exit():
    t = time.ticks_ms()

    ctx = d.decode_video()
    if not ctx:
        d.seek(0)
        continue

    img = ctx.image()
    disp.show(img)

    wait_ms = (ctx.duration_us() // 1000) - (time.ticks_ms() - t)
    wait_ms = wait_ms if wait_ms > 0 else 0
    time.sleep_ms(wait_ms)
```

Steps:

1. Import the module and initialise the camera

   ```python
   from maix import video, display, app
   disp = display.Display()
   ```

   - `disp = display.Display()` is used to initialise the display to show the decoded image


2. Initialise the `Decoder` module

   ```python
   d = video.Decoder('/root/output.mp4')
   ```

   - `d = video.Decoder(‘/root/output.mp4’)` is used to initialise the decoder and set the path to the video file that needs to be played. If you need to play `flv` files, you can fill in the path of the file with `flv` suffix, such as `{your_file_path}.flv`, if you need to play `h264` files, you can fill in the path of the file with `h264` suffix, such as `{your_file_path}.h264`

3. Set the decoding location

   ```python
   d.seek(0)
   ```

   - can be used to set the position of the video to be played, in seconds.

4. Get the decoded image

   ```python
   ctx = d.decode_video()
   img = ctx.image()
   ```

   - Each call returns a frame context, and you can obtain img through `ctx.image()`. Currently the decoded output only supports the NV21 format.

5. Display the decoded image

   ```python
   disp.show(img)
   ```

   - When displaying images, you can use `ctx.duration_us()` to obtain the duration of each frame. It can be used to control the playback speed, and the unit is microseconds.

6. Done, see [API documentation](https://wiki.sipeed.com/maixpy/api/maix/video.html) for more usage of `Decoder`.