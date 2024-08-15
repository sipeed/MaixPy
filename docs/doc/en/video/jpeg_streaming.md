---
title: MaixCAM MaixPy Video Stream JPEG Streaming / Sending Images to Server
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: Initial document
  - date: 2024-05-20
    author: lxowalle
    version: 1.0.1
    content: update JPEG-HTTP usage
---

## Introduction

Sometimes it is necessary to send images to a server, or to push video from a webcam to a server, so here are two ways to do it.

- One of the simplest methods is to compress images into `JPEG` format and send them one by one to the server. Note, this is a very basic method and not a formal way to stream video. It is also not suitable for high-resolution, high-frame-rate video streams, as it involves sending images one by one. For more efficient video streaming, please use the `RTSP` or `RTMP` modules discussed later.

- Set up an HTTP server, so that the PC side can be accessed directly through the browser.

## Methods for pushing streams as a client

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

## Methods for pushing streams as a server

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

Steps:

1. Import the image, camera and http modules:

   ```python
   from maix import image, camera, http
   ```

2. Initialize the camera:

   ```python
   cam = camera.Camera(320, 240)
   ```


3. Initialize Stream Object

   ```python
   stream = http.JpegStreamer()
   stream.start()
   ```

   - `http.JpegStreamer()` is used to create a `JpegStreamer` object, which will start an `http server` that will be used to publish `jpeg` image streams to clients.
   - `stream.start()` is used to start the `http server`.

4. Custom html styles (optional)

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

   - `html = xxx` is the `html` code that can be used to customise the style of your web page. Note that the core code is `<img src=‘/stream’ alt=‘Stream’>`, be sure not to miss this line of code.
   - `stream.set_html(html)` is used to set the custom `html` code, this step is optional. The default browsing address is `http://device_ip:8000`.

5. Getting images from the camera and pushing streams

   ```python
   while 1:
       img = cam.read()
       jpg = img.to_jpeg()
       stream.write(jpg)
   ```

   - `img = cam.read()` gets an image from the camera, when initialised as `cam = camera.Camera(320, 240)` the `img` object is an RGB image with a resolution of 320x240.
   - `jpg = img.to_jpeg()` converts the image to `jpeg` format
   - `stream.write(jpg)` writes the image format to the server and the `http` server will send this image to the `http` client.

6. 6. Done, after running the code above, you can see the video stream directly through your browser, the default address is `http://device_ip:8000`. Open your browser and take a look!


