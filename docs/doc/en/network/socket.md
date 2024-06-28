---
title: Using Socket for TCP/UDP Communication with MaixPy MaixCAM
---

## Introduction to Sockets

Sockets are software abstractions for TCP/UDP communication. Through socket interfaces, we can perform TCP/UDP communication.

Since MaixPy is based on Python, we can directly use the built-in `socket` library for communication. For more documentation and tutorials, please search online.

Here, we introduce simple usage methods. With these example codes, you can perform basic TCP and UDP communication on MaixPy MaixCAM. Remember to modify the IP address and port number according to your actual situation.

## Socket TCP Client

This example requests a TCP server, sends a message, waits for a response, and then closes the connection.

```python
import socket

def tcp_client(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    client_socket.connect(server_address)

    try:
        # Send data to the server
        message = 'Hello, Server!'
        print("Send:", message)
        client_socket.sendall(message.encode('utf-8'))

        # Receive the server's response
        data = client_socket.recv(1024)
        print('Received:', data.decode('utf-8'))
    finally:
        # Close the connection
        client_socket.close()

if __name__ == "__main__":
    tcp_client("10.228.104.1", 8080)
```

## Socket TCP Server

This example creates a socket server that continuously waits for client connections. Once a client connects, a thread is created to communicate with the client, reading the client's message and echoing it back.

```python
import socket
import threading

local_ip = "0.0.0.0"
local_port = 8080

def receiveThread(conn, addr):
    while True:
        print('Reading...')
        client_data = conn.recv(1024)
        if not client_data:
            break
        print(client_data)
        conn.sendall(client_data)
    print(f"Client {addr} disconnected")

ip_port = (local_ip, local_port)
sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sk.bind(ip_port)
sk.listen(50)

print("Waiting for clients...")
while True:
    conn, addr = sk.accept()
    print(f"Client {addr} connected")
    # Create a new thread to communicate with this client
    t = threading.Thread(target=receiveThread, args=(conn, addr))
    t.daemon = True
    t.start()
```

## Socket UDP Client

```python
import socket

def udp_send(ip, port):
    # Create a socket object
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define the server's IP address and port number
    server_address = (ip, port)

    try:
        # Send data to the server
        message = 'Hello, Server!'
        udp_socket.sendto(message.encode('utf-8'), server_address)
    finally:
        # Close the connection
        udp_socket.close()

# Call the function
udp_send("10.228.104.1", 8080)
```

## Socket UDP Server

```python
import socket

def udp_receive(ip, port):
    # Create a socket object
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Define the server's IP address and port number
    server_address = (ip, port)

    # Bind the port
    udp_socket.bind(server_address)

    print('Waiting for a message...')

    while True:
        data, address = udp_socket.recvfrom(1024)
        print('Received:', data.decode('utf-8'))
        print('From:', address)

    # Close the connection
    udp_socket.close()

# Call the function
udp_receive('0.0.0.0', 8080)
```

