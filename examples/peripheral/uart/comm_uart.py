
from maix import app, uart, pinmap, time
import struct

# ports = uart.list_devices()

# pinmap.set_pin_function("A16", "UART0_TX")
# pinmap.set_pin_function("A17", "UART0_RX")
device = "/dev/ttyS0"

serial0 = uart.UART(device, 115200)


print("send hello 1")
serial0.write("hello 1\r\n".encode())
print("send hello 2")
serial0.write_str("hello 2\r\n")

print("now wait receive data:")
while not app.need_exit():
    data = serial0.read()
    if data:
        print("Received, type: {}, len: {}, data: {}".format(type(data), len(data), data))
        serial0.write(data)

        new_data = [0x31, 0x32, 0x33]

        # Send a single byte array
        serial0.write(b'\n')
        send_data = bytes(new_data)
        serial0.write(b'Send a single byte array:')
        serial0.write(send_data)
        serial0.write(b'\n')

        # Send a double byte array
        format_str = f'{len(new_data)}H'
        send_data = struct.pack(format_str, *new_data)
        serial0.write(b'Send a double byte array:')
        serial0.write(send_data)
        serial0.write(b'\n')

        # Send a four byte array
        format_str = f'{len(new_data)}I'
        send_data = struct.pack(format_str, *new_data)
        serial0.write(b'Send a four byte array:')
        serial0.write(send_data)
        serial0.write(b'\n')
    time.sleep_ms(1) # sleep 1ms to make CPU free



