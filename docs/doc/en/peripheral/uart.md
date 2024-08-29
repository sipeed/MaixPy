---
title: Introduction to Using MaixCAM MaixPy UART Serial Port
---

## Introduction to Serial Ports

A serial port is a communication method that includes the definitions of both hardware and communication protocols.

* Hardware includes:
  * 3 pins: `GND`, `RX`, `TX`, with cross-connection for communication. `RX` and `TX` should be cross-connected, meaning one side's `TX` should connect to the other side's `RX`, and both sides' `GND` should be connected together.
  * Controller, usually inside the chip, also known as the `UART` peripheral. Generally, a chip can have one or more `UART` controllers, each with corresponding pins.
* Serial communication protocol: To ensure smooth communication between both parties, a set of protocols is established, specifying how communication should occur, including common parameters like baud rate and parity bit. Baud rate is the most commonly used parameter.

Using the serial port of the board, you can communicate data with other microcontrollers or SOCs. For example, human detection can be implemented on MaixCAM, and the detected coordinates can be sent to STM32/Arduino microcontrollers via the serial port.

## Using Serial Port in MaixPy

MaixCAM's default configuration exposes a serial port through the USB port. By plugging in the Type-C adapter board, you can directly use the serial port pins. Alternatively, you can use the `A16(TX)` and `A17(RX)` pins directly on the board, which are equivalent to those exposed via the USB port.

When using the serial port exposed through USB on MaixCAM, note that the `RX` and `TX` pins on the Type-C adapter board will swap between regular and reverse insertions (assuming the **Type-C female port is facing forward** and matching the silk screen). If communication fails, try flipping the Type-C connection to see if it resolves the issue. Although this is a design flaw, frequent plug/unplug operations are rare, so adapting to it is acceptable.

After connecting the two communicating boards (cross-connecting `RX` and `TX` and connecting both `GND`), you can use software for communication.

Using the serial port with MaixPy is simple:

