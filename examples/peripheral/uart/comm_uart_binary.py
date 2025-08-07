
from maix import app, uart, pinmap, time, err, sys
from struct import pack

def print_hex(data : bytes):
    for i in data:
        print(f"0x{i:02X}", end=" ")
    print("")

# ports = uart.list_devices()

# get pin and UART number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_function = {
        "IO0_A21": "UART4_TX",
        "IO0_A22": "UART4_RX"
    }
    device = "/dev/ttyS4"
else:
    pin_function = {
        "A16": "UART0_TX",
        "A17": "UART0_RX"
    }
    device = "/dev/ttyS0"

for pin, func in pin_function.items():
    err.check_raise(pinmap.set_pin_function(pin, func), f"Failed set pin{pin} function to {func}")


serial_dev = uart.UART(device, 115200)

data = b"\x01\x02\x03"
serial_dev.write(data)
print("sent:")
print_hex(data)

x = 10
y = 1000
data = pack("<HH", x, y)
data = b"\xAA\xBB\xCC\xDD" + data
data += pack("B", sum(data) % 255)
serial_dev.write(data)
print("sent:")
print_hex(data)

print("now wait receive data:")
while not app.need_exit():
    data = serial_dev.read()
    if data:
        print("Received, type: {}, len: {}, data:".format(type(data), len(data)))
        print_hex(data)
        serial_dev.write(data)
    time.sleep_ms(1) # sleep 1ms to make CPU free


