---
title: MaixCAM MaixPy UART 串口使用介绍
update:
  - date: 2024-03-07
    author: Neucrack
    version: 1.0.0
    content: 初版文档
  - date: 2024-08-01
    author: Neucrack
    version: 1.1.0
    content: 优化文档，更多详细内容
  - date: 2025-08-08
    author: Neucrack
    version: 1.2.0
    content: 添加 MaixCAM2 支持
---

## 前置知识

请先学会使用[pinmap](./pinmap.md) 模块设置引脚功能。

要让一个引脚能使用 `UART` 功能，先用`pinmap`设置对应引脚功能为`UART`。


## 串口简介

串口是一种通信方式，包含了硬件和通信协议的定义。

* 硬件包括：
  * 3 个引脚： `GND`， `RX`， `TX`，通信双发**交叉连接** `RX` `TX`， 即一方 `TX` 发送到另一方的 `RX`， 双方 `GND` 连接到一起。
  * 控制器，一般在芯片内部，也叫 `UART` 外设，一般一个芯片有一个或者多个 `UART` 控制器，每个控制器有相对应的引脚。
* 串口通信协议： 为了让双方能顺利通信，规定了一套协议，即以什么样的时序通信，具体可以自行学习，常见的参数有 波特率 校验位等，波特率是我们用得最多的参数。


通过板子的串口，可以和其它单片机或者 SOC 进行数据通信，比如可以在 MaixCAM 上实现人体检测功能，检测到坐标后通过串口发送给 STM32/Arduino 单片机。


## 选择合适的 I2C 使用

首先我们需要知道设备有哪些引脚和 I2C，如图：

