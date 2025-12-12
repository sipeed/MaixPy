---
title: MaixCAM MaixPy 视频流 WebRTC 推流
update:
  - date: 2025-12-11
    author: 916BGAI
    version: 1.0.0
    content: 初版文档
---

<br/>

> WebRTC 推流需要浏览器支持 WebRTC 协议，请使用最新版本的 Chrome 浏览器进行测试。

## 简介

本文档提供通过 WebRTC 推流摄像头画面的方法

## 使用方法

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

步骤：

1. 导入 time, webrtc, camera 和 image 模块

   ```python
   from maix import time, webrtc, camera, image
   ```

2. 初始化摄像头

   ```python
   # 初始化摄像头，输出分辨率640x480 NV21格式

   cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
   ```

   - 注意 WebRTC 模块目前只支持 NV21 格式， 因此摄像头需要配置为 NV21 格式输出

3. 初始化并启动 WebRTC 对象

   ```python
   server = webrtc.WebRTC()
   server.bind_camera(cam)
   server.start()
   ```

   - `server = webrtc.WebRTC()` 用来创建一个 `WebRTC` 对象
   - `server.bind_camera(cam)` 用来绑定一个 `Camera` 对象， 绑定后原 `Camera` 对象将不能再使用
   - `server.start()` 用来启动 `webrtc` 推流

4. 打印当前WebRTC流的URL

   ```python
   print(server.get_url())
   ```

   - `server.get_url()` 用来获取 `WebRTC` 的 `播放地址`。

6. 完成，运行上须代码后, 你可以通过浏览器访问打印出的URL地址来查看摄像头画面
