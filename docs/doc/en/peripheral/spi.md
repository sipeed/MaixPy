---
title: Using SPI in MaixCAM MaixPy
update:
  - date: 2024-06-11
    author: iawak9lkm
    version: 1.0.0
    content: Initial document
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

![](https://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

You need to use `maix.peripheral.pinmap` to complete the pin mapping for SPI before use.

**Note: The MaixCAM's SPI can only be used as an SPI master device. MaixCAM's SPI does not support modifying the valid level of the hardware CS pins at this time. The active level of all SPI hardware CS is low. If you need to use other CS active levels, configure the software CS pins and their active levels in the SPI API. SPI4 is the software simulated SPI, the measured maximum rate is 1.25MHz, and the usage is the same as hardware SPI.**

Using SPI with MaixPy is easy:

```python
from maix import spi, pinmap

pin_function = {
    "A24": "SPI4_CS",
    "A23": "SPI4_MISO",
    "A25": "SPI4_MOSI",
    "A22": "SPI4_SCK"
}

for pin, func in pin_function.items():
    if 0 != pinmap.set_pin_function(pin, func):
        print(f"Failed: pin{pin}, func{func}")
        exit(-1)
        

spidev = spi.SPI(4, spi.Mode.MASTER, 1250000)

### Example of full parameter passing.
# spidev = spi.SPI(id=4,                  # SPI ID
#                  mode=spi.Mode.MASTER,  # SPI mode
#                  freq=1250000,          # SPI speed
#                  polarity=0,            # CPOL 0/1, default is 0
#                  phase=0,               # CPHA 0/1, default is 0
#                  bits=8,                # Bits of SPI, default is 8
#                  cs_enable=True,        # Use soft CS pin? True/False, default is False
#                  cs='GPIOA19')          # Soft cs pin number, default is 'GPIOA19'

b = bytes(range(0, 8))

res = spidev.write_read(b, len(b))
if res == b:
    print("loopback test succeed")
else:
    print("loopback test failed")
    print(f"send:{b}\nread:{res}")
```

You need to connect the `MOSI` and `MISO` of this SPI first.

Configure the required pins with `pinmap` and then enable full duplex communication, the return value will be equal to the sent value.


See the [SPI API documentation]((../../../api/maix/peripheral/spi.md)) for a more detailed description of the SPI API.
