---
title: MaixPy UART 串口使用介绍
---

## 串口简介

串口是一种通信方式，包含了硬件和通信协议的定义。

* 硬件包括：
  * 3 个引脚： `GND`， `RX`， `TX`，通信双发交叉连接 RX TX， 即一方 TX 发送到另一方的 RX， 双方 GND 连接到一起。
  * 控制器，一般在芯片内部，也叫 UART 外设，一般一个芯片有一个或者多个 UART 控制器，每个控制器有相对应的引脚。
* 通信协议： 为了让双方能顺利通信，规定了一套协议，具体可以自行学习，常见的参数有 波特率 校验位等，波特率是我们用得最多的参数。


通过板子的串口，可以和其它单片机或者 SOC 进行数据通信，比如可以在 MaixCAM 上实现人体检测功能，检测到坐标后通过串口发送给 STM32 单片机。

## MaixPy 中使用串口


对于 MaixCAM 默认从 USB 口引出了一个串口，可以插上配套的 Type-C 转接小板，就能直接使用上面的串口引脚，
也可以不用转接板，直接使用板子上的 `A16(TX)` 和 `A17(RX)`引脚, 和 USB 口引出的是同样的引脚，是等效的。


对于 MaixCAM 使用 USB 引出的串口时需要**注意**，Typc-C 正插和反插，转接小板上的 `RX` 和 `TX`会交换(默认 Type-C 母口朝前和丝印符合)，所以当你发现无法通信时，有可能就是 RX TX 反了，可以尝试将 Type-C 翻转一面插再看看通信是否正常。这个算是设计缺陷，不过一般也不会经常拔插所以适应一下也能接受。

将两个通信的板子双方连接好后（通信双发交叉连接 RX TX， 即一方 TX 发送到另一方的 RX， 双方 GND 连接到一起），就可以使用软件了。


通过 MaixPy 使用串口很简单：

```python
from maix import uart

devices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

先列出了系统的所有串口设备，然后这里使用了第一个，也就是上面说的 Type-C 出 引出的串口。

更多串口的 API 请看 [UART API 文档](../../../api/maix/peripheral/uart.md)

## MaixCAM 串口使用注意点

有开发者可能会问：为什么插上 USB 电脑没出现串口设备？
答： 因为设备的 USB 默认是 虚拟 USB 网卡，没有串口功能，如果要访问设备的终端，请使用 ssh 连接。

对于 MaixCAM, 从 Type-C 转接板引出的`串口0`直连到 `A16(TX)`和 `A17(RX)`引脚，可以直接接到其它设备比如单片机的串口引脚；
如果要和电脑通信，需要使用 USB 转串口小板(比如[这个](https://item.taobao.com/item.htm?spm=a1z10.5-c-s.w4002-24984936573.13.73cc59d6AkB9bS&id=610365562537))连接到电脑。

需要注意的是， **MaixCAM 的`串口0` 在开机时会打印一部分开机日志**， 启动完毕后会打印`serial ready`字样，如果和单片机通信需要注意丢弃这部分信息，如果出现系统启动出现问题也可以通过查看`串口0`的开机打印来诊断问题。


## 发送接收数据

这里使用了`write_str`函数来发送字符串，在`Python`中有`str`和`bytes`两种基础数据类型，前者是字符串，后者是原始字节数据，比如:
* `"A"` 调用`encode()`方法变成`b"A"`，反过来`b"A"`调用`decode()`方法变成`"A"`。
* `str` 没法显示一些不可见字符比如 ASCII 码中的值`0`，在字符串中也是`\0`一般作为结束符，在`bytes`类型中就可以用`b"\x00"`来储存。
* 对于非 ASCII 编码的字符串更有用，比如`UTF-8`编码中中文`好`是由三个字节`\xe5\xa5\xbd`来表示的，我们可以通过`"好".encode("utf-8")`得到`b"\xe5\xa5\xbd"`，也可以通过`b'\xe5\xa5\xbd'.decode("utf-8)`得到`"好"`。

所以如果我们需要发送字节数据，则用`write()`方法发送即可。

所以对于 `str` 类型，也可以不用`write_str`，而是使用`serial.write(str_content.encode())` 来发送。

另外如果你有一个 `list` 类型的数据，可以通过`bytes()`方法来构建一个`bytes`对象，比如
```python
a = [1, 2, 3]
serial.write(bytes(a))
```

同样，`read`方法获得的数据也是`bytes`类型。

## 其它写法

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

另外，这里循环里面加了一个 `sleep_ms` 是简单地释放一下 CPU，以达到程序不会占满 CPU 的效果，当然也有其它方式，这种方式最简单粗暴。


## 使用其它串口

每个引脚可能可以对应不同的外设功能，这也叫引脚复用，如下图，每个引脚对应了不同功能，比如`A17`引脚(板子的丝引标识)对应了`GPIOA17` `UART0_RX` `PWM5` 这三种功能，默认是`UART0_RX`。

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)


