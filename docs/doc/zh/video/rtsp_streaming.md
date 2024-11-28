---
title: MaixCAM MaixPy 视频流 RTSP 推流
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本文档提供通过RTSP推流摄像头画面的方法

## 使用方法

```python
from maix import time, rtsp, camera, image

cam = camera.Camera(2560, 1440, image.Format.FMT_YVU420SP)
server = rtsp.Rtsp()
server.bind_camera(cam)
server.start()

print(server.get_url())

while True:
    time.sleep(1)
```

步骤：

1. 导入time、rtsp、camera和image模块

   ```python
   from maix import time, rtsp, camera, image
   ```

2. 初始化摄像头

   ```python
   cam = camera.Camera(2560, 1440, image.Format.FMT_YVU420SP) # 初始化摄像头，输出分辨率2560x1440 NV21格式
   ```

   - 注意RTSP模块目前只支持NV21格式， 因此摄像头需要配置为NV21格式输出


3. 初始化并启动Rtsp对象

   ```python
   server = rtsp.Rtsp()
   server.bind_camera(cam)
   server.start()
   ```

   - `server = rtsp.Rtsp()`用来创建一个`Rtsp`对象
   - `server.bind_camera(cam)`用来绑定一个`Camera`对象， 绑定后原`Camera`对象将不能再使用
   - `server.start()`用来启动`rtsp`推流

4. 打印当前RTSP流的URL

   ```python
   print(server.get_url())
   ```

   - `server.get_url()`用来获取`RTSP`的`播放地址`。

6. 完成，运行上须代码后, 你可以通过[VLC](https://www.videolan.org/vlc/)软件播放视频流, 已测试的`VLC`版本是`3.0.20`. 默认播放地址为`rtsp://设备的ip:8554/live`


## 支持推流音频

MaixPy支持同时推送音视频流, 通过绑定一个`Recorder`对象后可以在推送视频流的同时附带音频数据

> 注:MaixPy v4.7.8之后的版本支持该方法（不包括v4.7.8）

参考代码如下:

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

上文中通过`audio.Recorder()`创建一个`audio_recorder`对象,并使用`Rtsp`的`bind_audio_recorder()`方法绑定该对象, 使用`ffplay rtsp://设备的ip:8554/live`命令或者`vlc 3.0.20`就能接收音视频数据了