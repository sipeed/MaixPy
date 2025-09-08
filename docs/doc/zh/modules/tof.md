---
titile: MaixCAM MaixPy 使用 TOF 模块测距和地形检测
---

## 效果演示

单 ToF 效果图:

![](../../assets/tof003.jpg)

ToF和可见光融合效果图:

![](../../assets/tof002.jpg)

该 APP 已集成到 MaixCAM Release 镜像中, 安装支持的模块, 启动 `ToF Camera` APP 即可

[APP 安装地址](https://maixhub.com/app/88)

[源码地址](https://github.com/sipeed/MaixCDK/tree/main/projects/app_tof_camera)

## 适配列表

* PMOD_TOF100

[咨询购买地址](https://wiki.sipeed.com/en/store.html)

### PMOD_TOF100

![](../../assets/tof004.jpg)

PMOD_TOF100 是一个 100x100 TOF 模块, 可用于测距或者地形检测, 模块参数:

|参数名称||
|-------|---|
|分辨率|100x100,50x50,25x25|
|测距范围|0.2~2.5m|
|视角|70°Hx60°V|
|激光发射器|940nm VCSEL|
|帧率|5~20fps|

安装 PMOD_TOF100 模块后, 可以使用 MaixPy 提供的 API 获得模块测得的距离数据矩阵、伪彩图、最近一帧数据中的最小最大以及中心距离的值和对应的坐标等信息, 详情见 [模块 API 文档](../../../api/maix/ext_dev/tof100.md)

您也可以参考我们的效果演示 APP 编写您的应用代码.

Sipeed 官方有另外[两款 TOF 模块](https://wiki.sipeed.com/hardware/zh/maixsense/index.html) 可以用来测距，可以购买使用串口通信使用。
