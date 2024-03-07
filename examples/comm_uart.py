
from maix.peripheral import uart
from maix import app

ports = uart.list_ports()
for p in ports:
    print("find port:", p)

print("use port:", ports[0])

serial = uart.UART(ports[0], 115200)

serial.write("hello 1\r\n".encode())
serial.write_str("hello 2\r\n")

while not app.exit_flag():
    data = serial.read()
    if data:
        print("Received, type: {}, len: {}, data: {}".format(type(data), len(data), data))
        serial.write(data)



