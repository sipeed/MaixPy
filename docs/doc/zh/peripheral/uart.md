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


对于 MaixCAM 使用 USB 引出的串口时需要**注意**，Typc-C 正插和反插，转接小板上的 `RX` 和 `TX`会交换，所以当你发现无法通信时，有可能就是 RX TX 反了，可以尝试将 Type-C 翻转一面插再看看通信是否正常。这个算是设计缺陷，不过一般也不会经常拔插所以适应一下也能接受。

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









