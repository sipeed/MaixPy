---
title: MaixPy MaixCAM 使用 http 网络通信
---

## 简介

HTTP 是一个应用层网络协议，底层基于 TCP，通过它我们可以向网络服务器发送和接受信息，比如从网页服务器获取网页内容等。
更多介绍可以自行搜索 HTTP。

## 在 MaixPy 使用 HTTP 请求

因为 MaixPy 基于 Python， 所以直接使用自带的 `requests` 库即可，`requests` 库是一个非常健全易用的库，这里就不进行过多的介绍，请自行搜索相关文档和教程使用。

这里举个例子，获取`https://example.com` 的首页内容。

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


