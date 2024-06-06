---
title: MaixPy SPI 串行外设接口使用介绍
update:
  - date: 2024-06-05
    author: sipeed
    version: 1.0.0
    content: 初版文档
---

## SPI 简介

SPI (Serial Peripheral Interface，即串行外设接口)，是一种同步外设接口，它可以使 SoC 与各种外围设备以串行方式进行通信以交换信息。常见的外围设备有 Flash RAM、网络控制器、LCD显示驱动器和A/D转换器等。

SPI 采用主从模式(Master—Slave)架构，支持一个或多个Slave设备。

在硬件电路上，SPI 通常由 4 根线组成，它们分别是：

* `MISO`：即主设备输入从设备输出（Master Output Slave Input），该引脚在从模式下发送数据，在主模式下接收数据。
* `MOSI`：即主设备输出从设备输入（Master Input Slave Output），该引脚在主模式下发送数据，在从模式下接收数据。
* `SCK`：串行总线时钟，由主设备输出，从设备输入。
* `NSS`/`CS`：从设备选择。它作为片选引脚，让主设备可以单独地与特定从设备通信，避免数据线上的冲突。

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

## MaixPy 中使用 SPI

MaixCAM 的引脚分布如下：

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

使用前需要 `maix.peripheral.pinmap` 完成对 SPI 的管脚映射。

**注意：MaixCAM 由于其 SPI 外设的限制，只能作为 SPI 主设备使用。**

**左侧 SPI1 为软件 SPI，实际的设备节点为 `/dev/spi4.0`，在使用 MaixCDK/MaixPy SPI API 时只需传入编号1即可使用该软件 SPI**

通过 MaixPy 使用 SPI 很简单：

```python
from maix.peripheral import spi

### Note: The IO corresponding to SPI2 is multiplexed as SDIO by default, the SDIO interface is connected to the WIFI device, if it is multiplexed as SPI2, it will lead to WIFI unavailability.
### 注意：SPI2 对应的 IO 默认被复用作 SDIO，该 SDIO 接口连接着 WIFI 设备，如果复用为 SPI2，会导致 WIFI 不可用。
# s = spi.SPI(2, spi.Mode.MASTER, 400000)

s = spi.SPI(1, spi.Mode.MASTER, 400000)
v = list(range(0, 32))

r = s.write_read(v, len(v))
if r != []:
    print(f"spi read {len(r)} bytes")
    print(f"read:{r}")
if r == v:
    print("The loopback test was successful.")
else:
    print("The loopback test failed")
```

将对应的 SPI 设备的 MOSI 引脚和 MISO 引脚接在一起，使用全双工通信，接收的数据将会等于发送的数据。先写后读没有以上现象。

更多 SPI API 的详细说明请看 [SPI API 文档](../../../api/maix/peripheral/spi.md)



