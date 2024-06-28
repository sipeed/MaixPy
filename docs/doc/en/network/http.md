---
title: Using HTTP Network Communication with MaixPy MaixCAM
---

## Introduction

HTTP is an application layer network protocol based on TCP. Through it, we can send and receive information to and from network servers, such as retrieving webpage content from a web server. For more information, you can search for HTTP.

## Using HTTP Requests in MaixPy

Since MaixPy is based on Python, you can directly use the built-in `requests` library. The `requests` library is a very robust and user-friendly library, so it won't be elaborated on here. Please search for related documentation and tutorials for more information.

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