| 设备型号 | 引脚简图 | 引脚复用说明 |
| ------- | ------- | --- |
| MaixCAM | ![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg) | 板子丝印比如`A19`是引脚名，`UART1_TX`是功能名 |
| MaixCAM-Pro | ![maixcam_pro_io](/static/image/maixcam_pro_io.png) | 第一个名如`A19`是引脚名，对应`UART1_TX`是功能名 |
| MaixCAM2 | ![maixcam2_io](https://wiki.sipeed.com/hardware/assets/maixcam/maixcam2_pins.jpg) | 第一个名如`A21`是引脚名，对应`UART4_TX`是功能名  |

需要注意的是，引脚默认可能用做其它用途，最好避开这些引脚，请看[pinmap](./pinmap.md) 文档中的说明。

### MaixCAM/MaixCAM-Pro 串口使用注意点：

* 默认从 USB 口引出了一个串口0，可以插上配套的 Type-C 转接小板，就能直接使用上面的串口引脚，也可以不用转接板，直接使用板子上的 `A16(TX)` 和 `A17(RX)`引脚, 和 USB 口引出的是同样的引脚，是等效的。
* 对于 MaixCAM 使用 USB 引出的串口时需要**注意**，Typc-C 正插和反插，转接小板上的 `RX` 和 `TX`会交换(默认 **Type-C 母口朝前**和丝印符合)，所以当你发现无法通信时，有可能就是 RX TX 反了，可以尝试将 Type-C 翻转一面插再看看通信是否正常。这个算是设计缺陷，不过一般也不会经常拔插所以适应一下也能接受。
* **MaixCAM 的`串口0` 在开机时会打印一部分开机日志**， 启动完毕后会打印`serial ready`字样，如果和单片机通信需要注意丢弃这部分信息，如果出现系统启动出现问题也可以通过查看`串口0`的开机打印来诊断问题。
* MaixCAM 的 `TX`(`UART0`) 引脚也是启动模式检测引脚之一，所以在**串口0开机时不能是被拉低**的状态，不然会导致无法开机，是芯片的特性，如果你在做 `3.3v` 转 `5v` 的电平转换电路要十分注意不要默认拉低请保持浮空（可以考虑使用电平转换芯片）。以及如果你发现无法开机，也可以先检查一下 `TX` 是否被拉低了。
* 综上，`UART0` 如果你遇到了问题不好解决，建议使用其它串口比如`UART1`。
* `UART0` 也是系统默认`maix protocol` 串口。

### MaixCAM2 使用注意点

* `MaixCAM2`引出的串口很多，有`UART0 / UART1 / UART2 / UART3 / UART4`共 4 组串口，使用时不要混淆。
* `UART0`是系统终端和日志串口。


### 波特率限制

注意，不是所有波特率都能使用的，推荐没有特殊需求使用 `115200`，这是芯片都支持的，其它波特率误码率可能会很高或者驱动未支持导致数据传输丢失。

这里列举不同设备的常见测试可用波特率（欢迎PR）：
* `MaixCAM / MaixCAM-Pro`: `115200`。
* `MaixCAM2`: `115200`。理论最高能到`4000000 bits/s`，底层`baud = uart_clk /(小数分频 * 16)`，默认`uart_clk`是 `200000000`，小数分频值整数部分`uart_clk / (baud * 16)`，小数部分`round((uart_clk % (baud * 16)) * 16 / (baud * 16)) / 16`，比如`115200`计算出来分频器设置为`108.5`，实际验证精度`(115200 - (uart_clk / (108.5 * 16))) / 115200 = 0.0064%`，所以如果你切换波特率，也可以根据这个公式进行计算精度。


## 串口硬件接线

两个设备通信， 接三个引脚，`GND`， `RX`， `TX`，通信双发**交叉连接** `RX` `TX`， 即一方 `TX` 发送到另一方的 `RX`， 双方 `GND` 连接到一起即可。


## MaixPy 中使用串口


将两个通信的板子双方连接好后（通信双发交叉连接 RX TX， 即一方 TX 发送到另一方的 RX， 双方 GND 连接到一起），就可以使用软件了。


通过 MaixPy 使用串口，核心代码：
```python
from maix import uart

serial_dev = uart.UART("/dev/ttyS0", 115200)
serial_dev.write_str("Hello MaixPy")
```

`/dev/ttyS0` 是串口设备，可以通过`print(uart.list_devices())`看到所有串口设备。
一般`/dev/ttyS*`,`*`就是串口号。

对于默认对应引脚就是串口功能的串口可以这样直接使用，其它串口则需要先用`pinmap`映射引脚功能为对应的`UART`功能，然后创建`UART`对象即可：

```python
from maix import uart, pinmap, time, sys, err

# ports = uart.list_devices() # 列出所有串口

# get pin and UART number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_function = {
        "A21": "UART4_TX",
        "A22": "UART4_RX"
        # "B0": "UART2_TX",
        # "B1": "UART2_RX"
    }
    device = "/dev/ttyS4"
    # device = "/dev/ttyS2"
else:
    pin_function = {
        "A16": "UART0_TX",
        "A17": "UART0_RX"
        # "A19": "UART1_TX"
        # "A18": "UART1_RX",

    }
    device = "/dev/ttyS0"
    # device = "/dev/ttyS1"

for pin, func in pin_function.items():
    err.check_raise(pinmap.set_pin_function(pin, func), f"Failed set pin{pin} function to {func}")

# Init UART
serial_dev = uart.UART(device, 115200)
serial_dev.write_str("Hello MaixPy")
```

## 串口连接电脑

* 有开发者可能会问：为什么插上 USB 电脑没出现串口设备？
答： 因为设备的 USB 口是 USB 功能，不是 USB 转串口功能，而且默认会虚拟成 USB 网卡，如果要访问设备的终端，请使用 ssh 连接。

* 我想电脑和板子串口通信，怎么办？
答： 现代电脑一般只有 USB 口，所以想电脑和板子的 UART 通信，中间需要一个 USB 转 UART 的转接板，比如[这个](https://item.taobao.com/item.htm?spm=a1z10.5-c-s.w4002-24984936573.13.73cc59d6AkB9bS&id=610365562537)，USB 连接电脑，串口连接开发板的串口就能通信了。

* 我想在电脑看板子串口终端打印的日志，或者终端交互，怎么操作？
答：一般推荐通过网络 ssh 进行终端交互，如果遇到问题，可以用以下方法进入串口终端：
  * 对于 MaixCAM/MaixCAM-Pro： 将 USB 转 UART 的转接板和板子的`串口0`（`A16(TX)`和 `A17(RX)`）引脚交叉相连，提前将系统内`/boot/uEnv.txt`中的`consoledev`一行前面加`#`号注释掉或者直接删掉使能串口0作为终端，然后重启系统就能通过串口0看到开机日志和终端交互了。
  * 对于 MaixCAM2: 将 USB 转 UART 的转接板和板子的`串口0`(`U0T`/`U0R`)引脚交叉相连，就可以进行串口终端交互了，开机也会打印日志。


## 发送数据

主要有两个函数`write_str`和`write`函数。

`write_str`函数来发送字符串，`write`用来发送字节流，即`str`和`bytes`类型，两者可以互相转换，比如:
* `"A"` 调用`encode()`方法变成`b"A"`，反过来`b"A"`调用`decode()`方法变成`"A"`。
* `str` 没法显示一些不可见字符比如 ASCII 码中的值`0`，在字符串中也是`\0`一般作为结束符，在`bytes`类型中就可以用`b"\x00"`来储存。
* 对于非 ASCII 编码的字符串更有用，比如`UTF-8`编码中中文`好`是由三个字节`\xe5\xa5\xbd`来表示的，我们可以通过`"好".encode("utf-8")`得到`b"\xe5\xa5\xbd"`，也可以通过`b'\xe5\xa5\xbd'.decode("utf-8)`得到`"好"`。

所以如果我们需要发送字节数据，则用`write()`方法发送即可, 比如:
```python
bytes_content = b'\x01\x02\x03'
serial.write(bytes_content)
```

所以对于 `str` 类型，也可以不用`write_str`，而是使用`serial.write(str_content.encode())` 来发送。

如果你有其它类型的数据，想将它们变成一个**字符串发送**，可以使用`Python 字符串格式化`来创建一个字符串，比如：
想发送`I have xxx apple`，这里`xxx` 想用一个整型变量，则：
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

另外你也可以把数据编码成**二进制流数据发送**，比如前 4 个字节是十六进制的 `AABBCCDD`，中间发送一个 `int` 类型的数值，最后再加一个`0xFF`结尾，使用`struct.pack`来进行编码（看不懂可以看后文的介绍）：
```python
from struct import pack
num = 10
bytes_content = b'\xAA\xBB\xCC\xDD'
bytes_content += pack("<i", num)
bytes_content += b'\xFF'
print(bytes_content, type(bytes_content))
serial.write(bytes_content)
```
这里 `pack("<i", num)` 把 `num`编码为`int`类型即`4字节`的有符号数，`<`符号意思是小端编码，低位在前，这里`num = 10`，十六进制 `4 字节`表示就是`0x0000000A`，小端就是把低字节`0x0A`放在前面，得到一个`b'\x0A\x00\x00\x00'`的字节类型数据。
> 这里只举例使用`i`编码`int`类型的数据，还有其它类型比如`B`表示`unsigned char`等等，更多的`struct.pack`格式化用法可以自行搜索`python struct pack`。

这样最终发送的就是`AA BB CC DD 0A 00 00 00 FF`二进制数据了。


## 接收

使用`read`方法进行读取数据，直接：
```python
while not app.need_exit():
    data = serial.read()
    if data:
        print(data)
    time.sleep_ms(1)
```
同样，`read`方法获得的数据也是`bytes`类型，这里`read`会读取对方一次性发送的一串数据，如果没有数据就是`b''`即空字节。
这里用了`time.sleep_ms(1)`进行睡眠了`1ms`，用来释放 CPU，不让这个线程占用所有 CPU 资源，而且`1ms`不影响我们程序的效率，特别是在多线程时有用。

另外`read`函数有两个参数：
* `len`：代表想接收的最大长度，默认`-1`代表缓冲区有多少就返回多少，传`>0`的值则代表最多返回这个长度的数据。
* `timeout`：
  * 默认 `0` 代表从缓冲区读取数据立马返回数据，如果`len`为 `-1`则返回所有数据，如果指定了`len`则返回长度不超过`len` 的数据。
  * `<0` 代表一直等待直到接收到了数据才返回，如果`len`为 `-1`则等待到接收到数据才返回（一串连续接收到的数据，即阻塞式读取所有数据），如果指定了`len`则等待接收数量达到`len`才返回。
  * `>0` 代表无论有没有接收到数据，超过这个时间就会返回。
看起来有点复杂，常见的参数组合：
* `read()`: 即`read(-1, 0)`，从缓冲区读取收到的数据，通常是对方一次性发来的一串数据，等到对方没有发送（一个字符的发送时间内没有再发）就立刻返回。
* `read(len = -1, timeout = -1)`: 阻塞式读取一串数据，等到对方发送了数据并且一个字符的发送时间内没有再发才返回。
* `read(len = 10, timeout = 1000)`: 阻塞式读取 10 个字符，读取到 10 个字符或者 超过 1000ms 还没收到就返回已经收到的数据。

## 设置接收回调函数

在 MCU 开发中，串口收到数据通常会有中断事件发生， MaixPy 已经在底层处理好了中断，开发者无需再处理中断。
如果你想在接收到数据时调用一个回调函数，可以用`set_received_callback`设置回调函数：

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

在接收到数据后会在**另外一个线程**里调用设置的回调函数，因为是在另外的线程里调用的，所以不像中断函数要尽快退出函数，你可以在回调函数里处理一些事务再退出也是可以的，注意多线程常见问题。

使用回调函数的方式接收数据请不要再使用`read`函数读取，否则会读取出错。


## 更多串口例程

看[MaixPy examples](https://github.com/sipeed/MaixPy/tree/main/examples/peripheral/uart)。


## 串口API 文档

更多 API 看 [UART API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/uart.html)


## 应用层通信协议

### 概念和字符协议

串口只是规定了保证硬件通信的时序，为了让接收方知道发送方发送的字符流的含义，我们一般会规定一个应用通信协议。
比如发送放需要发送一个坐标，包含了`x, y`两个整型值，为了让接收方能理解我们发送的字节流的含义，我们规定：
* **帧头**：当我开始发送`$`符号时，就代表我要开始发送有效的数据啦。
> **内容**：设计一个开头符号的原因是串口是流式传输，比如发送两次`12345`有可能在某个时刻接收到了`12345123`这样的数据，第二帧的`45`还没有接收到，我们可以根据起始和结尾符号来判断一个完整的数据帧。
* x， y 的取值范围是 0~65535， 即两个字节的无符号短整型(`unsinged short`)，我会先发 x 再发 y，用逗号隔开，比如`10,20`。
* **帧尾**：最后我会再发一个`*`标记来代表我这次数据发送完成了。
这样发送一次数据就类似`$10,20*`这样一个字符串，对方如果用 C 语言接收和解析：
```c
// 1. 接收数据
// 2. 根据帧头帧尾判断是否接收完毕了，并将完整的一帧数据存到 buff 数组里面
// 3. 解析一帧数据
uint16_t x, y;
sscanf(buff, "$%d,%d*", &x, &y);
```

这样我们就制定了最简单的字符通信协议，具有一定的可靠性。
但是由于我们串口一般用的参数是`115200 8 N 1`，这里的`N`就是无奇偶校验，我们可以在自己的协议里面加一个**校验值**放在末尾，比如：
* 这里我们规定 x,y 后还有一个校验值，取值范围是 0 到 255，它的值为前面所有字符加起来的和对 255 取余。
* 这里以 `$10,20`举例，在`Python`只需要使用`sum`函数就可以`sum(b'$10,20') % 255 --> 20`，最终发送`$10,20,20*`。
* 接收放接收到数据后读取到校验值`20`，然后自己也同样的方式计算一遍`$10,20`的校验值，如果也是`20`说明数据传输没有发生错误，如果不相同我们则可以认为数据传输过程中发生了错误，可以丢弃等下一个数据包。

比如在 MaixPy 中，我们需要编码一个字符协议，直接使用 `Python 的字符串格式化`功能即可：
```python
x = 10
y = 20
content = "${},{}*".format(x, y)
print(content)
```

### 二进制通信协议

上面的字符协议有个很明显的特征，我们都是用可见字符的方式在传输数据，传输数据时有点就是简单，人眼能直接看懂；
缺点就是占用字符数量不固定，数据量比较大，比如`$10,20*`和`$1000,2000*`，同样的格式，数值不同长度不同，这里`1000`用了 4 个字符也就是4个字节，我们都知道一个无符号短整型（`uint16`）类型的数据只需要两个字节就能表示`0~65535`的取值范围，用这种表示方法可以少传输数据。
我们也知道可见字符可以通过`ASCII`码表转换成二进制表示形式，比如`$1000`查找`ASCII码表`换成二进制表示就是`0x24 0x31 0x30 0x30 0x30`一共 5 个字节，也就是我们实际传输数据的时候传输的二进制内容，如果现在我们用二进制的方式直接编码`1000`，即`0x03E8`，就可以直接发送`0x24 0x03 0xE8`，最终只需要发送 3 个字节，减少了通信开销。

另外这里`0x03E8`两个字节低位是`0xE8`，先发送低位`0xE8`我们称之为小端编码，反之则是大端编码，两个皆可，双方规定一致即可。

在 MaixPy 中，要将一个数值转换成 bytes 类型也很简单，使用`struct.pack`函数即可，比如这里的`0x03E8`也就是十进制的`1000`，我们用
```python
from struct import pack
b = pack("<H", 1000)
print(b)
```
这里`<H`表示小端编码，`H`表示一个 `uint16`类型的数据，最终得到`b'\xe8\x03'`的 bytes 类型数据。

同样的，二进制协议也可以有 帧头，数据内容，校验值，帧尾等，也可以不要帧尾，而是设计一个帧长的字段，看个人喜好即可。




### MaixPy MaixPy 内置通信协议

另外 MaixPy 也内置了一个通信协议可以直接使用，使用这个协议可以实现串口甚至 TCP 来切换应用、控制应用、获取应用发出的数据等。

比如 AI 检测应用检测到物体后发出的坐标就可以通过这个协议解析到。


## 其它教程

* [【MaixPy/MaixCAM】视觉利器 -- MaixCAM 入门教程二](https://www.bilibili.com/video/BV1vcvweCEEe/?spm_id_from=333.337.search-card.all.click) 看串口讲解部分
* [视觉模块和STM32如何进行串口通信](https://www.bilibili.com/video/BV175vWe5EfV/?spm_id_from=333.337.search-card.all.click&vd_source=6c974e13f53439d17d6a092a499df304)
* [[MaixCam]使用心得二：UART串口通信](https://blog.csdn.net/ButterflyBoy0/article/details/140577441)
* 更多请自行互联网搜索

## MaixCAM UART 串口排查指南

> 适用型号：MaixCAM / MaixCAM-Pro / MaixCAM2
> 参考文档：[MaixPy UART 串口使用介绍](https://wiki.sipeed.com/maixpy/doc/zh/peripheral/uart.html)

### 目录

1. [快速排查流程图](#1-快速排查流程图)
2. [问题分类排查](#2-问题分类排查)
   - [完全无法通信（收发均无数据）](#21-完全无法通信收发均无数据)
   - [能发不能收](#22-能发不能收)
   - [能收不能发](#23-能收不能发)
   - [收到乱码](#24-收到乱码)
   - [数据丢失或不完整](#25-数据丢失或不完整)
   - [USB 口相关问题](#26-usb-口相关问题)
   - [开机异常问题](#27-开机异常问题)
3. [引脚与串口映射速查表](#3-引脚与串口映射速查表)
4. [代码模板与示例](#4-代码模板与示例)
5. [FAQ 快问快答](#5-faq-快问快答)

### 快速排查流程图

```
串口通信异常
├── 1. 硬件接线是否正确？
│   ├── GND 是否共地？
│   ├── RX/TX 是否交叉连接？（A的TX → B的RX）
│   └── Type-C 转接板是否正插？（MaixCAM 独有问题）
├── 2. 引脚功能是否设置？
│   ├── 是否用 pinmap 设置了引脚功能为 UART？
│   └── 引脚是否与其它功能（WiFi、SPI等）冲突？
├── 3. 参数是否一致？
│   ├── 波特率是否匹配？
│   ├── 数据位 / 校验位 / 停止位是否一致？
│   └── 是否使用了推荐波特率 115200？
├── 4. 代码是否正确？
│   ├── 串口设备路径是否正确？（/dev/ttyS0, /dev/ttyS1...）
│   ├── 是否同时使用了 read 和 set_received_callback？（不可混用）
│   └── 是否加了 sleep 释放 CPU？
└── 5. 其它
    ├── 是否是 UART0 且被拉低导致无法开机？
    └── 是否使用了不支持的波特率？
```

## 问题分类排查

### 完全无法通信（收发均无数据）

**排查步骤：**

| 步骤 | 检查项 | 操作 |
|------|--------|------|
| ① | **接线检查** | 确认 GND 共地，RX/TX 交叉连接（A的TX→B的RX，A的RX→B的TX） |
| ② | **Type-C 转接板方向** | MaixCAM 使用 USB 引出的串口时，Type-C 正插和反插会让 RX/TX 交换。**尝试将 Type-C 翻转一面再插** |
| ③ | **引脚功能映射** | 非默认串口引脚必须先用 `pinmap.set_pin_function()` 设置功能 |
| ④ | **串口设备路径** | 用 `uart.list_devices()` 确认实际设备路径，一般 `/dev/ttyS*` 中 `*` 就是串口号 |
| ⑤ | **波特率匹配** | 两端波特率必须一致，推荐 **115200** |

**常见代码错误：**
```python
# ❌ 错误：没有设置引脚功能就直接使用
serial_dev = uart.UART("/dev/ttyS1", 115200)

# ✅ 正确：先设置引脚功能
from maix import uart, pinmap, err
err.check_raise(pinmap.set_pin_function("A19", "UART1_TX"), "Failed")
err.check_raise(pinmap.set_pin_function("A18", "UART1_RX"), "Failed")
serial_dev = uart.UART("/dev/ttyS1", 115200)
```

### 能发不能收

**排查步骤：**

| 步骤 | 检查项 | 操作 |
|------|--------|------|
| ① | **RX 引脚接线** | 确认本端的 RX 引脚连接到了对方的 TX 引脚 |
| ② | **RX 引脚功能映射** | TX 和 RX 都需要设置 pinmap，不能只设 TX |
| ③ | **read 参数** | 检查 `read()` 的 `timeout` 参数，`timeout=0` 可能返回空 |
| ④ | **回调冲突** | 如果设置了 `set_received_callback`，**不要再调用 `read()`**，否则会读取出错 |
| ⑤ | **对方是否在发送** | 用逻辑分析仪或万用表确认对方 TX 引脚有信号输出 |

**推荐读取方式：**
```python
# 方式一：轮询读取（推荐新手）
while not app.need_exit():
    data = serial.read()       # read(-1, 0)：有数据立即返回
    if data:
        print("收到:", data)
    time.sleep_ms(1)           # 释放 CPU，必须加！

# 方式二：阻塞读取
data = serial.read(len=-1, timeout=-1)  # 一直等到收到数据才返回

# 方式三：回调函数（不能同时用 read）
def on_received(serial, data):
    print("收到:", data)
serial.set_received_callback(on_received)
while not app.need_exit():
    time.sleep_ms(100)
```

### 能收不能发

| 步骤 | 检查项 | 操作 |
|------|--------|------|
| ① | **TX 引脚接线** | 确认本端 TX 连接到对方 RX |
| ② | **TX 引脚功能映射** | 检查 pinmap 是否设置了 TX 功能 |
| ③ | **数据类型** | `write_str()` 发送字符串，`write()` 发送 bytes，确认使用的函数正确 |
| ④ | **串口初始化** | 确认 `UART()` 对象创建成功，没有报错 |

**发送数据类型说明：**
```python
# 发送字符串
serial.write_str("Hello")

# 发送字节流
serial.write(b'\x01\x02\x03')

# 字符串转字节流
serial.write("Hello".encode("utf-8"))

# 中文发送（必须 encode）
serial.write("你好".encode("utf-8"))  # → b'\xe5\xa5\xbd'
```

### 收到乱码

**最大概率原因：波特率不匹配！**

| 排查项 | 说明 |
|--------|------|
| **波特率不一致** | 两端必须使用相同波特率，最常见原因是写错了其中一端的波特率 |
| **使用了不支持的波特率** | 芯片对波特率有精度要求，非标波特率可能导致误码，**强烈推荐 115200** |
| **编码不一致** | 对方发的是 GBK 编码，你用 UTF-8 解码就会乱码 |
| **电平不匹配** | 对方是 5V TTL 电平，MaixCAM 是 3.3V，需要电平转换 |

**波特率精度说明（MaixCAM2）：**

底层时钟 200MHz，分频公式：
```
baud = uart_clk / (小数分频 × 16)
```
例如 115200 时，分频器设置为 108.5，精度误差仅 **0.0064%**，完全可用。

> ⚠️ **MaixCAM / MaixCAM-Pro：仅验证 115200 可靠可用，其它波特率误码率可能很高。**

### 数据丢失或不完整

| 排查项 | 说明 |
|--------|------|
| **read 时没有加 sleep** | 循环中必须加 `time.sleep_ms(1)` 释放 CPU |
| **read 的 len 参数限制** | `read(len=10)` 最多只返回 10 字节，超出部分可能丢失 |
| **缓冲区溢出** | 对方发送太快、处理太慢，导致缓冲区溢出 |
| **帧协议不完整** | 没有帧头帧尾校验，导致粘包/拆包问题 |
| **回调和 read 混用** | 设置了 callback 又调用 read，会导致数据读取出错 |

**防止数据丢失的读取模式：**
```python
# 方式一：指定长度 + 超时（推荐定长协议）
data = serial.read(len=10, timeout=1000)  # 读 10 字节，最多等 1 秒

# 方式二：循环拼接（适合变长协议）
buffer = b''
while not app.need_exit():
    data = serial.read()
    if data:
        buffer += data
        # 按帧头帧尾解析 buffer
        while b'$' in buffer and b'*' in buffer:
            start = buffer.index(b'$')
            end = buffer.index(b'*', start)
            frame = buffer[start+1:end]
            buffer = buffer[end+1:]
            print("解析到帧:", frame)
    time.sleep_ms(1)
```

### USB 口相关问题

> **Q：为什么插上 USB 电脑没出现串口设备？**

**A：** MaixCAM 的 USB 口是 **USB 功能**（网络/存储），**不是 USB 转串口**。默认虚拟成 USB 网卡。

**解决方案：**
- 电脑访问终端 → 使用 **SSH** 连接（`ssh root@<设备IP>`）
- 电脑串口通信 → 需要额外购买 **USB 转 UART 转接板**，连接板子的串口引脚

```
电脑 ──USB──> [USB转UART转接板] ──TX/RX/GND──> MaixCAM 串口引脚
```

### 开机异常问题

MaixCAM / MaixCAM-Pro 的 **UART0** 有两个特殊限制：

| 问题 | 原因 | 解决 |
|------|------|------|
| **无法开机** | UART0 的 TX 引脚（A16）被外部电路拉低 | 检查 A16 是否被拉低，保持浮空或使用电平转换芯片 |
| **开机日志干扰通信** | UART0 开机会打印日志，直到出现 `serial ready` | 单片机端需丢弃开机阶段的数据；或改用 UART1 |
| **UART0 被系统占用** | UART0 是默认的 `maix protocol` 串口和系统终端 | 遇到问题建议换用 UART1 |

> ⚠️ **如果你做了 3.3V 转 5V 电平转换电路，务必确保 TX 默认不是拉低状态！这是芯片特性，TX 拉低 = 无法开机。**

### 引脚与串口映射速查表 MaixCAM / MaixCAM-Pro

| 串口 | TX 引脚 | RX 引脚 | 设备路径 | 备注 |
|------|---------|---------|----------|------|
| UART0 | A16 | A17 | `/dev/ttyS0` | USB 口引出的同一个串口；系统日志串口；开机打印日志 |
| UART1 | A19 | A18 | `/dev/ttyS1` | 推荐用于自定义通信 |

> **注意：** 引脚默认可能用作其它用途（如 SPI、WiFi），使用前请查看 [PINMAP 文档](https://wiki.sipeed.com/maixpy/doc/zh/peripheral/pinmap.html)。

### MaixCAM2

| 串口 | TX 引脚 | RX 引脚 | 设备路径 | 备注 |
|------|---------|---------|----------|------|
| UART0 | U0T | U0R | `/dev/ttyS0` | 系统终端和日志串口 |
| UART1 | — | — | `/dev/ttyS1` | — |
| UART2 | B0 | B1 | `/dev/ttyS2` | — |
| UART3 | — | — | `/dev/ttyS3` | — |
| UART4 | A21 | A22 | `/dev/ttyS4` | 板上默认引脚 |

### FAQ 快问快答

| # | 问题 | 回答 |
|---|------|------|
| 1 | 插上 USB 电脑识别不到串口？ | 正常，USB 口是网络/存储功能，不是串口。需用 SSH 连接或额外的 USB 转 UART 转接板。 |
| 2 | Type-C 正插反插有区别吗？ | **MaixCAM 有区别！** 正插和反插会交换 RX/TX，通信不上时试试翻转 Type-C。 |
| 3 | 推荐用哪个波特率？ | **115200**，这是唯一在所有型号上都验证可靠的波特率。 |
| 4 | UART0 和 UART1 选哪个？ | **推荐 UART1**。UART0 是系统串口，有开机日志干扰、系统占用、TX 拉低无法开机等问题。 |
| 5 | write_str 和 write 有什么区别？ | `write_str` 发送字符串（str），`write` 发送字节流（bytes）。中文/二进制数据用 `write` + `encode()`。 |
| 6 | read 和 callback 能同时用吗？ | **不能！** 设置了 `set_received_callback` 就不要再调用 `read()`，否则读取出错。 |
| 7 | 怎么知道我的串口设备路径？ | `from maix import uart; print(uart.list_devices())` |
| 8 | 串口0开机打印的乱码是什么？ | 那是系统启动日志，到 `serial ready` 为止。单片机端需丢弃这部分数据。 |
| 9 | 接了电平转换板但无法开机？ | 检查 UART0 TX（A16）是否被默认拉低，芯片特性：TX 拉低 = 无法开机。保持浮空或使用电平转换芯片。 |
| 10 | 发送中文出现乱码？ | 确保发送时 `encode("utf-8")`，接收端也要用 UTF-8 解码。 |




