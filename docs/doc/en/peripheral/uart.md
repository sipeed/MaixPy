# Introduction to Using UART in MaixPy

## Introduction to UART

UART (Universal Asynchronous Receiver/Transmitter) is a communication method that includes definitions for both hardware and communication protocols.

* **Hardware includes:**
  * 3 pins: `GND`, `RX`, `TX`. The communication parties connect `RX` and `TX` in a cross configuration, i.e., the `TX` of one side is connected to the `RX` of the other side, and both `GND` pins are connected together.
  * Controller: Usually inside the chip, also known as a UART peripheral. A chip generally has one or more UART controllers, each with corresponding pins.

* **Communication protocol:** To ensure smooth communication between both parties, a set of protocols is defined. You can learn the specifics on your own. Common parameters include baud rate and parity bit, with baud rate being the most frequently used parameter.

Using the board's UART, you can communicate with other microcontrollers or SoCs. For instance, you can implement a human detection function on MaixCAM and send the detected coordinates to an STM32 microcontroller via UART.

## Using UART in MaixPy

For MaixCAM, a UART is by default exposed through the USB port. By connecting a Type-C adapter board, you can directly use the UART pins on it. Alternatively, you can use the `A16 (TX)` and `A17 (RX)` pins on the board directly, which are equivalent to the ones exposed through the USB port.

When using the UART exposed through the USB port on MaixCAM, **note** that the `RX` and `TX` pins on the Type-C adapter board will switch when you flip the Type-C connector. So, if communication fails, it might be due to reversed `RX` and `TX`. Try flipping the Type-C connector and check if the communication works properly. This is a design flaw, but it’s manageable with minimal adjustments.

After connecting the communicating boards (connecting `RX` to `TX` in a cross configuration and both `GND` pins together), you can use the software.

Using UART in MaixPy is simple:

```python
from maix import uart

devices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

Here, we list all UART devices in the system and use the first one, which is the one exposed through the Type-C port.

For more UART APIs, please refer to the [UART API Documentation](../../../api/maix/peripheral/uart.md)

## Other Usage and Using Additional UARTs

```python
from maix import app, uart, pinmap, time
import sys

# pinmap.set_pin_function("A16", "UART0_TX")
# pinmap.set_pin_function("A17", "UART0_RX")
device = "/dev/ttyS0"

serial0 = uart.UART(device, 115200)

serial0.write("hello 1\r\n".encode())
serial0.write_str("hello 2\r\n")

while not app.need_exit():
    data = serial0.read()
    if data:
        print("Received, type: {}, len: {}, data: {}".format(type(data), len(data), data))
        serial0.write(data)
    time.sleep_ms(1) # sleep 1ms to make CPU free
```

Here, we set up pin mapping, especially if you want to use UARTs other than UART0. Use `pinmap.set_pin_function` based on the pin numbers and UART in the diagram:

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

Additionally, a `sleep_ms` function is added in the loop to briefly release the CPU, ensuring that the program does not occupy the CPU fully. There are other methods to achieve this, but this is the simplest and most straightforward approach.
