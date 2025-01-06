---
title: MaixCAM MaixPy 使用热红外图像传感器
---

## 效果演示

单热成像效果图:

![](../../assets/thermal002.jpg)

热成像和可见光融合效果图 (左侧为冷饮,右侧为工作中的小主机):

![](../../assets/thermal001.png)

该 APP 已集成到 MaixCAM Release 镜像中, 安装支持的模块, 启动 `Thermal Camera` APP 即可

[APP 安装地址](https://maixhub.com/app/87)

[源码地址](https://github.com/sipeed/MaixCDK/tree/main/projects/app_thermal_camera)


## 适配列表

* PMOD_Thermal32

[咨询购买地址](https://wiki.sipeed.com/en/store.html)

### PMOD_Thermal32

![](../../assets/thermal003.jpg)

PMOD_Thermal32 是工业标准并经过完全校准的 32*24 像素热红外阵列传感器, 模块参数:

|参数名称||
|-------|---|
|分辨率|32x24|
|测温范围|-40～450℃|
|帧率|1~30fps|
|接口|I2C|

安装 PMOD_Thermal32 模块后, 可以使用 MaixPy 提供的 API 获得模块测得的温度数据矩阵、伪彩图、最近一帧数据中的最小最大以及中心温度的值和对应的坐标等信息, 详情见 [模块 API 文档](../../../api/maix/ext_dev/mlx90640.md)

您也可以参考我们的效果演示 APP 编写您的应用代码.



