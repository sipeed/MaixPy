import socket

def tcp_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    server_socket.bind(server_address)
    server_socket.listen(1)

    print('Waiting for a connection...')
    connection, client_address = server_socket.accept()
    try:
        print('Connection from:', client_address)

        # 接收数据
        data = connection.recv(1024)
        print('Received:', data.decode('utf-8'))

        # 发送响应
        message = 'Hello, Client!'
        connection.sendall(message.encode('utf-8'))
    finally:
        # 关闭连接
        connection.close()

if __name__ == "__main__":
    tcp_server('0.0.0.0', 8080)

