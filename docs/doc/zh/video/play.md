---
title: MaixPy 播放视频
update:
  - date: 2024-08-19
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本文档提供播放视频功能的使用方法。

`MaixPy`支持播放`h264`、`mp4`、`flv`格式的视频，需要注意目前只支持`avc`编码的`mp4`和`flv`文件。此外由于硬件编码器限制，如果播放视频时发现无法解码，先尝试`ffmpeg`重新编码一遍后再试，参考命令：

```shell
ffmpeg -i input_video.mp4 -c:v libx264 -x264opts "bframes=0" -c:a aac -strict experimental output_video.mp4
```




## 播放`MP4`视频

一个播放`mp4`视频的示例，视频文件路径为`/root/output.mp4`

```python
from maix import video, display, app

disp = display.Display()
d = video.Decoder('/root/output.mp4')
print(f'resolution: {d.width()}x{d.height()} bitrate: {d.bitrate()} fps: {d.fps()}')
d.seek(0)
while not app.need_exit():
    ctx = d.decode_video()
    if not ctx:
        d.seek(0)
        continue

    img = ctx.image()
    disp.show(img)
    print(f'need wait : {ctx.duration_us()} us')
```

步骤：

1. 导入模块并初始化摄像头

   ```python
   from maix import video, display, app
   disp = display.Display()
   ```

   - `disp = display.Display()`用来初始化显示屏，用于显示解码的图像


2. 初始化`Decoder`模块

   ```python
   d = video.Decoder('/root/output.mp4')
   ```

   - `d = video.Decoder('/root/output.mp4')`用来初始化解码器，并设置需要播放的视频文件路径。如果你需要播放`flv`文件，则可以填写`flv`为后缀的文件路径，例如`{your_file_path}.flv`，如果你需要播放`h264`文件，则可以填写`h264`为后缀的文件路径，例如`{your_file_path}.h264`

3. 设置解码的位置

   ```python
   d.seek(0)
   ```

   - 可以用来设置播放视频的位置，单位是秒

4. 获取解码后的图像

   ```python
   ctx = d.decode_video()
   img = ctx.image()
   ```

   - 每次调用都会返回一帧图像的上下文`ctx`，通过`ctx.image()`获取`img`。目前解码后只能支持输出`NV21`格式的图像

5. 显示解码后的图像

   ```python
   disp.show(img)
   ```

   - 显示图像时使用`ctx.duration_us()`可以获取每帧图像的时长，单位是微秒

6. 完成，更多`Decoder`的用法请看[API文档](https://wiki.sipeed.com/maixpy/api/maix/video.html)
