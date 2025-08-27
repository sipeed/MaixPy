---
title: MaixCAM MaixPy Using I2C
update:
  - date: 2025-08-08
    author: Neucrack
    version: 1.1.0
    content: Refactored the documentation to be more understandable for beginners
---

## Prerequisites

Please learn how to use the [pinmap](https://www.google.com/search?q=./pinmap.md) module to set pin functions first.

To enable an pin for `I2C` functionality, first use `pinmap` to set the function of the corresponding pin to `I2C`.

## I2C Introduction

`I2C` uses only two pins, `SCL` and `SDA`, to achieve bus communication. This allows one master to connect to multiple slaves, enabling convenient one-to-many communication.
It is commonly used for:

  * Reading sensor data, such as temperature and humidity, IMU, and touchscreens.
  * Controlling devices, such as setting camera parameters.
  * Communication between two devices.

There are many good tutorials on the basics of I2C online. This article will not go into detail; please search and learn on your own.

## Choosing the Right I2C to Use

First, we need to know which pins and I2C interfaces the device has, as shown in the figure:

| Device Model | Pinout Diagram | Pin Multiplexing Description |
| ------- | ------- | --- |
| MaixCAM |  | The silkscreen on the board, e.g., `A15`, is the pin name, and `I2C5_SCL` is the function name |
| MaixCAM-Pro |  | The first name, e.g., `A15`, is the pin name, and `I2C5_SCL` is the corresponding function name |
| MaixCAM2 |  | The first name, e.g., `A1`, is the pin name, and `I2C6_SCL` is the corresponding function name  |

It's important to note that pins might have other default uses. It's best to avoid these pins. Please refer to the [pinmap](https://www.google.com/search?q=./pinmap.md) documentation for details.

For example:
  * For `MaixCAM / MaixCAM-Pro`, the `I2C1` and `I2C3` pins overlap with the WiFi module (SDIO1), so their use is not recommended. There is also an `I2C5`, which is a software-simulated driver at the low level. It is recommended to use it as the underlying driver has been configured, and it works the same as a hardware `I2C`.
  * The `I2C6 / I2C7` pins on `MaixCAM2` are idle and can be used once `pinmap` is configured.

## Using I2C in MaixPy

First, use `pinmap` to set the pin function to `I2C`, then initialize the `I2C` object:

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

## More Examples

See [MaixPy examples](https://github.com/sipeed/MaixPy/tree/main/examples/peripheral/i2c).

## API Documentation

For more API information, see [i2c API documentation](https://wiki.sipeed.com/maixpy/api/maix/peripheral/i2c.html).

## Using Other Libraries

Additionally, since it is a standard Linux driver, besides using the APIs provided by MaixPy, you can also use general Linux libraries like `smbus / smbus2`.

Steps to use:

  * Run `pip install smbus` in the development board's terminal to install the library.
  * Use `pinmap` to map the pin functions.
  * Call `smbus` APIs to read from and write to `i2c`.


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
