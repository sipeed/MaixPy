---
title: MaixPy Video Stream JPEG Streaming / Sending Images to Server
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: Initial document

---

## Introduction

Sometimes it is necessary to send images to a server or push video from a camera to a server. Here, we provide the simplest method, which is to compress images into `JPEG` format and send them one by one to the server.

Note, this is a very basic method and not a formal way to stream video. It is also not suitable for high-resolution, high-frame-rate video streams, as it involves sending images one by one. For more efficient video streaming, please use the `RTSP` or `RTMP` modules discussed later.

## How to Use

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
# but be careful, when jpeg object is deleted, jpeg_bytes object MUST NOT be used, or program will crash
# jpeg_bytes = jpeg.to_bytes(copy = False)

# send image binary bytes to server
url = "http://192.168.0.123:8080/upload"
res = requests.post(url, data=jpeg_bytes)
print(res.status_code)
print(res.text)
```

As you can see, the image is first converted into `JPEG` format, and then the binary data of the `JPEG` image is sent to the server via `TCP`.
