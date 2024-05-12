---
title: Introduction to MaixPy UART Serial Communication
---

## Introduction to Serial Communication

Serial communication is a method of communication that includes definitions for both hardware and communication protocols.

* Hardware includes:
  * 3 pins: `GND`, `RX`, `TX`. The communication is cross-connected between RX and TX, meaning one side's TX sends to the other side's RX, and both sides' GND are connected together.
  * Controllers, generally located inside the chip, are also referred to as UART peripherals. Typically, a chip will have one or more UART controllers, each associated with specific pins.
* Communication protocol: To enable smooth communication between the two parties, a set of protocols has been established. Specific details can be self-studied, with common parameters including baud rate and parity bits, among which baud rate is the most frequently used parameter.

Using the board's serial port, data communication can be established with other microcontrollers or SoCs. For example, human detection functions can be implemented on MaixCAM, and upon detecting coordinates, the information can be sent to an STM32 microcontroller through the serial port.

## Using Serial Communication in MaixPy

By default, MaixCAM routes a serial port from the USB port, which can be directly utilized by connecting a compatible Type-C adapter board. Alternatively, the `A16(TX)` and `A17(RX)` pins on the board can be used without an adapter board, which are equivalent to the pins routed from the USB port.

When using the USB-routed serial port on MaixCAM, **attention** is required regarding the Type-C orientation. The `RX` and `TX` may swap when the Type-C is flipped, which might result in communication failures. If issues arise, try flipping the Type-C connector to see if the communication restores. This is considered a design flaw, but since frequent unplugging is uncommon, it is generally acceptable.

Once the two communicating boards are properly connected (cross-connecting RX and TX, with both sides' GND connected together), you can start using the software.

Using the serial port in MaixPy is straightforward:

```python
from maix import uart

devices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

This script first lists all serial port devices in the system, then uses the first device, which is the one routed from the Type-C as mentioned above.

For more information on the UART API, please refer to the [UART API Documentation](../../../api/maix/peripheral/uart.md).

