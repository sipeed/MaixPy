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
