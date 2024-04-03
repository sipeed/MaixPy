---
title: MaixPy 视频流 JPEG 推流 / 发送图片到服务器
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
---

## 简介

有时需要将图像发送到服务器，或者将摄像头的视频推送到服务器，这里提供一个最简单的方法，即压缩成 `JPEG` 图片，然后一张一张地发送到服务器。

注意，这是一种最简单的方法，不算很正规的视频推流方法，也不适合高分辨率高帧率的视频流，因为这只是一张一张发送图片，如果要高效推送视频流，请使用后文的 `RTSP` 或者 `RTMP` 模块。

## 使用方法

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


