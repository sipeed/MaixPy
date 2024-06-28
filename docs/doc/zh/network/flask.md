---
title: MaixPy MaixCAM 使用 Flask 建立 HTTP 网页服务器
---


## 简介

MaixPy 基于 Python， 所以你可以使用 Python 库 Flask，通过它可以快速实现一个 Web 网页服务器，因为是 Python 通用的，具体的用处和使用方法可以自行搜索，这里不过多阐述。

如果你只是想做一个显示摄像头图像的页面，也可以参考[JPEG 串流](../video/jpeg_streaming.md) 中的 HTTP 图像服务器的方法。

## 简单的 HTTP 服务例程

运行下面的程序后，电脑浏览器访问 `http://设备ip:8000` 就会显示 `hello world` 字符和一张图片了。

```python
from flask import Flask, request, send_file
import maix # we not use it but we import it to listening key event to exit this program

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def root():
    print("========")
    print(request.remote_addr)
    print(f'headers:\n{request.headers}')
    print(f'data: {request.data}')
    print("========")
    return 'hello world<br><img src="/img" style="background-color: black">'

@app.route("/<path:path>")
def hello(path):
    print(path)
    print(f'headers:\n{request.headers}')
    print(f'data: {request.data}')
    print("---------\n\n")
    return f"hello from {path}"

@app.route("/img")
def img():
    return send_file("/maixapp/share/icon/detector.png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

```

