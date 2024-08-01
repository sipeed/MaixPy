
from maix import app, uart, pinmap, time

def on_received(serial : uart.UART, data : bytes):
    print("received:", data)
    # send back
    serial.write(data)
    print("sent", data)

# ports = uart.list_devices()

# pinmap.set_pin_function("A16", "UART0_TX")
# pinmap.set_pin_function("A17", "UART0_RX")
device = "/dev/ttyS0"

serial0 = uart.UART(device, 115200)
serial0.set_received_callback(on_received)

serial0.write_str("hello\r\n")
print("sent hello")
print("wait data")

while not app.need_exit():
    time.sleep_ms(100) # sleep to make CPU free

