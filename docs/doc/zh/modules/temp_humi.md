---
title: MaixCAM MaixPy 读取温湿度传感器
---

## 简介

通过给 MaixCAM 外挂一个温湿度传感器模块，可以轻松读取到环境温度和湿度，这里以 `Si7021` 这款传感器为例，通过 `I2C` 可以驱动它。

## 使用

完整的代码在[MaixPy/examples/sensors/temp_humi_si7021.py](https://github.com/sipeed/MaixPy/blob/main/examples/sensors/temp_humi_si7021.py)

注意系统镜像需要 `>= 2024.6.3_maixpy_v4.2.1` 版本。

