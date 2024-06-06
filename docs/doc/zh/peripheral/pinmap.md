---
title: MaixPy Pinmap 管脚映射使用介绍
update:
  - date: 2024-06-05
    author: sipeed
    version: 1.0.0
    content: 初版文档
---

## 管脚映射简介

在系统级芯片（System on Chip, SoC）设计中，一个管脚通常具有多个功能，这种设计方法被称为引脚复用。其原因主要有以下几个方面：

* 节省引脚数量：SoC 集成了大量的功能模块，如 CPU、GPU、内存控制器、I/O 接口、通信模块等。如果每个功能都分配独立的引脚，会导致需要的引脚数量非常庞大，增加封装的复杂性和成本。通过引脚复用，一个引脚可以在不同的模式下支持不同的功能，从而显著减少引脚的总数。
* 降低芯片封装和制造成本：减少引脚数量可以选择更小的封装尺寸，从而降低封装和制造成本。小封装不仅降低了材料成本，还减少了芯片在电路板上的占用空间，有利于设计更紧凑的电子产品。
* 提高设计灵活性：引脚复用提供了更大的设计灵活性。不同的应用场景可能需要不同的功能组合，通过软件配置可以根据具体需求启用不同的引脚功能。例如，同一个引脚在一个实际应用中可以作为 UART 通信接口，而在另一个实际应用中可以作为 SPI 总线接口。
* 简化 PCB 布局：减少引脚数量可以简化印刷电路板（PCB）的布局设计。更少的引脚意味着更少的布线层数和过孔，从而简化了 PCB 设计，降低了生产难度和成本。
* 优化性能：在某些情况下，通过复用引脚可以优化信号路径和性能。例如，通过选择适当的引脚功能组合，可以减少信号传输路径上的干扰和噪声，提高系统的整体性能和可靠性。

而 Pinmap 展示和管理芯片各个引脚配置，这些配置通常包括每个引脚的名称及其功能（通常有多个功能）。

以 MaixCAM GPIO A28为例子：
 * `A28` 为引脚名称。
 * `GPIOA28`/`UART2_TX`/`JTAG_TDI` 为引脚功能（可从 SoC 手册查询），同一时间该引脚只能是这三个功能中的其中一个。

通过 Pinmap，可以设定指定的芯片引脚为指定的功能。

## MaixPy 中使用Pinmap

对于 MaixCAM 板子上各个引脚的编号及其功能，可以参考下图：
![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

或是阅读 [SG2002芯片手册](https://cn.dl.sipeed.com/fileList/LICHEE/LicheeRV_Nano/07_Datasheet/SG2002_Preliminary_Datasheet_V1.0-alpha_CN.pdf) Pinmux 章节了解剩余的引脚的编号及功能。

介绍了那么多，其实通过 MaixPy 使用 Pinmap 来管理引脚功能很简单：

```python
from maix.peripheral import pinmap

print(pinmap.get_pins())

f = pinmap.get_pin_functions("A28")
print(f"GPIO A28 pin functions:{f}")

print(f"Set GPIO A28 to {f[0]} function")
pinmap.set_pin_function("A28", f[0])
```

先列出了可供管脚映射的所有引脚，然后查询 `GPIO A28` 可供选择的引脚功能，最后将该引脚设置为该引脚的第一个功能(作为GPIO)。

更详细的 Pinmap 的 API 说明请看 [Pinmap API 文档](../../../api/maix/peripheral/pinmap.md)

