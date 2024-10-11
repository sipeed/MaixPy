---
title: MaixCAM MaixPy 读取加速度计和姿态解算
---


## IMU 简介

对于 MaixCAM-Pro，板载了一款集成了三轴陀螺仪和三轴加速度计的QMI8658芯片, 它能够提供高精度的姿态、运动和位置数据，适用于各种需要精确运动检测的应用场景，如无人机、机器人、游戏控制器和虚拟现实设备等。QMI8658具有低功耗、高稳定性和高灵敏度的特点, 下面将介绍使用IMU模块来获取姿态数据。
> MaixCAM 无板载加速度计，可自行外接使用 iic 驱动。

## MaixPy 中使用 IMU

Using IMU module to read data from the QMI8658.

示例代码:

```python
from maix.ext_dev import imu

i = imu.IMU("qmi8658", mode=imu.Mode.DUAL,
                              acc_scale=imu.AccScale.ACC_SCALE_2G,
                              acc_odr=imu.AccOdr.ACC_ODR_8000,
                              gyro_scale=imu.GyroScale.GYRO_SCALE_16DPS,
                              gyro_odr=imu.GyroOdr.GYRO_ODR_8000)

while True:
    data = i.read()
    print("\n-------------------")
    print(f"acc x: {data[0]}")
    print(f"acc y: {data[1]}")
    print(f"acc z: {data[2]}")
    print(f"gyro x: {data[3]}")
    print(f"gyro y: {data[4]}")
    print(f"gyro z: {data[5]}")
    print(f"temp: {data[6]}")
    print("-------------------\n")
```

按照您的需求初始化 IMU 对象, 然后调用 `read()` 即可. `read()` 返回的是从 IMU 中读出的原始数据.

**如果 `mode` 参数选择 `DUAL`, 则 `read()`返回的数据为 `[acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temp]`, 如果 `mode` 只选择 ACC/GYRO 中的一个, 只会返回对应的 `[x, y, z, temp]`, 例如选择 ACC, `read()` 会返回 `[acc_x, acc_y, acc_z, temp]`.**

有关 IMU API 的详细说明请看 [IMU API 文档](../../../api/maix/ext_dev/imu.md)
