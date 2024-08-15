---
title: MaixCAM MaixPy 视频流 JPEG 推流 / 发送图片到服务器
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.1
    content: 更新JPEG-HTTP用法
---

## 简介

有时需要将图像发送到服务器，或者将摄像头的视频推送到服务器，这里提供两种方法:

- 一个最简单的方法，即压缩成 `JPEG` 图片，然后一张一张地发送到服务器。注意，这是一种最简单的方法，不算很正规的视频推流方法，也不适合高分辨率高帧率的视频流，因为这只是一张一张发送图片，如果要高效推送视频流，请使用后文的 `RTSP` 或者 `RTMP` 模块。
- 建立一个HTTP服务器, 让PC端可以通过浏览器直接访问

## 作为客户端推流的方法

```python
from maix import image
import requests

# create image
img = image.Image(640, 480, image.Format.FMT_RGB)
# draw something
img.draw_rect(60, 60, 80, 80, image.Color.from_rgb(255, 0, 0))

# convert to jpeg
jpeg = img.to_format(image.Format.FMT_JPEG) # image.Format.FMT_PNG
# get jpeg bytes
jpeg_bytes = jpeg.to_bytes()

# faster way, borrow memory from jpeg object,
# but be carefully, when jpeg object is deleted, jpeg_bytes object MUST NOT be used, or program will crash
# jpeg_bytes = jpeg.to_bytes(copy = False)

# send image binary bytes to server
url = "http://192.168.0.123:8080/upload"
res = requests.post(url, data=jpeg_bytes)
print(res.status_code)
print(res.text)
```

可以看到，先将图片转换成了 `JPEG` 格式，然后将 `JPEG` 图片的二进制数据通过`TCP`发送到服务器。

## 作为服务器推流的方法

```python
from maix import camera, time, app, http

html = """<!DOCTYPE html>
<html>
<head>
    <title>JPG Stream</title>
</head>
<body>
    <h1>MaixPy JPG Stream</h1>
    <img src="/stream" alt="Stream">
</body>
</html>"""

cam = camera.Camera(320, 240)
stream = http.JpegStreamer()
stream.set_html(html)
stream.start()

print("http://{}:{}".format(stream.host(), stream.port()))
while not app.need_exit():
    t = time.ticks_ms()
    img = cam.read()
    jpg = img.to_jpeg()
    stream.write(jpg)
    print(f"time: {time.ticks_ms() - t}ms, fps: {1000 / (time.ticks_ms() - t)}")
```


步骤：

1. 导入image、camera和http模块

   ```python
   from maix import image, camera, http
   ```

2. 初始化摄像头

   ```python
   cam = camera.Camera(320, 240) # 初始化摄像头，输出分辨率320x240 RGB格式
   ```

3. 初始化Stream对象

   ```python
   stream = http.JpegStreamer()
   stream.start()
   ```

   - `http.JpegStreamer()`用来创建一个`JpegStreamer`对象，这个对象将会启动一个`http服务器`，用来向客户端发布`jpeg`图像流
   - `stream.start()`用来启动`http服务器`

4. 自定义html样式（可选）

   ```python
   html = """<!DOCTYPE html>
   <html>
   <head>
       <title>JPG Stream</title>
   </head>
   <body>
       <h1>MaixPy JPG Stream</h1>
       <img src="/stream" alt="Stream">
   </body>
   </html>"""
   
   stream.set_html(html)
   ```

   - `html = xxx`是`html`代码，可以用来定制自己的网页风格。注意核心代码是`<img src="/stream" alt="Stream">`，一定不要漏了这行代码。
   - `stream.set_html(html)`用来设置自定义的`html`代码，这一步是可选的。默认浏览地址是`http://设备的ip:8000`。

5. 从摄像头获取图片并推流

   ```python
   while 1:
       img = cam.read()
       jpg = img.to_jpeg()
       stream.write(jpg)
   ```

   - `img = cam.read()`从摄像头获取一张图像，当初始化的方式为`cam = camera.Camera(320, 240)`时，`img`对象是一张分辨率为320x240的RGB图。
   - `jpg = img.to_jpeg()`将图像转换为`jpeg`格式
   - `stream.write(jpg)`向服务器写入图像格式，`http`服务器将会把这个图像发送到`http`客户端。

6. 完成，运行上须代码后, 你可以通过浏览器直接看到视频流, 默认地址为`http://设备的ip:8000`。打开你的浏览器看看吧！

   
