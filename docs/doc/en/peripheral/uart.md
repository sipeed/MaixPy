Translation to English:
---
title: MaixPy UART Serial Port Usage Introduction
---

## Introduction to Serial Ports

A serial port is a method of communication that includes definitions of hardware and communication protocols.

* Hardware includes:
  * 3 pins: `GND`, `RX`, `TX`. The communication between two parties involves cross-connecting RX and TX, i.e., one's TX sends to the other's RX, and both parties' GNDs are connected.
  * Controller, usually internal within the chip, also known as UART peripheral, typically a chip has one or more UART controllers, each with corresponding pins.
* Communication Protocol: To enable smooth communication between both parties, a set of protocols is established, which includes commonly used parameters like baud rate, parity bits, etc. Baud rate is the most frequently used parameter.

Using the board’s serial port, you can communicate data with other microcontrollers or SoCs, such as implementing human detection on MaixCAM and then sending the coordinates through the serial port to an STM32 microcontroller.

## Using Serial Ports in MaixPy

For MaixCAM, a serial port is defaulted from the USB port, which can be used directly by plugging in the accompanying Type-C adapter board. Alternatively, without an adapter board, you can use the `A16(TX)` and `A17(RX)` pins on the board directly, which are equivalent to the pins led out from the USB port.

**Note** when using the USB-lead serial port on MaixCAM: the Type-C plug and unplug orientation can switch the `RX` and `TX` on the adapter board. So, if you find communication is not happening, it might be due to the RX and TX being reversed; try flipping the Type-C connector to see if communication normalizes. This is considered a design flaw, but generally, as frequent unplugging is not common, this can be adapted to.

