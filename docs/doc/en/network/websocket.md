---
title: Using WebSocket with MaixPy MaixCAM
---

## Introduction

Similar to sockets, WebSocket enables long-lived communication connections and supports communication with web pages.

Since MaixPy is based on Python, you can use the commonly available Python `websockets` and `asyncio` modules. For more detailed information, please refer to the documentation and tutorials available online.

## WebSocket Client

The following example connects to a server, sends a message 10 times, and then ends the connection:

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
        print(f"Received: {recv_text}", end="\n")
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

## WebSocket Server

The following example accepts client connections and responds with `ack for msg:` followed by the received message.

```python
import asyncio
import websockets
import functools

async def recv_msg(websocket):
    print("New client connected, recv_msg start")
    while True:
        try:
            recv_text = await websocket.recv()
        except Exception as e:
            print("Receive failed")
            break
        print("Received:", recv_text)
        response_text = f"ack for msg: {recv_text}"
        await websocket.send(response_text)
    print("recv_msg end")

async def main_logic(websocket, path, other_param):
    await recv_msg(websocket)

ip = "0.0.0.0"
port = 5678
start_server = websockets.serve(functools.partial(main_logic, other_param="test_value"), ip, port)
print("Start server")
asyncio.get_event_loop().run_until_complete(start_server)
print("Start server loop")
asyncio.get_event_loop().run_forever()
```

