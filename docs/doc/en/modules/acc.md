---
title: Reading the Accelerometer and Attitude Calculation with MaixCAM MaixPy
---

## Introduction to IMU

For the MaixCAM-Pro, it has an onboard QMI8658 chip that integrates a three-axis gyroscope and a three-axis accelerometer. This chip can provide high-precision data on attitude, motion, and position, making it suitable for various applications that require accurate motion detection, such as drones, robots, game controllers, and virtual reality devices. The QMI8658 features low power consumption, high stability, and high sensitivity. Below is an introduction to using the IMU module to obtain attitude data.

> MaixCAM does not have an onboard accelerometer, but you can connect one externally using an IIC driver.


## Using IMU in MaixPy

Example:

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

Initialize the IMU object according to your needs, and then call `read()` to get the raw data read from the IMU.

**If the `mode` parameter is set to `DUAL`, the data returned by `read()` will be `[acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, temp]`. If `mode` is set to only one of ACC or GYRO, it will return only the corresponding `[x, y, z, temp]`. For example, if ACC is selected, `read()` will return `[acc_x, acc_y, acc_z, temp]`.**

For detailed information on the BM8653 API, please refer to the [BM8653 API Documentation](../../../api/maix/ext_dev/imu.md)