Once both communicating boards are connected (communication between the two involves cross-connecting RX and TX, and both parties' GNDs are connected), you can use the software.

Using a serial port in MaixPy is simple:

```python
from maix import uart

devices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

This lists all serial port devices in the system, then uses the first one, which is the one led out from the Type-C as mentioned above.

For more serial port APIs, see [UART API Documentation](../../../api/maix/peripheral/uart.md).

## Sending and Receiving Data

The `write_str` function is used to send strings. In Python, there are two fundamental data types, `str` and `bytes`, where the former is a string, and the latter is raw byte data, for example:
* `"A"` becomes `b"A"` using the `encode()` method, conversely `b"A"` becomes `"A"` using the `decode()` method.
* `str` can't display some invisible characters, like ASCII code value `0`, represented as `\0` in strings, generally used as an end character, whereas in `bytes` type, it can be stored as `b"\x00"`.
* It's even more useful for non-ASCII encoded strings, e.g., the Chinese character `好` in UTF-8 encoding is represented by three bytes `\xe5\xa5\xbd`, which can be obtained by `"好".encode("utf-8")` to produce `b"\xe5\xa5\xbd"`, or converted back to `"好"` using `b'\xe5\xa5\xbd'.decode("utf-8)`.

Thus, if you need to send byte data, use the `write()` method.

For `str` type, you can avoid using `write_str` and instead send using `serial.write(str_content.encode())`.

Also, if you have a `list` type of data, you can construct a `bytes` object using the `bytes()` method, like:
```python
a = [1, 2, 3]
serial.write(bytes(a))
```

Similarly, the data obtained by the `read` method is also of `bytes` type.

## Other Usage

```python
from maix import app, uart, time
import sys

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

Additionally, a `sleep

_ms` is included in the loop as a simple way to release the CPU, aiming to ensure the program does not consume all CPU resources. This is the simplest and most straightforward method.

## Using Other Serial Ports

Each pin may correspond to different peripheral functions, also known as pin multiplexing. As shown in the diagram below, each pin corresponds to different functions, for example, pin `A17` (as labeled on the board) corresponds to `GPIOA17`, `UART0_RX`, `PWM5`, by default set to `UART0_RX`.

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

Normally, you can directly use `UART0` as mentioned above. For other serial ports, whose pins are not defaulted to serial peripheral functions, you need to first set up the mapping using `pinmap.set_pin_function`.

For example, to use `UART1`, first set the pin function mapping for serial, then use the device number `/dev/ttyS1`. Note that `uart.list_devices()` does not by default return serial ports that require manual mapping, so you can manually pass parameters:

```python
from maix import app, uart, pinmap, time

pinmap.set_pin_function("A18", "UART1_RX")
pinmap.set_pin_function("A19", "UART1_TX")

device = "/dev/ttyS1"

serial1 = uart.UART(device, 115200)
```



## Using Serial Communication Protocols

With serial communication, you can choose to transmit information in a way that suits your preferences, either by directly sending string results or by using Python's `struct` library to encode into a binary protocol.

Additionally, MaixPy also has a built-in communication protocol that you can use directly.

This communication protocol specifies the format in which both parties transmit content, facilitating the parsing and recognition of information. It is a binary protocol that includes a frame header, data content, checksum, etc. The complete protocol definition can be found at [Maix Serial Communication Protocol Standard](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md).
It might seem difficult if you have never dealt with communication protocols, but you can understand it after going through the example below several times.

For instance, if we have an object detection task, and we want to send the detected object information via serial port to other devices (like an STM32 or Arduino microcontroller), telling them what objects were detected and their coordinates.

Complete example: [MaixPy/examples/protocol/comm_protocol_yolov5.py](https://github.com/sipeed/MaixPy/tree/main/examples/protocol/comm_protocol_yolov5.py)

First, we need to detect the object, refer to the `yolov5` object detection example, and here we skip other details to focus on what the detection results look like:

```python
while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

As you can see, `objs` contains multiple detection results, and here we draw boxes on the screen. We can also find a way to send these results via the serial port.
We do not need to manually initialize the serial port, just use the built-in `maix.comm, maix.protocol` modules, and calling `comm.CommProtocol` will automatically initialize the serial port with a default baud rate of `115200`. The serial port protocol settings can be found in the device `System Settings->Communication Protocol`.
System settings might also include other communication methods like `tcp`, the default is `uart`, and you can also use `maix.app.get_sys_config_kv("comm", "method")` to check if the current setting is `uart`.

```python
from maix import comm, protocol, app
from maix.err import Err
import struct

def encode_objs(objs):
    '''
        Encode object info into a bytes body for protocol
        2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...
    '''
    body = b""
    for obj in objs:
        body += struct.pack("<hhHHH", obj.x, obj.y, obj.w, obj.h, obj.class_id)
    return body

APP_CMD_ECHO = 0x01
APP_CMD_DETECT_RES = 0x02

p = comm.CommProtocol(buff_size = 1024)

while not app.need_exit():
    # ...
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    if len(objs) > 0:
        body = encode_objs(objs)
        p.report(APP_CMD_DETECT_RES, body)
    # ...
```

Here, the `encode_objs` function packages all detected object information into a `bytes` type of data, and then the `p.report` function sends the results out.

The content of `body` is simply defined as `2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...`,
meaning:
* Multiple objects detected in this image are arranged in order in `body`, each target occupies 10 bytes, totaling `body_len / 10` objects.
* The first and second bytes represent the top-left `x` coordinate of the detected object, measured in pixels. Since the `yolov5` results might have negative coordinates, we use a `short` type to represent them, encoded in little-endian (LE).
  > Here, little-endian means the lower byte comes first, for example, the coordinate `x` is `100`, hex `0x64`, represented by two bytes as `short` would be `0x0064`, and little-endian encoded into `bytes` would be `0x64` first,resulting in `b'\x64\x00'`.
* Similarly, encode the subsequent data sequentially, with each object resulting in a `10`-byte-long `bytes` type data.
* Loop to encode all object information and concatenate into a `bytes` object.

When calling the `report` function, the underlying system will automatically concatenate protocol headers, checksums, etc., according to the protocol, resulting in a frame of complete data being received at the other end.

After receiving the information at the other end, it must also be decoded according to the protocol. If the receiving end uses MaixPy, you can directly:
```python
while not app.need_exit():
    msg = p.get_msg()
    if msg and msg.is_report and msg.cmd == APP_CMD_DETECT_RES:
        print("receive objs:", decode_objs(msg.get_body()))
        p.resp_ok(msg.cmd, b'1')
```

For other devices such as `STM32` or `Arduino`, refer to the C language functions in the appendix of [Maix Serial Communication Protocol Standard](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) for encoding and decoding.

