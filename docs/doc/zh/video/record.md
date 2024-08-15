---
title: MaixCAM MaixPy 录像
update:
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

## 简介

本文档提供录像功能的使用方法


## 示例一

一个录入`h265`格式视频的示例

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

1. 导入模块并初始化摄像头

   ```python
   from maix import video, image, camera, app, time
   cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
   ```

   - `camera.Camera（）`用来初始化摄像头， 这里初始化摄像头分辨率为`640x480`，注意目前`Encoder`只支持`NV21`格式，因此设置图像格式为`image.Format.FMT_YVU420SP`。


2. 初始化`Encoder`模块

   ```python
   e = video.Encoder()
   ```

   - `video.Encoder()`模块目前只支持处理`image.Format.FMT_YVU420SP`格式图像，支持`h265`和`h264`编码, 默认为`h265`编码。如果你想使用`h264`编码，则可以修改初始化参数为` video.Encoder(type=video.VideoType.VIDEO_H264_CBR)`
   - 注意，同时只能存在一个编码器

3. 编码摄像头的图像

   ```python
   img = cam.read()
   frame = e.encode(img)
   ```

   - `img = cam.read()`读取摄像头图像并保存到`img`
   - `frame = e.encode(img)`对`img`编码并保存结果到`frame`

4. 保存编码结果到文件

   ```python
   f = open('/root/output.h265', 'wb')
   f.write(frame.to_bytes(False))
   ```

   - `f = open(xxx)`打开并创建一个文件
   - `f.write(frame.to_bytes(False))`将编码结果`frame`转换为`bytes`类型，然后调用`f.write()`将数据写入文件中

5. 定时2s退出

   ```python
   record_ms = 2000
   start_ms = time.ticks_ms()
   while not app.need_exit():
       if time.ticks_ms() - start_ms > record_ms:
       app.set_exit_flag(True)
   ```

   - 这里是定时退出的应用逻辑，自己看看吧

6. 完成

## 示例二

一个录入`h265`格式视频的示例

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

与示例一类似，区别在于调用了`Encoder`对象的`bind_camera`方法，`Encoder`主动取图，这样的优点是可以充分利用硬件特性，增加编码速率

```
e = video.Encoder(capture = True)
e.bind_camera(cam)
frame = e.encode()
img = e.capture()
```

- `e = video.Encoder(capture = True)`使能了`capture`参数，让编码时可以抓取编码的图像
- `e.bind_camera(cam)`将摄像头绑定到`Encoder`对象
- `frame = e.encode()`编码时不需要再传入`img`，而是内部从摄像头取图
- `img = e.capture()`从`Encoder`对象中抓取编码的图像



## 转换为MP4格式

如果想要录制`mp4`格式视频，可以先录制好`H265`视频，再使用系统内的`ffmpeg`工具转换为`mp4`格式

```python
import os

# Pack h265 to mp4
# /root/output.h265 是h265文件路径
# /root/output.mp4  是mp4文件路径
os.system('ffmpeg -loglevel quiet -i /root/output.h265 -c:v copy -c:a copy /root/output.mp4 -y')
```

