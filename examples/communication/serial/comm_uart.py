
from maix import app, uart
import sys

ports = uart.list_ports()

if len(ports) == 0:
    print("no port found")
    sys.exit(1)

for p in ports:
    print("find port:", p)

print("use port:", ports[0])

serial0 = uart.UART(ports[0], 115200)

serial0.write("hello 1\r\n".encode())
serial0.write_str("hello 2\r\n")

while not app.need_exit():
    data = serial0.read()
    if data:
        print("Received, type: {}, len: {}, data: {}".format(type(data), len(data), data))
        serial0.write(data)



