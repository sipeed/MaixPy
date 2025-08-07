
from maix import app, uart, pinmap, time, sys, err

def on_received(serial : uart.UART, data : bytes):
    print("received:", data)
    # send back
    serial.write(data)
    print("sent", data)

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
serial_dev.set_received_callback(on_received)

serial_dev.write_str("hello\r\n")
print("sent hello")
print("wait data")

while not app.need_exit():
    time.sleep_ms(100) # sleep to make CPU free