```python
from maix import uart

device = "/dev/ttyS0"
# ports = uart.list_devices() # List available serial ports

serial = uart.UART(device, 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

Here, we use the first serial port `/dev/ttyS0`, which is the serial port exposed via `Type-C` mentioned above.

More serial port APIs can be found in the [UART API documentation](../../../api/maix/peripheral/uart.md).

## MaixCAM Serial Port Usage Notes

### TX Pin Notes

MaixCAM's `TX` (`UART0`) pin must not be in a pulled-down state during boot-up, or the device will fail to start. This is a characteristic of the chip. If you are designing a 3.3v to 5v level-shifting circuit, be sure not to default it to a pulled-down state and keep it floating (consider using a level-shifting chip).

If the device fails to boot, also check whether the `TX` pin is pulled down.

## Connecting to a Computer via Serial Port

Developers may ask: Why doesn't the serial port device appear on the computer when the USB is plugged in? The answer is that the USB on the device defaults to a virtual USB network card without serial port functionality. To access the device's terminal, use SSH connection.

For MaixCAM, the `serial port 0` from the Type-C adapter board is directly connected to the `A16(TX)` and `A17(RX)` pins. It can be connected directly to other devices, such as microcontrollers' serial port pins. To communicate with a computer, use a USB-to-serial converter board (such as [this one](https://item.taobao.com/item.htm?spm=a1z10.5-c-s.w4002-24984936573.13.73cc59d6AkB9bS&id=610365562537)).

## Boot Log Output

It is important to note that **MaixCAM's `serial port 0` will output some boot logs during startup**. After startup, the message `serial ready` will be printed. When communicating with a microcontroller, discard this information. If there are system startup issues, the boot log from `serial port 0` can help diagnose the problem.

## Sending Data

There are mainly two functions for sending data: `write_str` and `write`.

The `write_str` function is used to send strings, while `write` is used to send byte streams, i.e., `str` and `bytes` types, which can be converted to each other. For example:
* `"A"` can be converted to `b"A"` using the `encode()` method, and vice versa, `b"A"` can be converted back to `"A"` using the `decode()` method.
* `str` cannot display some invisible characters, such as the ASCII value `0`, which is generally `\0` in strings and serves as a terminator. In `bytes` type, it can be stored as `b"\x00"`.
* This is more useful for non-ASCII encoded strings. For example, the Chinese character `好` in `UTF-8` encoding is represented by three bytes `\xe5\xa5\xbd`. We can use `"好".encode("utf-8")` to get `b"\xe5\xa5\xbd"`, and `b'\xe5\xa5\xbd'.decode("utf-8)` to get `"好"`.

So if we need to send byte data, we can use the `write()` method to send it. For example:

```python
bytes_content = b'\x01\x02\x03'
serial.write(bytes_content)
```

Therefore, for the `str` type, you can use `serial.write(str_content.encode())` instead of `write_str` to send it.

If you have other data types that you want to convert into a **string to send**, you can use `Python string formatting` to create a string. For example, to send `I have xxx apple`, where `xxx` is an integer variable, you can do:

```python
num = 10
content = "I have {} apple".format(num)
content2 = f"I have {num} apple"
content3 = "I have {:04d} apple".format(num)
content4 = f"I have {num:d} apple"
print(content)
print(content2)
print(content3)
print(content4)
print(type(content))
serial.write_str(content)
```

Additionally, you can encode the data into a **binary stream to send**. For example, the first 4 bytes are hexadecimal `AABBCCDD`, followed by an `int` type value, and finally a `0xFF` at the end. You can use `struct.pack` to encode it (if this is unclear, you can read the explanation later):

```python
from struct import pack
num = 10
bytes_content = b'\xAA\xBB\xCC\xDD'
bytes_content += pack("<i", num)
bytes_content += b'\xFF'
print(bytes_content, type(bytes_content))
serial.write(bytes_content)
```

Here, `pack("<i", num)` encodes `num` as an `int` type, which is a 4-byte signed integer. The `<` symbol indicates little-endian encoding, with the low byte first. Here, `num = 10`, the 4-byte hexadecimal representation is `0x0000000A`, and little-endian encoding puts the low byte `0x0A` first, resulting in `b'\x0A\x00\x00\x00'`.

> Here, we use `i` to encode `int` type data as an example. Other types, such as `B` for `unsigned char`, etc., can also be used. More `struct.pack` formatting options can be searched online with `python struct pack`.

In this way, the final data sent is `AA BB CC DD 0A 00 00 00 FF` as binary data.

## Receiving Data

Use the `read` method to read data directly:

```python
while not app.need_exit():
    data = serial.read()
    if data:
        print(data)
    time.sleep_ms(1)
```

Similarly, the data obtained by the `read` method is also of the `bytes` type. Here, `read` reads a batch of data sent by the other party. If there is no data, it returns `b''`, which is an empty byte.

Here, `time.sleep_ms(1)` is used to sleep for `1ms`, which frees up the CPU so that this thread does not occupy all CPU resources. `1ms` does not affect the program's efficiency, especially in multithreading.

In addition, the `read` function has two parameters:
* `len`: Represents the maximum length you want to receive. The default is `-1`, meaning it will return as much as there is in the buffer. If you pass a value `>0`, it means it will return data up to that length.
* `timeout`:
  * The default `0` means it will return immediately with whatever data is in the buffer. If `len` is `-1`, it returns all data; if a length is specified, it returns data not exceeding that length.
  * `<0` means it waits until data is received before returning. If `

len` is `-1`, it waits until data is received and returns (blocking read for all data); if a length is specified, it waits until it reaches `len` before returning.
  * `>0` means it will return after this time, regardless of whether data is received.

It may seem complex, but here are some common parameter combinations:
* `read()`: Which is `read(-1, 0)`, reads the data received in the buffer, usually a batch of data sent by the other party. It returns immediately when the other party has stopped sending (within one character's sending time).
* `read(len = -1, timeout = -1)`: Blocking read for a batch of data, waits for the other party to send data and returns only when there is no more data within one character's sending time.
* `read(len = 10, timeout = 1000)`: Blocking read for 10 characters, returns when 10 characters are read or 1000ms has passed without receiving any data.

## Setting a Callback Function for Receiving Data

In MCU development, a serial port interrupt event usually occurs when data is received. MaixPy has already handled the interrupt at the bottom layer, so developers don't need to handle the interrupt themselves. If you want to call a callback function upon receiving data, you can use `set_received_callback` to set the callback function:

```python

from maix import uart, app, time

def on_received(serial : uart.UART, data : bytes):
    print("received:", data)
    # send back
    serial.write(data)

device = "/dev/ttyS0"

serial = uart.UART(device, 115200)
serial.set_received_callback(on_received)

serial0.write_str("hello\r\n")
print("sent hello")
print("wait data")

while not app.need_exit():
    time.sleep_ms(100) # sleep to make CPU free
```

When data is received, the set callback function will be called in **another thread**. Since it's called in another thread, unlike an interrupt function, you don't have to exit the function quickly. You can handle some tasks in the callback function before exiting, but be aware of common multithreading issues.

If you use the callback function method to receive data, do not use the `read` function to read it, or it will read incorrectly.

## Using Other Serial Ports

Each pin may correspond to different peripheral functions, which is also known as pin multiplexing. As shown below, each pin corresponds to different functions. For example, pin `A17` (silkscreen identification on the board) corresponds to `GPIOA17`, `UART0_RX`, and `PWM5` functions. The default function is `UART0_RX`.

![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

By default, you can directly use `UART0` as shown above. For other serial port pins, they are not set to the serial peripheral function by default, so you need to set the mapping to use other serial ports. Use `pinmap.set_pin_function` to set it.

Let's take `UART1` as an example. First, set the pin mapping to choose the serial port function, then use the device number `/dev/ttyS1`. Note that `uart.list_devices()` will not return manually mapped serial ports by default, so you can directly pass the parameters manually:

```python
from maix import app, uart, pinmap, time

pinmap.set_pin_function("A18", "UART1_RX")
pinmap.set_pin_function("A19", "UART1_TX")

device = "/dev/ttyS1"

serial1 = uart.UART(device, 115200)
```

## Application Layer Communication Protocol

### Concept and Character Protocol

Serial ports only define the hardware communication timing. To let the receiver understand the meaning of the character stream sent by the sender, an application communication protocol is usually established. For example, if the sender needs to send coordinates containing two integer values `x, y`, the following protocol is established:

* **Frame Header**: When I start sending the `$` symbol, it means I'm about to start sending valid data.
> **Content**: Designing a start symbol is because serial communication is stream-based. For example, sending `12345` twice may result in receiving `12345123` at some moment. The `45` from the second frame has not been received. We can determine a complete data frame based on start and end symbols.
* The value range of `x, y` is 0~65535, i.e., an unsigned short integer (`unsigned short`). I'll first send `x` then `y`, separated by a comma, such as `10,20`.
* **Frame Tail**: Finally, I'll send a `*` to indicate that I've finished sending this data.

In this way, sending a data packet looks like `$10,20*` as a string. The other party can receive and parse it using C language:

```c
// 1. Receive data
// 2. Determine if the reception is complete based on the frame header and tail, and store the complete frame data in the buff array
// 3. Parse a frame of data
uint16_t x, y;
sscanf(buff, "$%d,%d*", &x, &y);
```

Thus, we have defined a simple character communication protocol with a certain degree of reliability. However, since we usually use parameters like `115200 8 N 1` for serial ports, where `N` means no parity check, we can add a **checksum** to our protocol at the end. For example:

* Here, we add a checksum value after `x, y`, ranging from 0 to 255. It is the sum of all previous characters modulo 255.
* Taking `$10,20` as an example, in `Python`, you can simply use the `sum` function: `sum(b'$10,20') % 255 --> 20`, and send `$10,20,20*`.
* The receiver reads the checksum `20`, calculates it in the same way as `$10,20`, and if it is also `20`, it means no transmission error occurred. Otherwise, we assume a transmission error and discard the packet to wait for the next one.

In MaixPy, encoding a character protocol can be done using Python's string formatting feature:

```python
x = 10
y = 20
content = "${},{}*".format(x, y)
print(content)
```

### Binary Communication Protocol

The character protocol above has a clear characteristic of using visible characters to transmit data. The advantage is simplicity and human readability. However, it uses an inconsistent number of characters and larger data volumes. For example, `$10,20*` and `$1000,2000*` have varying lengths, with `1000` using 4 characters, which means 4 bytes. We know an unsigned short integer (`uint16`) can represent values ranging from `0~65535` using only two bytes. This reduces the transmission data. 

We also know visible characters can be converted to binary via ASCII tables, such as `$1000` being `0x24 0x31 0x30 0x30 0x30` in binary, requiring 5 bytes. If we directly encode `1000` in binary as `0x03E8`, we can send `0x24 0x03 0xE8` in just 3 bytes, reducing communication overhead.

Additionally, `0x03E8` is a 2-byte representation with `0xE8` as the low byte, transmitted first in little-endian encoding. The opposite is big-endian encoding. Both are fine as long as both parties agree on one.

In MaixPy, converting a number to bytes is simple with `struct.pack`. For example, `0x03E8` (decimal `1000`):

```python
from struct import pack
b = pack("<H", 1000)
print(b)
```

Here, `<H` indicates little-endian encoding, with `H` denoting a `uint16` data type, resulting in `b'\xe8\x03'` as bytes.

Similarly, binary protocols can have a frame header, data content, checksum, frame tail, or a frame length field instead of a frame tail, based on preference.

### Built-in MaixPy Communication Protocol

MaixPy also includes a built-in communication protocol.

This communication protocol defines the format for communication between parties, making it easier to parse and recognize information. It's a binary protocol that includes a frame header, data content, and checksum. The complete protocol is defined in the [Maix Serial Communication Protocol Standard](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md). Those unfamiliar with communication protocols may find it challenging at first, but reviewing the example below multiple times can help with understanding.

For instance, if we have object detection, and we want to send the detected objects' information, such as coordinates, to another device (like STM32 or Arduino microcontrollers) via serial port:

Complete example: [MaixPy/examples/protocol/comm_protocol_yolov5.py](https://github.com/sipeed/MaixPy/tree/main/examples/protocol/comm_protocol_yolov5.py).

First, we need to detect objects. Refer to the `yolov5` object detection example. Here, we omit other details and focus on the detection results:

```python
while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj

.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

You can see `objs` are multiple detection results. Here, we're drawing boxes on the screen, and we can find a way to send these results via the serial port.

We don't need to manually initialize the serial port, just use the built-in `maix.comm, maix.protocol` modules. Calling `comm.CommProtoco` will automatically initialize the serial port, with a default baud rate of `115200`. The serial port protocol can be set in the device's `System Settings->Communication Protocol`. 

The system settings may have other communication methods, such as `tcp`, with `uart` as the default. You can also use `maix.app.get_sys_config_kv("comm", "method")` to check if `uart` is currently set.

```python
from maix import comm, protocol, app
from maix.err import Err
import struct

def encode_objs(objs):
    '''
        encode objs info to bytes body for protocol
        2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...
    '''
    body = b""
    for obj in objs:
        body += struct.pack("<hhHHH", obj.x, obj.y, obj.w, obj.h, obj.class_id)
    return body

APP_CMD_ECHO = 0x01        # Custom command 1, for testing, not used here, reserved
APP_CMD_DETECT_RES = 0x02  # Custom command 2, send detected object information
                           # You can define more commands based on your application

p = comm.CommProtocol(buff_size = 1024)

while not app.need_exit():
    # ...
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    if len(objs) > 0:
        body = encode_objs(objs)
        p.report(APP_CMD_DETECT_RES, body)
    # ...
```

Here, the `encode_objs` function packages all detected object information into `bytes` type data, and the `p.report` function sends the result.

The content of `body` is simply defined as `2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...`, meaning:
* In this image, multiple objects are detected and arranged in order in `body`. Each target takes up `2+2+2+2+2 = 10` bytes, with `body_len / 10` objects in total.
* The 1st and 2nd bytes represent the `x` coordinate of the top-left corner of the detected object, in pixels. Since the yolov5 result can have negative values for this coordinate, we use a `short` type to represent it, with little-endian encoding (LE).

> Little-endian here means the low byte is in front. For example, if the `x` coordinate is `100`, hexadecimal `0x64`, we use a two-byte `short` to represent it as `0x0064`. Little-endian encoding puts `0x64` first, resulting in `b'\x64\x00'`.

* Similarly, encode the subsequent data in sequence, resulting in `10` bytes of `bytes` type data for each object.
* Iterate through and encode all object information into a single `bytes` string.

When calling the `report` function, the protocol header, checksum, etc., are automatically added according to the protocol, allowing the other end to receive a complete data frame.

On the other end, data should be decoded according to the protocol. If the receiving end is also using MaixPy, you can directly do:

```python
while not app.need_exit():
    msg = p.get_msg()
    if msg and msg.is_report and msg.cmd == APP_CMD_DETECT_RES:
        print("receive objs:", decode_objs(msg.get_body()))
        p.resp_ok(msg.cmd, b'1')
```

If the other device is something like `STM32` or `Arduino`, you can refer to the C language functions in the appendix of the [Maix Serial Communication Protocol Standard](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) for encoding and decoding.

## Other Tutorials

* [【MaixPy/MaixCAM】Visual Tool -- MaixCAM Beginner Tutorial 2](https://www.bilibili.com/video/BV1vcvweCEEe/?spm_id_from=333.337.search-card.all.click) Watch the serial port explanation section
* [How to Communicate via Serial Port between Visual Module and STM32](https://www.bilibili.com/video/BV175vWe5EfV/?spm_id_from=333.337.search-card.all.click&vd_source=6c974e13f53439d17d6a092a499df304)
* [[MaixCam] Experience 2: UART Serial Communication](https://blog.csdn.net/ButterflyBoy0/article/details/140577441)
* For more, search online for resources.


