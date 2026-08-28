---
title: http communication
---

## Introduction

HTTP is the communication method commonly used by websites and web APIs. A device sends a request, and the server returns a status, text, an image, or other data. For example, MaixCAM can fetch configuration data or upload sensor results over HTTP.

## Using HTTP Requests in MaixPy

MaixPy can use Python's `requests` library directly. This page demonstrates a common GET request. For query parameters, file uploads, timeouts, and other options, see the [`requests` quick start](https://requests.readthedocs.io/en/latest/user/quickstart/).

Here is an example of fetching the homepage content of `https://example.com`.

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
