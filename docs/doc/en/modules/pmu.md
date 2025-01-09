---
title: MaixCAM MaixPy Power Management Unit
update:
  - date: 2024-11-08
    author: 916BGAI
    version: 1.0.0
    content: Initial document
---

<br/>

>! Warning !!!
>Setting incorrect voltages may damage the `MaixCAM-Pro`. Do not modify the voltages of `DCDC2~DCDC5`, `ALDO1~ALDO4`, and `BLDO1~BLDO2` unless you fully understand the purpose and consequences of the adjustment.

## Introduction

The `MaixCAM-Pro` is equipped with the `AXP2101` Power Management Unit (PMU), providing multi-channel power outputs, charging management, and system protection functions. The `AXP2101` supports linear charging and features `5` `DC-DC` channels and 11 `LDO` channels, meeting a variety of power requirements. It also comes with multiple-channel `ADCs` for real-time monitoring of voltage and temperature, and integrates protection features such as over-voltage, over-current, and over-temperature to ensure system stability and safety.

> The MaixCAM does not have an onboard power management unit. If power management functionality is required, please connect an external power management unit.

## Using Power Management Unit in MaixPy

Operate the AXP2101 device using the PMU module.

Example:

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

> You can also use the `AXP2101` module to configure the power management unit. The usage is similar to the `PMU` module, and you can refer to the example script [axp2101_example.py](https://github.com/sipeed/MaixPy/blob/main/examples/ext_dev/pmu/pmu_axp2101/axp2101_example.py) for guidance.

Initialize the `PMU` object, and call `get_bat_percent()` to get the current battery level. Call `set_bat_charging_cur()` to set the maximum charging current.

Calling `poweroff()` will immediately cut off power to the device. Please ensure that data in memory is synced to disk before using this function.

You can use the `set_vol()` and `get_vol()` methods to set and read the voltage of the `DC-DC` and `LDO` channels, respectively. Currently, the following channels of the `AXP2101` are supported for voltage configuration: `DCDC1~DCDC5`, `ALDO1~ALDO4`, and `BLDO1~BLDO2`.

>! Warning !!!
>Setting incorrect voltages may damage the `MaixCAM-Pro`. Do not modify the voltages of `DCDC2~DCDC5`, `ALDO1~ALDO4`, and `BLDO1~BLDO2` unless you fully understand the purpose and consequences of the adjustment. If you need to test, please use the `DCDC1` channel.

For detailed information on the PMU API, please refer to the [PMU API Documentation](../../../api/maix/ext_dev/pmu.md)