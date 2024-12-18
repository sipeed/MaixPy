---
title: MaixCAM MaixPy 使用 TOF 模块 OPNS303x 测距和地形检测
---

## 简介

OPNS303x 是炬佑推出的 100x100 TOF 模块, 可用于测距或者地形检测.

本 OPNS303x 驱动目前适配了 OPNS3031(MaixSense-A010同款).

通过给 MaixCAM 外接一个 OPNS3031, 调用 `matrix()` 方法可以获得距离数据矩阵, 适用于需要距离数据的应用场景. 调用 `image()` 方法可以直接获取 MaixCAM 能显示的伪彩色图像, 相当于 `obj.image_from(obj.matrix())`. 调用 `xxx_dis_point()` 方法可以获得最近一帧数据中的最小最大以及中心点距离的值和对应的坐标.

如果您有 TOF 需求, 欢迎您访问 [Sipeed Store](https://wiki.sipeed.com/store.html) 咨询购买.

## 使用

示例代码在[MaixPy/examples/ext_dev/sensors/tof_opns303x/tof_opns303x_example.py](https://github.com/sipeed/MaixPy/tree/main/examples/ext_dev/sensors/tof_opns303x/tof_opns303x_example.py)


