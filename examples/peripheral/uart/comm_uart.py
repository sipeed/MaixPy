
from maix import app, uart, pinmap, time, sys, err

# ports = uart.list_devices()

# get pin and UART number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_function = {
        "IO0_A21": "UART4_TX",
        "IO0_A22": "UART4_RX"
        # "IO1_A0": "UART2_TX",
        # "IO1_A1": "UART2_RX"
    }
    device = "/dev/ttyS4"
    # device = "/dev/ttyS2"
else:
    pin_function = {
        "A16": "UART0_TX",
        "A17": "UART0_RX"
    }
    device = "/dev/ttyS0"

for pin, func in pin_function.items():
    err.check_raise(pinmap.set_pin_function(pin, func), f"Failed set pin{pin} function to {func}")

# Init UART
serial_dev = uart.UART(device, 115200)


data = "hello 1\r\n".encode()
serial_dev.write(data)
print("sent:", data)

data = "hello 2\r\n"
serial_dev.write_str(data)
print("sent:", data)

data = "object {} at x: {} y: {} w: {} h: {}, prob: {:.2f}\r\n".format("apple", 100, 100, 80, 80, 0.98123)
serial_dev.write_str(data)
print("sent:", data)

print("now wait receive data:")
while not app.need_exit():
    data = serial_dev.read()
    if data:
        print("Received, type: {}, len: {}, data: {}".format(type(data), len(data), data))
        serial_dev.write(data)

    time.sleep_ms(1) # sleep 1ms to make CPU free



