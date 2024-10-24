---
title: MaixCAM MaixPy UART 串口使用介绍
---

## 串口简介

串口是一种通信方式，包含了硬件和通信协议的定义。

* 硬件包括：
  * 3 个引脚： `GND`， `RX`， `TX`，通信双发**交叉连接** `RX` `TX`， 即一方 `TX` 发送到另一方的 `RX`， 双方 `GND` 连接到一起。
  * 控制器，一般在芯片内部，也叫 `UART` 外设，一般一个芯片有一个或者多个 `UART` 控制器，每个控制器有相对应的引脚。
* 串口通信协议： 为了让双方能顺利通信，规定了一套协议，即以什么样的时序通信，具体可以自行学习，常见的参数有 波特率 校验位等，波特率是我们用得最多的参数。


通过板子的串口，可以和其它单片机或者 SOC 进行数据通信，比如可以在 MaixCAM 上实现人体检测功能，检测到坐标后通过串口发送给 STM32/Arduino 单片机。

## MaixPy 中使用串口


对于 MaixCAM 默认从 USB 口引出了一个串口，可以插上配套的 Type-C 转接小板，就能直接使用上面的串口引脚，
也可以不用转接板，直接使用板子上的 `A16(TX)` 和 `A17(RX)`引脚, 和 USB 口引出的是同样的引脚，是等效的，具体看接口图：

![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)
![maixcam_pro_io](/static/image/maixcam_pro_io.png)


对于 MaixCAM 使用 USB 引出的串口时需要**注意**，Typc-C 正插和反插，转接小板上的 `RX` 和 `TX`会交换(默认 **Type-C 母口朝前**和丝印符合)，所以当你发现无法通信时，有可能就是 RX TX 反了，可以尝试将 Type-C 翻转一面插再看看通信是否正常。这个算是设计缺陷，不过一般也不会经常拔插所以适应一下也能接受。

将两个通信的板子双方连接好后（通信双发交叉连接 RX TX， 即一方 TX 发送到另一方的 RX， 双方 GND 连接到一起），就可以使用软件了。


通过 MaixPy 使用串口很简单：

```python
from maix import uart

device = "/dev/ttyS0"
# ports = uart.list_devices() # 列出当前可用的串口

serial = uart.UART(device, 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

这里使用了第一个串口`/dev/ttyS0`，也就是上面说的 `Type-C` 出 引出的串口。

更多串口的 API 在 [UART API 文档](../../../api/maix/peripheral/uart.md)。

## MaixCAM 串口使用注意点

### TX 引脚注意点

MaixCAM 的 `TX`(`UART0`) 引脚在开机时**不能是被拉低**的状态，不然会导致无法开机，是芯片的特性，如果你在做 `3.3v` 转 `5v` 的电平转换电路要十分注意不要默认拉低请保持浮空（可以考虑使用电平转换芯片）。

以及如果你发现无法开机，也可以先检查一下 `TX` 是否被拉低了。

## 串口连接电脑

有开发者可能会问：为什么插上 USB 电脑没出现串口设备？
答： 因为设备的 USB 默认是 虚拟 USB 网卡，没有串口功能，如果要访问设备的终端，请使用 ssh 连接。

对于 MaixCAM, 从 Type-C 转接板引出的`串口0`直连到 `A16(TX)`和 `A17(RX)`引脚，可以直接接到其它设备比如单片机的串口引脚；
如果要和电脑通信，需要使用 USB 转串口小板(比如[这个](https://item.taobao.com/item.htm?spm=a1z10.5-c-s.w4002-24984936573.13.73cc59d6AkB9bS&id=610365562537))连接到电脑。

## 开机日志输出

需要注意的是， **MaixCAM 的`串口0` 在开机时会打印一部分开机日志**， 启动完毕后会打印`serial ready`字样，如果和单片机通信需要注意丢弃这部分信息，如果出现系统启动出现问题也可以通过查看`串口0`的开机打印来诊断问题。


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


## 使用其它串口

每个引脚可能可以对应不同的外设功能，这也叫引脚复用，如下图，每个引脚对应了不同功能，比如`A17`引脚(板子的丝引标识)对应了`GPIOA17` `UART0_RX` `PWM5` 这三种功能，默认是`UART0_RX`。

![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)
![maixcam_pro_io](/static/image/maixcam_pro_io.png)


默认我们就能像上面直接使用`UART0`，对于其它串口的引脚默认都不是串口外设功能，所以要使用其它串口，需要先设置一下映射，使用`pinmap.set_pin_function`来设置。

这里以使用`UART1` 为例，先设置引脚映射选择引脚功能为串口，然后设备编号使用`/dev/ttyS1`，注意`uart.list_devices()` 默认不会返回需要手动映射的串口，所以直接手动传参就可以了：

```python
from maix import app, uart, pinmap, time

pinmap.set_pin_function("A18", "UART1_RX")
pinmap.set_pin_function("A19", "UART1_TX")

device = "/dev/ttyS1"

serial1 = uart.UART(device, 115200)
```

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

APP_CMD_ECHO = 0x01        # 自定义命令 1, 测试用，这里没用到，保留
APP_CMD_DETECT_RES = 0x02  # 自定义命令 2, 发送检测到的物体信息
                           # 可以根据自己的应用自定义更多的命令

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


## 其它教程

* [【MaixPy/MaixCAM】视觉利器 -- MaixCAM 入门教程二](https://www.bilibili.com/video/BV1vcvweCEEe/?spm_id_from=333.337.search-card.all.click) 看串口讲解部分
* [视觉模块和STM32如何进行串口通信](https://www.bilibili.com/video/BV175vWe5EfV/?spm_id_from=333.337.search-card.all.click&vd_source=6c974e13f53439d17d6a092a499df304)
* [[MaixCam]使用心得二：UART串口通信](https://blog.csdn.net/ButterflyBoy0/article/details/140577441)
* 更多请自行互联网搜索