默认我们就能像上面直接使用`UART0`，对于其它串口的引脚默认都不是串口外设功能，所以要使用其它串口，需要先设置一下映射，使用`pinmap.set_pin_function`来设置。

这里以使用`UART1` 为例，先设置引脚映射选择引脚功能为串口，然后设备编号使用`/dev/ttyS1`，注意`uart.list_devices()` 默认不会返回需要手动映射的串口，所以直接手动传参就可以了：

```python
from maix import app, uart, pinmap, time

pinmap.set_pin_function("A18", "UART1_RX")
pinmap.set_pin_function("A19", "UART1_TX")

device = "/dev/ttyS1"

serial1 = uart.UART(device, 115200)
```

## 使用串口协议通信

基于串口，你可以按照你自己的习惯进行通信，直接发字符串结果，或者可以结合`Python`的`struct`库进行编码成二进制协议。

另外 MaixPy 也内置了一个通信协议可以直接使用。

这里的通信协议即：规定通信双方的以什么样的格式来传输内容，方便双方解析识别信息，是一个二进制协议，包括帧头、数据内容、校验等。
完整的协议定义在 [Maix 串口通信协议标准](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md)。
没有接触过通信协议可能看起来有点困难，结合下面的例子多看几遍就能理解了。


比如我们现在有一个物体检测，我们想检测到物体后通过串口发送给其它设备（比如 STM32 单片机或者 Arduino 单片机），告诉其我们检测到了什么物体，坐标是多少。

完整的例程：[MaixPy/examples/protocol/comm_protocol_yolov5.py](https://github.com/sipeed/MaixPy/tree/main/examples/protocol/comm_protocol_yolov5.py)

首先我们需要检测到物体，参考 `yolov5` 检测物体的例程即可，这里我们就省略其它细节，来看检测到的结果是什么样
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
可以看到`objs`是多个检测结果，这里在屏幕上进行画框了，我们也可以在这里想办法把结果通过串口发送出去。
这里我们不需要手动初始化串口，直接使用内置的`maix.comm, maix.protocol`模块，调用`comm.CommProtoco`会自动初始化串口，默认波特率是`115200`，串口协议的相关可以在设备`系统设置->通信协议`里面设置。
系统设置里面可能还有其它通信方式比如`tcp`，默认是`uart`，你也可以通过`maix.app.get_sys_config_kv("comm", "method")`来获取到当前设置的是不是`uart`。

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

这里通过`encode_objs`函数将所有检测到的物体信息打包成`bytes`类型的数据，然后用`p.report`函数将结果发送出去。

这里我们对`body`内容进行了一个简单的定义，即`2B x(LE) + 2B y(LE) + 2B w(LE) + 2B h(LE) + 2B idx ...`，
含义是：
* 这张图中检测到多个物体，在`body`中按顺序排列，每个目标占用 `2+2+2+2+2 = 10` 个字节的长度，一共有`body_len / 10`个物体。
* 第1、2个字节代表识别到的物体的左上角的 `x` 坐标，单位是像素，因为 yolov5 的结果这个坐标值有可能为负数，所以我们用一个`short`类型的值来表示，这里使用了小端编码（LE）。
> 这里小端即数值的低字节在前，比如坐标 `x` 为 `100`, 十六进制为 `0x64`，我们用两个字节的`short`来表示就是`0x0064`，这里小端编码成 `bytes` 就是`0x64`在前， 结果就是`b'\x64\x00'`。
* 同理，将后面的数据都依次编码，一个物体得到一个`10`字节长的`bytes`类型数据。
* 循环将所有物体信息编码并拼接成一个`bytes`。

在调用`report`函数时，底层会自动按照协议拼接上协议头、校验和等等，这是在另一端就能收到一帧完整的数据了。

在另一端收到信息后也要按照协议进行解码，如果接收端也是用 MaixPy 可以直接：
```python
while not app.need_exit():
    msg = p.get_msg()
    if msg and msg.is_report and msg.cmd == APP_CMD_DETECT_RES:
        print("receive objs:", decode_objs(msg.get_body()))
        p.resp_ok(msg.cmd, b'1')
```

如果是其它设备比如`STM32`或者`Arduino`则可以参考 [Maix 串口通信协议标准](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) 附录中的 C 语言函数进行编解码。








