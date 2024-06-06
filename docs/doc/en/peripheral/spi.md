---
title: MaixPy ues SPI
update:
  - date: 2024-06-05
    author: sipeed
    version: 1.0.0
    content: First Edition Documentation
---

## SPI Introduction

SPI (Serial Peripheral Interface) is a synchronous peripheral interface that enables the SoC to communicate serially with various peripheral devices to exchange information. Common peripherals are Flash RAM, network controllers, LCD display drivers, and A/D converters.

SPI uses Master-Slave mode, which supports one or more Slave devices.

On a hardware circuit, SPI usually consists of 4 wires which are:

* `MISO`(Master Output Slave Input): This pin sends data in slave mode or receives data in master mode.
* `MOSI`(Master Input Slave Output): This pin sends data in master mode or receives data in slave mode.
* `SCK`: Serial bus clock, output by the master device and input by the slave device.
* `NSS/CS`:  Slave Device Selection. It acts as a chip select pin, allowing the master device to communicate with specific slave devices individually, avoiding conflicts on the bus.

In terms of communication protocols, SPI behavior is generally like this:

* SPI supports one master device and multiple slave devices. When the master device needs to communicate with a specific slave device, it selects the CS pin connected to that slave device to enable this transfer.This means that a slave device has only one CS pin for the master device to select itself, and the number of chip-select pins for the master device depends on how many slave devices are connected to its SPI bus.

* SPI has four modes, depending on the configuration of polarity (CPOL) and phase (CPHA).

  Polarity affects the level of the clock signal when the SPI bus is idle.

  1. CPOL = 1, it indicates a high level at idle.
  2. CPOL = 0, it indicates a low level at idle.

  The phase determines the edge at which the SPI bus acquires data. There are two types of edges, rising edge and falling edge.

  1. CPHA = 0, it indicates that sampling starts from the first edge.
  2. CPHA = 1, it indicates that sampling starts from the second edge.

  Polarity and phase are combined to form the four modes of SPI:

  | Mode | CPOL | CPHA |
  | ---- | ---- | ---- |
  | 0    | 0    | 0    |
  | 1    | 0    | 1    |
  | 2    | 1    | 0    |
  | 3    | 1    | 1    |

* SPI typically supports both full-duplex transmission and half-duplex transmission.

* SPI does not specify a maximum transmission rate, it does not have an address scheme; SPI does not specify a communication response mechanism, it does not specify flow control rules.

## Using SPI in MaixPy

This is the pinout of MaixCAM.

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

You need to use `maix.peripheral.pinmap` to complete the pin mapping for SPI before use.

**Note: The MaixCAM's SPI can only be used as an SPI master device.**

**MaixCAM's SPI1 is a software SPI, its device node is `/dev/spidev4.0`, in practice you only need to pass 1 at the parameter `id` to use it, and CDK will automatically complete the mapping relationship.**

Using SPI with MaixPy is easy:

```python
from maix.peripheral import spi, pinmap

pinmap.set_pin_function("A24", "SPI1_CS")
pinmap.set_pin_function("A23", "SPI1_MISO")
pinmap.set_pin_function("A25", "SPI1_MOSI")
pinmap.set_pin_function("A22", "SPI1_SCK")

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

Before executing the code, you need to connect the MOSI and MISO of the corresponding SPI peripheral in the code. The example uses the full-duplex transfer API `spi.write_read()` and the data received by the SPI will be equal to the data sent.

See the [SPI API documentation]((../../../api/maix/peripheral/spi.md)) for a more detailed description of the SPI API.
