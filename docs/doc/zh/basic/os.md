---
title: MaixCAM MaixPy 升级和烧录系统
---

## 介绍

如果你购买了官方（Sipeed）的带 TF 卡的套餐，一般来说出厂已经烧录好了系统，可以跳过这一步直接使用。

但是为了防止出厂烧录的系统版本过旧，<span style="font-size: 1.2em; color: red">**强烈建议**</span> 先按照教程 **升级到最新** 的系统。

## 获得最新系统

在 [MaixPy 发布页面](https://github.com/sipeed/MaixPy/releases) 找到最新的系统镜像文件，比如`maixcam_os_20240401_maixpy_v4.1.0.xz`。
> 中国国内用户下载速度慢可以用迅雷下载，速度可能会快一些。
> 或者使用例如 [github.abskoop.workers.dev](https://github.abskoop.workers.dev/) 这种代理网站下载。

备用地址：[Sourceforge](https://sourceforge.net/projects/maixpy/files/) （同步可能不及时，建议优先上面的方式）


## 如何确认系统是否需要升级

* 在开机后的功能选择界面，点击`设置`，然后点击`设备信息`，可以看到系统的版本号。
* 到[MaixPy 发布历史页面](https://github.com/sipeed/MaixPy/releases)查看更新日志，里面有 MaixPy 固件和系统镜像的更新说明，如果在你的版本后有重要更新，建议升级。
> 如果最新系统和当前系统对比只是 MaixPy 固件的常规更新，也可以不升级，在 `设置` 中的 `更新 MaixPy` 中单独更新 `MaixPy`，不过一般 **不推荐** 这样做。




## 烧录系统到 MaixCAM

参考 硬件文档中的 [MaixCAM 系统烧录](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) 教程，注意里面能满足 `USB 烧录`的条件则推荐使用 `USB 烧录`方式，USB 烧录方式不用拔 TF 卡。

