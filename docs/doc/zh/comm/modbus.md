---
title: MaixCAM MaixPy 使用 Modbus 协议
---

MaixPy 适配了 modbus 协议, 其底层是 [libmodbus](https://libmodbus.org/).

在 MaixPy 上使用 modbus 协议非常简单, 您只需要知道:

* 当您使用 modbus.Slave 时, MaixCAM(Pro) 就是一个从设备(比如说作为传感器模块), 控制该模块的就是一个主机(比如说您的MCU/PC), 您的主机只需要像读写芯片寄存器一样从从设备读写寄存器即可.

* 您可以简单理解为:

    > 对主机来说, `coils` 是可读可写寄存器组, 存储一组布尔值; `discrete input` 是可读不可写寄存器组, 存储一组布尔值; `input registers` 是可读不可写寄存器组, 存储一组 16bit int值; `holding registers` 是可读可写寄存器组, 存储一组 16bit int 值.

    > 对从设备来说, 所有寄存器组可读可写, 且可自定义分配各组寄存器的大小, 其余特性跟上述主机视角一致.

直接上例程:

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
    5020, False         # TCP 端口号, 后者为 是否打印 debug 信息
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

这样, 我们就可以将 MaixCAM(Pro) 作为一个从设备, 主机可以随时读(写)其中的寄存器.


有关 Modbus API 的详细说明请看 [Modbus API 文档](../../../api/maix/comm/modbus.md).
