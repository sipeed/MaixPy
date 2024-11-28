---
title: MaixCAM MaixPy Maix 应用通信协议
---


## 通信协议简介

为了让两个设备能够实现稳定通信，简单地说，一般从底往上有几个层次：
* 硬件层：比如 `UART` 使用 `TX` `RX` `GND` 三根线，也有可能是无线的，比如 WiFi。
* 传输层：使用传输控制协议来实现数据的稳定传输，比如 `UART` 协议规定了波特率、停止位、校验位来保证数据正确传输，比如 `TCP` 协议也类似。
* 应用层：从传输层获得的数据是流式数据（简单理解成一长串没有标点符号的数据），为了让应用理解哪些数据是什么含义，一般应用会自己定义一份应用层通信协议来规范传输的内容（简单理解成给传输的数据中间加标点符号方便接收方知道断句）。

举个例子：
应用层协议规定：一包数据以 `$`开头
A 发送两包数据给 B: `$12345$67890`，B收到后就知道 A 发送了两包数据，分别是`12345`和`67890`，如果没有这个协议，那 A 发送`12345` 然后发送 `67890`， 由于是流式传输 B 收到的数据可能是`1234567890`， 我们就不知道是发了一次还是发了两次了。


## 字符协议和二进制协议

**字符协议**：
前面举了简单的例子给没一包加`$`符号来区别每一包的开头，如果想发送数值`123`，直接发送`$123`字符串，即人类都可以直接看懂的，接收方需要将`123`字符串转换为 `int` 类型，比如 C 语言中可以
```c
int value;
sscanf(buff, "$%d", &value);
```

**二进制协议**：
可以看到字符协议为了发送`123`这个数值，用了`4`个字节，而且接收方还要做解析将字符串转为 int 类型，用二进制协议则可以减少传输的字节数量而且接收方也更好处理。
我们发送`0x24 0x7B` 即可， `0x24` 即 `$` 的十六进制表示（查 ASCII 码表）， `0x7B` 即 十进制`123`的十六进制表示，可以看到这里只发送了两个字节就完成了字符协议 4 个字节完成的工作，同时接收放直接读取第二个字节`0x7B` 就能使用这个值，比如 C 语言中直接`uint8_t value = buff[1]`;

当然这里只是简单说明让你理解两者，实际还需要根据不同使用场景两者各有优势，以及还会加其它考虑比如校验值等，这里就不多说了，可以自行思考和学习以及在下面的 Maix 通信协议实践。

## Maix 应用通信协议

Maix 应用通信协议是一个应用层通信协议，传输层基于 UART 或者 TCP。

包括了：规定通信双方的以什么样的格式来传输内容，方便双方解析识别信息，是一个二进制协议，包括帧头、数据内容、校验等。


完整的协议定义在 [Maix 应用通信协议标准](https://wiki.sipeed.com/maixcdk/doc/zh/convention/protocol.html)。 （写到 MaixCDK 文档中是因为 MaixCDK 也同样使用这份协议）

没有接触过通信协议可能看起来有点困难，结合下面的例子多看几遍就能理解了。
在 `MaixPy` 这边已经封装好了`API`，可以很简单地使用，在其它单片机或者芯片上可能需要实现一下协议，可以在[Maix 应用通信协议标准](https://wiki.sipeed.com/maixcdk/doc/zh/convention/protocol.html) 附录找找有没有对应的实现。


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
    disp.show(img)
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

如果是其它设备比如`STM32`或者`Arduino`则可以参考 [Maix 应用通信协议标准](https://wiki.sipeed.com/maixcdk/doc/zh/convention/protocol.html) 附录中的 C 语言函数进行编解码。


