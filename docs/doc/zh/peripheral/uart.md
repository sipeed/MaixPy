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


