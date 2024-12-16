---
title: MaixCAM MaixPy Using TOF Module OPNS303x for Ranging and Terrain Detection
---

## Introduction

OPNS303x is a 100x100 TOF module, suitable for ranging or terrain detection.

The current OPNS303x driver is compatible with OPNS3031 (the same model as MaixSense-A010).

By connecting an OPNS3031 to MaixCAM, you can obtain a distance data matrix by calling the `matrix()` method, which is suitable for applications requiring distance data. The `image()` method can directly get the pseudo-color image that MaixCAM can display, equivalent to `obj.image_from(obj.matrix())`. The `xxx_dis_point()` method can get the values and corresponding coordinates of the minimum, maximum, and center point distances in the most recent frame of data.

If you have a TOF requirement, please visit [Sipeed Store](https://wiki.sipeed.com/store.html) for inquiries and purchases.

## Usage

Example code is available at [MaixPy/examples/ext_dev/sensors/tof_opns303x/tof_opns303x_example.py](https://github.com/sipeed/MaixPy/tree/main/examples/ext_dev/sensors/tof_opns303x/tof_opns303x_example.py)
