---
title: Using TOF Modules for Distance Measurement and Terrain Detection with MaixCAM and MaixPy
---

## Demo

Single ToF effect:

![](../../assets/tof003.jpg)

ToF and visible light fusion effect:

![](../../assets/tof002.jpg)

This APP has been integrated into the MaixCAM Release image. Install the supported module and launch the `ToF Camera` APP to use it.

[APP Installation Link](https://maixhub.com/app/88)

[Source Code Link](https://github.com/sipeed/MaixCDK/tree/main/projects/app_tof_camera)

## Supported List

* PMOD_TOF100

[Purchase Inquiry Link](https://wiki.sipeed.com/en/store.html)

### PMOD_TOF100

![](../../assets/tof004.jpg)

PMOD_TOF100 is a 100x100 TOF module that can be used for distance measurement or terrain detection. Module parameters:

| Parameter Name | Value |
|----------------|-------|
| Resolution     | 100x100, 50x50, 25x25 |
| Range          | 0.2~2.5m |
| Field of View  | 70°H x 60°V |
| Laser Emitter  | 940nm VCSEL |
| Frame Rate     | 5~20fps |

After installing the PMOD_TOF100 module, you can use the API provided by MaixPy to obtain the distance data matrix, pseudo-color images, and the minimum, maximum, and center distance values and their corresponding coordinates from the latest frame data. For details, see [Module API Documentation](../../../api/maix/ext_dev/tof100.md).

You can also refer to our demo APP to write your application code.

Sipeed offers two additional [TOF modules](https://wiki.sipeed.com/hardware/zh/maixsense/index.html) for distance measurement, which can be purchased and used with serial communication.
