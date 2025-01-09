---
title: MaixCAM MaixPy 电源管理单元
update:
  - date: 2024-11-08
    author: 916BGAI
    version: 1.0.0
    content: 初版文档
---

<br/>

>! 警告 ！！！
>设置错误的电压可能会损坏 `MaixCAM-Pro`。除非明确了解调整目的和后果，否则请勿修改 `DCDC2~DCDC5`、`ALDO1~ALDO4` 和 `BLDO1~BLDO2` 的电压。

## 简介

`MaixCAM-Pro` 板载了 `AXP2101` 电源管理单元，提供多通道电源输出、充电管理以及系统保护功能。`AXP2101` 支持线性充电，拥有 `5` 个 `DC-DC` 通道和 `11` 个 `LDO` 通道，能够满足多种电源需求。它还配备了多通道 `ADC`，用于实时监控电压和温度，并集成了过压、过流和过温等保护功能，确保系统的稳定性和安全性。

> MaixCAM 没有板载电源管理单元，如需使用电源管理功能请自行外接。

## MaixPy 中使用电源管理单元

使用 `PMU` 模块操作 `AXP2101` 设备。

示例代码:

```python
from maix import time, app
from maix.ext_dev import pmu

p = pmu.PMU("axp2101")

# Get battery percent
print(f"Battery percent: {p.get_bat_percent()}%")

# Set the max battery charging current
p.set_bat_charging_cur(1000)
print(f"Max charging current: {p.get_bat_charging_cur()}mA")

# Set DCDC1 voltage (!!! Do not modify the voltage of other channels,
# as it may damage the device.)
old_dcdc1_voltage = p.get_vol(pmu.PowerChannel.DCDC1)
print(f"Old DCDC1 voltage: {old_dcdc1_voltage}mV")
p.set_vol(pmu.PowerChannel.DCDC1, 3000)
new_dcdc1_voltage = p.get_vol(pmu.PowerChannel.DCDC1)
print(f"New DCDC1 voltage: {new_dcdc1_voltage}mV")

# Get all channel voltages
channels = [
    pmu.PowerChannel.DCDC1, pmu.PowerChannel.DCDC2, pmu.PowerChannel.DCDC3,
    pmu.PowerChannel.DCDC4, pmu.PowerChannel.DCDC5, pmu.PowerChannel.ALDO1,
    pmu.PowerChannel.ALDO2, pmu.PowerChannel.ALDO3, pmu.PowerChannel.ALDO4,
    pmu.PowerChannel.BLDO1, pmu.PowerChannel.BLDO2
]

print("------ All channel voltages: ------")
for channel in channels:
    print(f"{channel.name}: {p.get_vol(channel)}")
print("-----------------------------------")

# Poweroff (Important! Power will be cut off immediately)
# p.poweroff()

while not app.need_exit():
    time.sleep_ms(1000)
```

> 也可以使用 `AXP2101` 模块对电源管理单元进行设置。使用方法和 `PMU` 模块类似，可以参考例程 [axp2101_example.py](https://github.com/sipeed/MaixPy/blob/main/examples/ext_dev/pmu/pmu_axp2101/axp2101_example.py)

初始化 `PMU` 对象，调用 `get_bat_percent()` 即可获取当前电池电量。调用 `set_bat_charging_cur()` 可以设置最大充电电流。

调用 `poweroff()` 设备将立即断电。在使用前，请确保将内存中的数据同步到磁盘。

调用 `set_vol()` 和 `get_vol()` 方法可以分别设置和读取 `DC-DC` 和 `LDO` 通道的电压。当前支持对 `AXP2101` 的以下通道进行电压设置：`DCDC1~DCDC5`、`ALDO1~ALDO4` 和 `BLDO1~BLDO2`。

>! 警告 ！！！
>设置错误的电压可能会损坏 `MaixCAM-Pro`。除非明确了解调整目的和后果，否则请勿修改 `DCDC2~DCDC5`、`ALDO1~ALDO4` 和 `BLDO1~BLDO2` 的电压。若需测试，请使用 `DCDC1` 通道。

有关 PMU API 的详细说明请看 [PMU API 文档](../../../api/maix/ext_dev/pmu.md)