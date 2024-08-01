
from maix import app, uart, pinmap, time
import struct

# ports = uart.list_devices()

# pinmap.set_pin_function("A16", "UART0_TX")
# pinmap.set_pin_function("A17", "UART0_RX")
device = "/dev/ttyS0"

serial0 = uart.UART(device, 115200)


data = "hello 1\r\n".encode()
serial0.write(data)
print("sent:", data)

data = "hello 2\r\n"
serial0.write_str(data)
print("sent:", data)

data = "object {} at x: {} y: {} w: {} h: {}, prob: {:.2f}\r\n".format("apple", 100, 100, 80, 80, 0.98123)
serial0.write_str(data)
print("sent:", data)

print("now wait receive data:")
while not app.need_exit():
    data = serial0.read()
    if data:
        print("Received, type: {}, len: {}, data: {}".format(type(data), len(data), data))
        serial0.write(data)

    time.sleep_ms(1) # sleep 1ms to make CPU free



