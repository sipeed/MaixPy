---
title: http 网络通信
---

## 简介

HTTP 是网页和网络接口常用的通信方式。设备向服务器发送请求，服务器再返回状态、文字、图片或其他数据。例如，MaixCAM 可以通过 HTTP 获取配置，也可以把传感器结果上传到服务器。

## 在 MaixPy 使用 HTTP 请求

MaixPy 可以直接使用 Python 的 `requests` 库。本页先演示最常见的 GET 请求；请求参数、上传文件和超时设置等用法可以查阅 [`requests` 文档](https://requests.readthedocs.io/en/latest/user/quickstart/)。

下面的例子获取 `https://example.com` 的首页内容，并打印服务器返回的状态码、响应头和正文。

```python
import requests

url = 'https://example.com'
response = requests.get(url)
print("Response:")
print("-- status code:", response.status_code)
print("")
print("-- headers:", response.headers)
print("")
print("-- content:", response.content)
print("")
print("-- text:", response.text)
print("")
```
