---
title: Reading Temperature and Humidity Sensors with MaixCAM MaixPy
---

## Introduction

By attaching a temperature and humidity sensor module to the MaixCAM, you can easily measure the environmental temperature and humidity. Here, we use the `Si7021` sensor as an example, which can be driven using `I2C`. For other sensors, you can request drivers from the manufacturer and use `I2C` or `SPI` to read data from them.

![](../../assets/si7021.png)

**Note**: The power supply should be 3.3V. Connecting it to 5V may cause damage.

Connect the `SCL` / `SDA` pins of the sensor to the corresponding `SCL` / `SDA` pins on the MaixCAM. For instance, on `I2C5`, this corresponds to `A15(SCL)` / `A27(SDA)`.

## Usage

The complete code can be found in the [MaixPy/examples/ext_dev/sensors](https://github.com/sipeed/MaixPy/blob/main/examples/ext_dev/sensors) directory. Look for the `si7021` example.

**Note**: The system image version must be `>= 2024.6.3_maixpy_v4.2.1`.

