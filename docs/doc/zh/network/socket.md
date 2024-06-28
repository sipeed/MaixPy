---
title: MaixPy MaixCAM 使用 socket 进行 TCP/UDP 通信
---

## socket 简介

socket 就是 TCP/UDP 通信在软件上的封装，通过 socket 接口，我们可以进行 TCP/UDP 通信。

MaixPy 由于基于 Python，我们可以直接使用内置的`socket`库进行通信，更多文档和使用教程可以自行搜索学习。

这里介绍简单的使用方法，通过这些示例代码，你可以在 MaixPy MaixCAM 上进行基本的 TCP 和 UDP 通信。
记得根据实际情况修改 IP 地址和端口号。

## socket TCP 客户端

这里请求 TCP 服务器，发送了一句消息并等待回应，然后关闭连接。

```python
import socket
def tcp_client(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    client_socket.connect(server_address)

    try:
        # 发送数据到服务器
        message = 'Hello, Server!'
        print("send:", message)
        client_socket.sendall(message.encode('utf-8'))

        # 接收服务器的响应
        data = client_socket.recv(1024)
        print('Received:', data.decode('utf-8'))
    finally:
        # 关闭连接
        client_socket.close()

if __name__ == "__main__":
    tcp_client("10.228.104.1", 8080)
```

## socket TCP 服务端

这里创建一个 socket 服务器，并且不停等待客户端连接，客户端连接后创建一个线程用以和客户端通信，读取客户端的信息并原样发送回去。

```python
import socket
import threading

local_ip   = "0.0.0.0"
local_port = 8080

def receiveThread(conn, addr):
    while True:
        print('read...')
        client_data = conn.recv(1024)
        if not client_data:
            break
        print(client_data)
        conn.sendall(client_data)
    print(f"client {addr} disconnected")

ip_port = (local_ip,local_port)
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sk.bind(ip_port)
sk.listen(50)

print("accept now,wait for client")
while True:
    conn, addr = sk.accept()
    print(f"client {addr} connected")
    # create new thread to communicate for this client
    t = threading.Thread(target=receiveThread,args=(conn, addr))
    t.daemon = True
    t.start()
```

## socket UDP 客户端

```python
import socket

def udp_send(ip, port):
    # 创建 socket 对象
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 定义服务器的 IP 地址和端口号
    server_address = (ip, port)

    try:
        # 发送数据到服务器
        message = 'Hello, Server!'
        udp_socket.sendto(message.encode('utf-8'), server_address)

    finally:
        # 关闭连接
        udp_socket.close()

# 调用函数
udp_send("10.228.104.1", 8080)
```

## socket UDP 服务器

```python
import socket

def udp_receive(ip, port):
    # 创建 socket 对象
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 定义服务器的 IP 地址和端口号
    server_address = (ip, port)

    # 绑定端口
    udp_socket.bind(server_address)

    print('Waiting for a message...')

    while True:
        data, address = udp_socket.recvfrom(1024)
        print('Received:', data.decode('utf-8'))
        print('From:', address)

    # 关闭连接
    udp_socket.close()

# 调用函数
udp_receive('0.0.0.0', 8080)
```


