---
title: MaixCAM MaixPy 使用 Modbus 协议
---

## Modbus 简介

Modbus 是一个应用层总线协议，传输层基于 UART 或者 TCP。
使用它可以实现一个总线上挂多个设备，实现一对多通信。


## Modbus 和 Maix 应用通信协议的区别

* **Maix 应用通信协议**：
  * **通信方式**：一对一通信。
  * **通信模式**：全双工通信，双方都可以主动发送消息，实现更加实时的交互。
  * **数据灵活性**：数据长度和类型没有限制，灵活支持多种数据结构。
  * **MaixPy内置**： MaixCAM MaixPy 内置了这个协议，部分应用默认数据输出用这个协议，在 MaixPy 生态中使用相同的协议有利于应用生态繁荣。
  * **应用场景**：适用于一对一实时性要求高、需要双向数据传输的场景，比如 AI 推理结果传输和控制命令反馈，以及 Maix 应用信息读取和控制。

* **Modbus**：
  * **通信方式**：总线协议，支持一对多通信。
  * **通信模式**：只能由主机主动发起读写操作，从机的数据更新需要主机轮询获取，从机本质上可以看作具有多组寄存器的传感器。
  * **数据类型**：数据以寄存器为单位，从机通过多个可读写或只读的寄存器实现数据交换。
  * **应用场景**：适用于工业自动化中传感器或设备的数据采集与监控，尤其是在需要主从结构的情况下。

## MaixCAM MaixPy 使用 Modbus

MaixPy 适配了 modbus 协议, 主机和从机模式均支持，RTU（UART）和 TCP 模式均支持，底层使用了开源项目 [libmodbus](https://libmodbus.org/)，

## MaixCAM MaixPy 作为 Modbus 从机

作为从机时，可以将 MaixCAM 看作是一个有几组可读写寄存器的模块。

包含了几组寄存器，它们的区别就是值类型不同，以及有的能读写，有的只能读，寄存器组包括：
* `coils`寄存器组： 布尔值，可读写。
* `discrete input`：布尔值，可读不可写。
* `input registers`：16bit int 值，可读不可写。
* `holding registers` 16bit int 值，可读可写.


每组寄存器的地址和长度在从机初始化时自由指定，根据你的应用需求设置即可。

以下是例程，更多代码请看源码例程(`examples/protocol/comm_modbus_xxx.py`):

RTU（UART）：

```python
from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    modbus.Mode.RTU,    # modbus 模式选择为 rtu
    "/dev/ttyS0",       # 选择与主机通信的串口
    0x00, 10,           # coils 开始地址以及该组寄存器数量
    0x00, 10,           # discrete input 开始地址以及该组寄存器数量
    0x00, 10,           # input registers 开始地址以及该组寄存器数量
    0x00, 10,           # holding registers 开始地址以及该组寄存器数量
    115200, 1,          # 115200波特率, 默认为 8N1, 后面的 1 代表 rtu 的从机地址
    0, False            # tcp 端口号, 我们使用的是 rtu, 随便填写即可, 后者为 是否打印 debug 信息
)

"""
以 coils 寄存器组为例, 起始地址为 0x00, 数量为 10, 代表该从机 coils 寄存器组的地址范围为 0x00~0x09 共 10 个寄存器, 每个寄存器存储一个布尔值.
"""

# 读取当前 input registers 寄存器组里的所有值
# 寄存器内初始值均为 0
old_ir = slave.input_registers()
print("old ir: ", old_ir)

# 将列表内的值从引索2开始更新到 input registers 中
# 寄存器组内数值将变成 [0x00 0x00 0x22 0x33 0x44 0x00 0x00 0x00 0x00 0x00]
data : list[int] = [0x22, 0x33, 0x44]
slave.input_registers(data, 2)
# 读取, 打印验证
new_ir = slave.input_registers()
print("new ir:", new_ir)


while not app.need_exit():
    # 等待主机的读写操作
    if err.Err.ERR_NONE != slave.receive(2000): #timeout 2000ms
        continue

    # 获取主机的操作类型
    rtype = slave.request_type()
    # 如果主机想要读取 holding registers
    if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
        # 准备数据
        # 获取并查看当前 holding registers 内数据
        print("master read hr")
        hr = slave.holding_registers()
        print("now hr: ", hr)

        # 更新 holding registers 内所有数据
        hr = [x+1 for x in hr]
        print("now we make hr+1: ", hr)
        print("update hr")
        slave.holding_registers(hr)
    # else ... 处理其他操作

    # 自动处理主机请求, 自动更新寄存器值
    slave.reply()
```

TCP：

```python
from maix.comm import modbus
from maix import app, err

slave = modbus.Slave(
    modbus.Mode.TCP,    # 模式: TCP
    "",                 # 保持空即可
    0x00, 10,
    0x00, 10,
    0x00, 10,
    0x00, 10,
    0, 1,               # 我们使用的是 TCP 模式, 忽略波特率和rtu地址即可
    502, False         # TCP 端口号, 后者为 是否打印 debug 信息
)

### 以下代码与 RTU 部分一致

old_ir = slave.input_registers()
print("old ir: ", old_ir)
data : list[int] = [0x22, 0x33, 0x44]
slave.input_registers(data, 3)
new_ir = slave.input_registers()
print("new ir:", new_ir)

while not app.need_exit():
    if err.Err.ERR_NONE != slave.receive(2000): #timeout 2000ms
        continue

    rtype = slave.request_type()
    if rtype == modbus.RequestType.READ_HOLDING_REGISTERS:
        print("master read hr")
        hr = slave.holding_registers()
        print("now hr: ", hr)
        hr = [x+1 for x in hr]
        print("now we make hr+1: ", hr)
        print("update hr")
        slave.holding_registers(hr)

    slave.reply()
```

可以看到这里接收到来自主机的读取请求后调用`slave.reply()`就会自动回复主机要读取的数据了，以及这里展示了更改本身的寄存器值。

有关 Modbus API 的详细说明请看 [Modbus API 文档](../../../api/maix/comm/modbus.md).

## MaixCAM MaixPy 作为 Modbus 主机

主机则可以主动读写从机的数据，例程(以源码例程`examples/protocol/comm_modbus_xxx.py`为准)：

```python
from maix import pinmap, app, err, time, thread
from maix.comm import modbus


REGISTERS_START_ADDRESS = 0x00
REGISTERS_NUMBER = 10

RTU_SLAVE_ID = 1
RTU_BAUDRATE = 115200

def master_thread(*args):
    if pinmap.set_pin_function("A19", "UART1_TX") != err.Err.ERR_NONE:
        print("init uart1 failed!")
        exit(-1)
    if pinmap.set_pin_function("A18", "UART1_RX") != err.Err.ERR_NONE:
        print("init uart1 failed!")
        exit(-1)

    # modbus.set_master_debug(True)

    master = modbus.MasterRTU(
        "/dev/ttyS1",
        RTU_BAUDRATE
    )

    while not app.need_exit():
        hr = master.read_holding_registers(
            RTU_SLAVE_ID,
            REGISTERS_START_ADDRESS,
            REGISTERS_NUMBER,
            2000
        )
        if len(hr) == 0:
            continue
        print("Master read hr: ", hr)
        time.sleep(1)

master_thread(None)
```

可以看到这里用 串口1 作为主机从从机读取寄存器值。


