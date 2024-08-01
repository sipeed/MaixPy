
from maix import app, uart, pinmap, time
from struct import pack

def print_hex(data : bytes):
    for i in data:
        print(f"0x{i:02X}", end=" ")
    print("")

# ports = uart.list_devices()

# pinmap.set_pin_function("A16", "UART0_TX")
# pinmap.set_pin_function("A17", "UART0_RX")
device = "/dev/ttyS0"

serial0 = uart.UART(device, 115200)

data = b"\x01\x02\x03"
serial0.write(data)
print("sent:")
print_hex(data)

x = 10
y = 1000
data = pack("<HH", x, y)
data = b"\xAA\xBB\xCC\xDD" + data
data += pack("B", sum(data) % 255)
serial0.write(data)
print("sent:")
print_hex(data)

print("now wait receive data:")
while not app.need_exit():
    data = serial0.read()
    if data:
        print("Received, type: {}, len: {}, data:".format(type(data), len(data)))
        print_hex(data)
        serial0.write(data)
    time.sleep_ms(1) # sleep 1ms to make CPU free


