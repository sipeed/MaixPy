---
title: Using PINMAP in MaixCAM MaixPy
update:
  - date: 2024-06-11
    author: iawak9lkm
    version: 1.0.0
    content: Initial document
---

## Pinmap Introduction

In System on Chip (SoC) design, a pin usually has more than one function, and this design method is called pin multiplexing. There are several main reasons for this:

* It saves the number of SoC pins. 

  SoCs integrate a large number of functional modules, such as CPUs, GPUs, memory controllers, I/O interfaces, communication modules, and so on. Assigning separate pins for each function would result in a very large number of pins being required, increasing the complexity and cost of the package. Through pin multiplexing, one pin can support different functions in different modes, thus significantly reducing the total number of pins.

* It reduces the cost of chip packaging and manufacturing. 

  Designers can choose smaller package sizes by reducing the number of pins, thus reducing packaging and manufacturing costs. Smaller packages not only reduce material costs, but also reduce the amount of space the chip takes up on the board, facilitating the design of more compact electronic products.

* It improves design flexibility. 

  Pin-multiplexing provides greater design flexibility. Different combinations of pin functions may be required in different application scenarios, and different pin functions can be enabled according to specific needs through software configuration. For example, the same pin can be used as a UART interface in one practical application and an SPI bus interface in another.

* It simplifies the PCB layout. 

  Reducing the number of pins simplifies the layout design of a printed circuit board (PCB). Fewer pins mean fewer wiring layers and vias, which simplifies PCB design and reduces manufacturing challenges and costs.

* Optimize performance. 

  In some cases, signal paths and performance can be optimized by multiplexing pins. For example, by selecting the proper combination of pin functions, interference and noise in the signal transmission path can be reduced, improving the overall performance and reliability of the system.

Pinmap displays and manages the individual pin configurations of the chip, which typically include the name of each pin and its function (usually multiple functions).

We use the MaixCAM GPIO A28 as an example.

* `A28` is the pin name.
* `GPIOA28`/`UART2_TX`/`JTAG_TDI` are the functions supported by this pin as listed in the Soc manual, and the function of this pin at the same time can only be one of these three functions.

With Pinmap, we can set the specified chip pin for the specified function.

## Using Pinmap in MaixPy

The following diagram lists the pin numbers and their functions on the MaixCAM board.

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

Or read the [SG2002 Chip Manual](https://cn.dl.sipeed.com/fileList/LICHEE/LicheeRV_Nano/07_Datasheet/SG2002_Preliminary_Datasheet_V1.0-alpha_CN.pdf) Pinmux section for the remaining pin numbers and functions.

It's actually quite easy to use Pinmap to manage pin functions through MaixPy.

```python
from maix.peripheral import pinmap

print(pinmap.get_pins())

f = pinmap.get_pin_functions("A28")
print(f"GPIO A28 pin functions:{f}")

print(f"Set GPIO A28 to {f[0]} function")
pinmap.set_pin_function("A28", f[0])
```

In the example, we start by listing all the pins available for management. Then we query `GPIO A28` for all the functions available. Finally the function of the pin is set to the first function listed (GPIO).

For a more detailed description of the Pinmap API, see the [Pinmap API documentation](../../../api/maix/peripheral/pinmap.md).