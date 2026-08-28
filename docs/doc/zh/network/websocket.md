---
title: websocket 网络通信
---


## 简介

WebSocket 会在客户端和服务器之间保持一条连接，双方都可以主动发送消息。它常用于实时控制、状态更新，以及设备和网页之间的双向通信。

MaixPy 可以使用 Python 的 `websockets` 和 `asyncio` 模块。下面分别给出客户端和服务端示例，更多连接参数可以查阅 [`websockets` 文档](https://websockets.readthedocs.io/)。


## websocket 客户端

连接服务器发送 10 次消息就结束：

```python
import asyncio
import websockets
import time

async def send_msg(websocket):
    count = 1
    while count <= 10:
        msg = f"hello {count}"
        await websocket.send(msg)
        recv_text = await websocket.recv()
        print(f"receive: {recv_text}", end="\n")
        count += 1
        time.sleep(1)
    await websocket.close(reason="client exit")

async def main_logic(ip, port):
    async with websockets.connect(f'ws://{ip}:{port}') as websocket:
        await send_msg(websocket)

ip = "10.228.104.100"
port = 5678
asyncio.get_event_loop().run_until_complete(main_logic(ip, port))
```

## websocket 服务端

接受客户端的连接并且客户端发送过来消息后，返回`ack for msg:` + 发送过来的消息。

```python
import asyncio
import websockets
import functools

async def recv_msg(websocket):
    print("new client connected, recv_msg start")
    while True:
        try:
            recv_text = await websocket.recv()
        except Exception as e:
            print("receive failed")
            break
        print("received:", recv_text)
        response_text = f"ack for msg: {recv_text}"
        await websocket.send(response_text)
    print("recv_msg end")

async def main_logic(websocket, path, other_param):
    await recv_msg(websocket)

ip = "0.0.0.0"
port = 5678
start_server = websockets.serve(functools.partial(main_logic, other_param="test_value"), ip, port)
print("start server")
asyncio.get_event_loop().run_until_complete(start_server)
print("start server loop")
asyncio.get_event_loop().run_forever()
```
