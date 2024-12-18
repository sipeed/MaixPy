---
title: MaixCAM MaixPy 读取热成像传感器mlx90640
---

## 简介

MLX90640 是工业标准并经过完全校准的 32*24 像素热红外阵列传感器.

通过给 MaixCAM 外挂一个热成像传感器mlx90640, 调用 `matrix()` 方法可以获得 32x24 的温度数据矩阵(list[24][32]), 适用于需要温度数据的应用场景. 调用 `image()` 方法可以直接获取 MaixCAM 能显示的伪彩色图像, 相当于 `obj.image_from(obj.matrix())`. 调用 `xxx_temp_point()` 方法可以获得最近一帧数据中的最小最大以及中心温度的值和对应的坐标.

如果您有该需求, 欢迎您访问 [Sipeed Store](https://wiki.sipeed.com/store.html) 咨询购买.

## 使用

示例代码在[MaixPy/examples/ext_dev/sensors/thermography_mlx90640/mlx90640_example.py](https://github.com/sipeed/MaixPy/tree/main/examples/ext_dev/sensors/thermography_mlx90640/mlx90640_example.py)


