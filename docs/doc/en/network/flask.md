---
title: Using Flask to Build an HTTP Web Server with MaixPy MaixCAM
---

## Introduction

MaixPy is based on Python, so you can use the Python library Flask to quickly set up a web server. As it is a common Python library, you can find specific uses and methods online, so they won't be elaborated on here.

If you only want to create a page that displays camera images, you can also refer to the HTTP image server method in [JPEG Streaming](../video/jpeg_streaming.md).

## Simple HTTP Service Example

After running the following program, accessing `http://device_ip:8000` in a computer browser will display the "hello world" text and an image.

```python
from flask import Flask, request, send_file
import maix # we not use it but we import it to listen for key events to exit this program

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
