---
title: MaixCAM MaixPy Reading Thermography Sensor mlx90640
---

## Introduction

MLX90640 is an industrial standard and fully calibrated 32*24 pixel thermal infrared array sensor.

By attaching a thermography sensor mlx90640 to MaixCAM, you can obtain a 32x24 temperature data matrix (list[24][32]) by calling the `matrix()` method, which is suitable for applications requiring temperature data. The `image()` method can directly get the pseudo-color image that MaixCAM can display, equivalent to `obj.image_from(obj.matrix())`. The `xxx_temp_point()` method can get the values and corresponding coordinates of the minimum, maximum, and center temperatures in the most recent frame of data.

If you have this requirement, please visit [Sipeed Store](https://wiki.sipeed.com/store.html) for inquiries and purchases.

## Usage

Example code is available at [MaixPy/examples/ext_dev/sensors/thermography_mlx90640/mlx90640_example.py](https://github.com/sipeed/MaixPy/tree/main/examples/ext_dev/sensors/thermography_mlx90640/mlx90640_example.py)
