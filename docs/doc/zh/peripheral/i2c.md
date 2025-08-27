---
title: MaixCAM MaixPy 使用 I2C
update:
  - date: 2025-08-08
    author: Neucrack
    version: 1.1.0
    content: 重构文档，更以于初学者理解
---

## 前置知识

请先学会使用[pinmap](./pinmap.md) 模块设置引脚功能。

要让一个引脚能使用 `I2C` 功能，先用`pinmap`设置对应引脚功能为`I2C`。


## I2C 简介

`I2C` 使用两个引脚`SCL` `SDA` 即可实现总线通信，即一个主机可以挂多个从机，实现一对多通信，十分方便。
常用来：
* 读取传感器数据，比如温湿度、IMU、触摸屏。
* 控制设备，比如设置摄像头参数。
* 两个设备通信。

关于 I2C 基础知识，网上有很多好教程，本文不展开讲解，请自行搜索学习。


## 选择合适的 I2C 使用

首先我们需要知道设备有哪些引脚和 I2C，如图：

| 设备型号 | 引脚简图 | 引脚复用说明 |
| ------- | ------- | --- |
| MaixCAM | ![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg) | 板子丝印比如`A15`是引脚名，`I2C5_SCL`是功能名 |
| MaixCAM-Pro | ![maixcam_pro_io](/static/image/maixcam_pro_io.png) | 第一个名如`A15`是引脚名，对应`I2C5_SCL`是功能名 |
| MaixCAM2 | ![maixcam2_io](/static/image/maixcam2_io.png) | 第一个名如`A1`是引脚名，对应`I2C6_SCL`是功能名  |

需要注意的是，引脚默认可能用做其它用途，最好避开这些引脚，请看[pinmap](./pinmap.md) 文档中的说明。

比如：
* 对于`MaixCAM / MaixCAM-Pro`, 引出的 `I2C1` `I2C3` 引脚和 WiFi 模块（SDIO1）重合了，所以不建议使用了，另外还有一个`I2C5`，是底层驱动软件模拟的，建议使用它，底层已经做好了驱动，使用时和使用硬件`I2C`一样。
* `MaixCAM2`引出的`I2C6 / I2C7`则是空闲的，设置了 `pinmap` 就能使用。

## MaixPy 中使用 I2C

先用`pinmap`设置引脚功能为`I2C`，然后初始化`I2C`对象即可：


```python
from maix import i2c, pinmap, sys, err


# get pin and i2c number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    scl_pin_name = "A1"
    scl_i2c_name = "I2C6_SCL"
    sda_pin_name = "A0"
    sda_i2c_name = "I2C6_SDA"
    i2c_id = 6
else:
    scl_pin_name = "A15"
    scl_i2c_name = "I2C5_SCL"
    sda_pin_name = "A27"
    sda_i2c_name = "I2C5_SDA"
    i2c_id = 5

# set pinmap
err.check_raise(pinmap.set_pin_function(scl_pin_name, scl_i2c_name), "set pin failed")
err.check_raise(pinmap.set_pin_function(sda_pin_name, sda_i2c_name), "set pin failed")

bus = i2c.I2C(i2c_id, i2c.Mode.MASTER)
slaves = bus.scan()
print("find slaves:")
for s in slaves:
    print(f"{s}[0x{s:02x}]")

```

## 更多例程

看[MaixPy examples](https://github.com/sipeed/MaixPy/tree/main/examples/peripheral/i2c)。


## API 文档

更多 API 看 [i2c API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html)

## 使用其它库

另外，由于是 Linux 标准驱动，除了使用 MaixPy 提供的 API，你也可以使用 Linux 通用库，比如`smbus / smbus2`。

使用步骤：
* 在开发板终端执行`pip install smbus` 安装库。
* 使用`pinmap` 映射引脚功能。
* 调用`smbus` API 对 `i2c` 进行读写。

```python
from maix import i2c, pinmap, sys, err
import smbus

# get pin and i2c number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    scl_pin_name = "A1"
    scl_i2c_name = "I2C6_SCL"
    sda_pin_name = "A0"
    sda_i2c_name = "I2C6_SDA"
    i2c_id = 6
else:
    scl_pin_name = "A15"
    scl_i2c_name = "I2C5_SCL"
    sda_pin_name = "A27"
    sda_i2c_name = "I2C5_SDA"
    i2c_id = 5

# set pinmap
err.check_raise(pinmap.set_pin_function(scl_pin_name, scl_i2c_name), "set pin failed")
err.check_raise(pinmap.set_pin_function(sda_pin_name, sda_i2c_name), "set pin failed")


bus = smbus.SMBus(i2c_id)
```

