---
title: MaixCAM MaixPy Maix Application Communication Protocol
---


## Communication Protocol Overview

In order for two devices to communicate stably, there are typically several layers, starting from the bottom:

* **Hardware Layer**: For example, `UART` uses three wires: `TX`, `RX`, and `GND`. It can also be wireless, such as with WiFi.
* **Transport Layer**: Uses transmission control protocols to ensure stable data transmission, such as the `UART` protocol, which specifies baud rate, stop bits, and parity bits to ensure correct data transmission. The `TCP` protocol works similarly.
* **Application Layer**: The data obtained from the transport layer is stream data (simply put, a long string of data without punctuation). To help the application understand what the data means, the application typically defines its own communication protocol for the application layer to structure the transmitted content (you can think of this as adding punctuation to the stream of data to make it easier for the receiver to understand the sentence structure).

For example:
The application layer protocol specifies that a data packet begins with a `$` symbol.
A sends two data packets to B: `$12345$67890`. After receiving it, B knows that A has sent two packets, `12345` and `67890`. Without this protocol, if A sends `12345` followed by `67890`, since the data is transmitted as a stream, B might receive `1234567890`, making it unclear whether one or two packets were sent.

## Character Protocol vs. Binary Protocol

**Character Protocol**:  
In the previous example, we used `$` to mark the beginning of each packet. If we want to send the number `123`, we simply send the string `$123`, which is human-readable. The receiver needs to convert the string `123` to an `int` type. For example, in C language:
```c
int value;
sscanf(buff, "$%d", &value);
```

**Binary Protocol**:  
In a character protocol, sending the number `123` takes 4 bytes, and the receiver has to parse the string to convert it into an integer type. In a binary protocol, we can reduce the number of bytes transmitted and make it easier for the receiver to handle. We can simply send `0x24 0x7B`. `0x24` is the hexadecimal representation of the `$` symbol (refer to the ASCII table), and `0x7B` is the hexadecimal representation of the decimal number `123`. This uses only two bytes to transmit the same information that required 4 bytes in the character protocol. The receiver can directly read the second byte `0x7B` and use its value, such as in C language:
```c
uint8_t value = buff[1];
```

This is just a simple explanation to help you understand the two protocols. In practice, each has its advantages depending on the specific use case, and other factors, such as checksum values, may also be considered. You can explore more and learn about it in the Maix Communication Protocol Practice section below.

## Maix Application Communication Protocol

The Maix Application Communication Protocol is an application layer protocol that uses UART or TCP as the transport layer.

It defines how the two parties communicate and the format in which data is transmitted, making it easier to parse and identify information. It is a binary protocol that includes frame headers, data content, checksums, etc.

The complete protocol definition is available in the [Maix Application Communication Protocol Standard](https://wiki.sipeed.com/maixcdk/doc/convention/protocol.html) (included in the MaixCDK documentation because MaixCDK also uses this protocol).

If you have no prior experience with communication protocols, it might seem a bit difficult, but by reviewing the examples below a few times, you should be able to understand it. In `MaixPy`, the API is already encapsulated, making it very simple to use. For other microcontrollers or chips, you may need to implement this protocol yourself, and you can refer to the appendix of the [Maix Application Communication Protocol Standard](https://wiki.sipeed.com/maixcdk/doc/convention/protocol.html) to check for any corresponding implementations.

For example, if we are performing object detection and want to send the detected object information (such as type and coordinates) via UART to another device (e.g., STM32 or Arduino microcontroller), here’s how it can be done.

Full Example: [MaixPy/examples/protocol/comm_protocol_yolov5.py](https://github.com/sipeed/MaixPy/tree/main/examples/protocol/comm_protocol_yolov5.py)

First, we need to detect the objects, based on the `yolov5` detection example. Here, we’ll skip other details and focus on how the detection results look:
```python
while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
```
You can see that `objs` is a list of detection results. Here, we draw bounding boxes on the screen, but we can also send these results via UART.

We don't need to manually initialize the UART; we can directly use the built-in `maix.comm, maix.protocol` modules. By calling `comm.CommProtocol`, the UART is automatically initialized, with a default baud rate of `115200`. Communication protocol settings can be configured in the device's `System Settings -> Communication Protocol`. There might also be other communication methods, such as `TCP`, with the default set to `UART`. You can check the current setting by using `maix.app.get_sys_config_kv("comm", "method")`.

```python
from maix import comm, protocol, app
from maix.err import Err
import struct

def encode_objs(objs):
    '''
        Encode objects info to bytes body for protocol
        2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...
    '''
    body = b""
    for obj in objs:
        body += struct.pack("<hhHHH", obj.x, obj.y, obj.w, obj.h, obj.class_id)
    return body

APP_CMD_ECHO = 0x01        # Custom command 1, for testing, not used here, just reserved
APP_CMD_DETECT_RES = 0x02  # Custom command 2, send detected object information
                           # You can define more custom commands for your application

p = comm.CommProtocol(buff_size = 1024)

while not app.need_exit():
    # ...
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    if len(objs) > 0:
        body = encode_objs(objs)
        p.report(APP_CMD_DETECT_RES, body)
    # ...
```

In the `encode_objs` function, we pack the detected object information into a `bytes` type data. Then, using the `p.report` function, we send the result.

The `body` content is simply defined as `2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...`, where:

* For each object, we send 10 bytes (2 bytes for each of the `x`, `y`, `w`, `h`, and `class_id` coordinates). The `x` coordinate is represented as a short integer, encoded in little-endian (LE) format.
* The loop encodes all objects and concatenates them into one byte array (`bytes`).

When calling the `report` function, the protocol header, checksum, and other details are automatically added at the lower level, resulting in a complete data frame ready to be received.

On the receiving end, you can decode the data according to the protocol. If the receiver is also using MaixPy, you can directly use:
```python
while not app.need_exit():
    msg = p.get_msg()
    if msg and msg.is_report and msg.cmd == APP_CMD_DETECT_RES:
        print("Received objects:", decode_objs(msg.get_body()))
        p.resp_ok(msg.cmd, b'1')
```

If the device is something like an STM32 or Arduino, you can refer to the C language functions in the appendix of the [Maix Application Communication Protocol Standard](https://wiki.sipeed.com/maixcdk/doc/convention/protocol.html) for encoding and decoding.
