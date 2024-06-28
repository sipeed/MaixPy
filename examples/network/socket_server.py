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

