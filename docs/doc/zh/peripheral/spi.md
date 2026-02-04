---
title: MaixCAM MaixPy SPI 串行外设接口使用介绍
update:
  - date: 2024-06-11
    author: iawak9lkm
    version: 1.0.0
    content: 初版文档
  - date: 2025-08-08
    author: Neucrack
    version: 1.1.0
    content: 重构文档，更以于初学者理解
---

## 前置知识

请先学会使用[pinmap](./pinmap.md) 模块设置引脚功能。

要让一个引脚能使用 `SPI` 功能，先用`pinmap`设置对应引脚功能为`SPI`。


## SPI 简介

前面介绍了 `I2C`，通过两根线就能实现总线一对多通信，但是有局限，比如通信速度比较低（一般`200k/400k`）， `SPI` (Serial Peripheral Interface，即串行外设接口) 也是一种一对多总线通信方式，速度更快，但是需要 `4`根线通信：
* `MISO`：即主设备输入从设备输出（Master Output Slave Input），该引脚在从模式下发送数据，在主模式下接收数据。
* `MOSI`：即主设备输出从设备输入（Master Input Slave Output），该引脚在主模式下发送数据，在从模式下接收数据。
* `SCK`：串行总线时钟，由主设备输出，从设备输入。
* `NSS`/`CS`：从设备选择。它作为片选引脚，让主设备可以单独地与特定从设备通信，避免数据线上的冲突。

常用在：
* 读写 Flash。
* 两个设备通信。
* 通信方式转换，比如 SPI 转以太网。
* LCD显示驱动器。
* 输出特定方波，比如 WS2812 灯，除了用 GPIO 控制， 用 SPI 输出的数据是方波的特性，也能输出特定方波信号。

在通信协议上，SPI 行为一般如下：

* SPI 支持一主多从，主设备通过片选引脚来选择需要进行通信的从设备，一般情况下，从设备 SPI 接口只需一根片选引脚，而主设备的片选引脚数量等同于设备数量。主设备使能某个从设备的片选信号期间，该从设备会响应主设备的所有请求，其余从设备会忽略总线上的所有数据。

* SPI 有四种模式，取决于极性（CPOL）和相位（CPHA）的配置。

  极性，影响 SPI 总线空闲时的时钟信号电平。

  1. CPOL = 1：表示空闲时是高电平
  2. CPOL = 0：表示空闲时是低电平

  相位，决定 SPI 总线采集数据的跳变沿。

  1. CPHA = 0：表示从第一个跳变沿开始采样
  2. CPHA = 1：表示从第二个跳变沿开始采样

  极性与相位组合成了 SPI 的四种模式：

| Mode | CPOL | CPHA |
| ---- | ---- | ---- |
| 0    | 0    | 0    |
| 1    | 0    | 1    |
| 2    | 1    | 0    |
| 3    | 1    | 1    |

* SPI 通常支持全双工和半双工通信。

* SPI 不规定最大传输速率，没有地址方案；SPI 也没规定通信应答机制，没有规定流控制规则。

SPI 是非常常见的通信接口，通过 SPI 接口，SoC 能控制各式各样的的外围设备。

## 选择合适的 SPI 使用

首先我们需要知道设备有哪些引脚和 SPI，如图：

| 设备型号 | 引脚简图 | 引脚复用说明 |
| ------- | ------- | --- |
| MaixCAM | ![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg) | 板子丝印比如`A24`是引脚名，`SPI4_CS`是功能名 |
| MaixCAM-Pro | ![maixcam_pro_io](/static/image/maixcam_pro_io.png) | 第一个名如`A24`是引脚名，对应`SPI4_CS`是功能名 |
| MaixCAM2 | ![maixcam2_io](https://wiki.sipeed.com/hardware/assets/maixcam/maixcam2_pins.jpg) | 第一个名如`B21`是引脚名，对应`SPI2_CS1`是功能名  |

需要注意的是，引脚默认可能用做其它用途，最好避开这些引脚，请看[pinmap](./pinmap.md) 文档中的说明。

比如：
* `MaixCAM/MaixCAM-Pro`: 由于其 SPI 外设的限制，只能作为 SPI 主设备使用,MaixCAM 的 SPI 暂时不支持修改硬件 CS 引脚有效电平，所有 SPI 硬件 CS 的有效电平为低电平。如需要使用其他的 CS 有效电平，请在 SPI API 中配置软件 CS 引脚及其有效电平。SPI4 为软件模拟的 SPI，实测最大速率为 1.25MHz，使用方法与硬件 SPI 无异。
* `MaixCAM2`: 默认有 2 个硬件 SPI 引脚，SPI2 默认功能就是 SPI, SPI1 的引脚需要先设置引脚复用，具体看`pinmap`。

## MaixPy 中使用 SPI


通过 MaixPy 使用 SPI，先设置好 `pinmap`，构造`SPI`对象通信即可。

这里一个例子，先连接该 SPI 的 `MOSI` 和 `MISO`，自己全双工收发：

```python
from maix import spi, pinmap, sys, err

# get pin and SPI number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_function = {
        "B21": "SPI2_CS1",
        "B19": "SPI2_MISO",
        "B18": "SPI2_MOSI",
        "B20": "SPI2_SCK"
    }
    spi_id = 2
else:
    pin_function = {
        "A24": "SPI4_CS",
        "A23": "SPI4_MISO",
        "A25": "SPI4_MOSI",
        "A22": "SPI4_SCK"
    }
    spi_id = 4

for pin, func in pin_function.items():
    err.check_raise(pinmap.set_pin_function(pin, func), f"Failed set pin{pin} function to {func}")


spidev = spi.SPI(spi_id, spi.Mode.MASTER, 1250000)

### Example of full parameter passing, fully documention see API documentation.
# spidev = spi.SPI(id=4,                  # SPI ID
#                  mode=spi.Mode.MASTER,  # SPI mode
#                  freq=1250000,          # SPI speed
#                  polarity=0,            # CPOL 0/1, default is 0
#                  phase=0,               # CPHA 0/1, default is 0
#                  bits=8,                # Bits of SPI, default is 8
#                  hw_cs=-1,              # use default hardware cs.
#                  soft_cs="",            # If you want use soft cs, set GPIO name,
#                                         # e.g.  GPIOA19(MaixCAM), GPIOA2(MaixCAM2)
#                                         # you should set pinmap first by yourself.
#                  cs_active_low=true     # cs pin active low voltage level


b = bytes(range(0, 8))

res = spidev.write_read(b, len(b))
if res == b:
    print("loopback test succeed")
else:
    print("loopback test failed")
    print(f"send:{b}\nread:{res}")
```

## 更多例程

看[MaixPy examples](https://github.com/sipeed/MaixPy/tree/main/examples/peripheral/spi)。


## API 文档

更多 API 看 [SPI API 文档](https://wiki.sipeed.com/maixpy/api/maix/peripheral/spi.html)





