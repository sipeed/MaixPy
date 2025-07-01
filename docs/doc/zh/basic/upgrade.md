---
title: MaixCAM MaixPy 升级和烧录系统
---

## 系统和 MaixPy 介绍

首先需要区分一下  `系统` 和 `MaixPy`:
* **系统**： 运行所有软件的基础，包含了操作系统和驱动等，所有软件运行的基石。
* **MaixPy**: 软件包，依赖系统的驱动运行。

## 获得最新系统

在 [MaixPy 发布页面](https://github.com/sipeed/MaixPy/releases) 找到最新的系统镜像文件，比如:
* `maixcam_os_20240401_maixpy_v4.1.0.xz`: MaixCAM 系统镜像，包含了 MaixPy v4.1.0。
* `maixcam-pro_os_20240401_maixpy_v4.1.0.xz`： MaixCAM Pro 系统镜像，包含了 MaixPy v4.1.0。
* `maixcam2_os_20250801_maixpy_v4.11.0.xz`： MaixCAM2 系统镜像，包含了 MaixPy v4.11.0。
<span style="color: #e91e63; font-weight: 800">注意一定要下载对应型号的系统镜像</span>，下载错误可能导致设备损坏。

> 中国国内用户下载速度慢可以用迅雷下载，速度可能会快一些。
> 或者使用例如 [github.abskoop.workers.dev](https://github.abskoop.workers.dev/) 这种代理网站下载。

备用地址：[Sourceforge](https://sourceforge.net/projects/maixpy/files/) （同步可能不及时，建议优先上面的方式）

## 备份数据

**更新（烧录）系统会抹掉所有数据**。
如果你已经在系统里面存了重要数据，请先将数据拷贝到电脑备份。

备份方法：
* 连接 MaixVision， 使用文件管理功能下载你的重要数据文件到电脑本地，一般来说`/maixapp` 和 `/root` 目录下的文件需要多注意保存。
* 使用 `scp` 命令进行拷贝。
* 使用其它文件管理软件，比如 `WinSCP` 或者 `FileZilla` 等进行传输。
* 直接用读卡器插到电脑拷贝。注意根目录是`ext4`格式，`Windows`默认不支持（可以用三方软件比如diskgenius 读取）。


## 烧录系统到硬件

| 项目 | MaixCAM / MaixCAM-Pro | MaixCAM2 |
| --- | --- | --- |
| 烧录文档 | [MaixCAM 系统烧录](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) | [MaixCAM2 系统烧录](https://wiki.sipeed.com/hardware/zh/maixcam/os_maixcam2.html) |
| 系统存放位置 | TF 卡 | 内置EMMC(/TF卡) |
| 必须 TF 卡 | 是 | 否 |
| 烧录方式 | USB 烧录 或 读卡器烧录 | USB 烧录 或 读卡器烧录 |
| 推荐烧录方式 | USB 烧录 | USB 烧录 |
| 救砖烧录方式 | 读卡器烧录 | USB烧录/读卡器烧录 |


## 什么时候需要更新系统，什么时候可以只更新 MaixPy

为了简单并且不出问题，升级 `MaixPy` 一律**推荐直接更新系统**。

以下情况出现**之一**就**必须**更新系统：
1. TF 卡为新卡，则必须使用 TF 读卡器升级系统。
2. 想升级 MaixPy， [MaixPy 发布页面](https://github.com/sipeed/MaixPy/releases) 显示自旧版本到新版本所有版本中，只要**有一个版本**系统有更新，则**必须更新系统**才能正常使用对应版本的`MaixPy`。
> 比如设备现在运行的`maixcam_os_20240401_maixpy_v4.1.0`，想要升级到`4.7.8`，如果`4.1.0`到 `4.7.8`中间任意一个版本系统有更新则必须更新系统，否则可能导致`MaixPy`无法正常使用。

以下情况**强烈推荐**更新：
1. 第一次拿到手，出厂烧录的系统版本可能比较老旧，升级到最新以保持和文档同步。

以下情况不推荐轻易更新：
1. 功能满足要求，并且在重要场合（比如比赛中、 产品部署中）运行稳定，无需更新。
2. 升级会带来新特性，但由于是开发套件，理论上存在轻微代码不兼容或新引入bug，请在做好开发调试准备的情况下升级。


## 单独升级 MaixPy

仔细阅读上述注意点后，如果你确定你需要只升级 MaixPy，三种方法：
1. MaixVision 中使用`ssh终端`功能，执行`pip install -U MaixPy`，中国可以使用`pip install -U MaixPy -i https://pypi.mirrors.ustc.edu.cn/simple` 下载速度更快。
2. MaixVision 中执行`examples/tools/install_maixpy.py` 脚本来升级。
3. 手动下载[MaixPy-x.x.x-py3-none-any.whl](https://github.com/sipeed/MaixPy/releases)传输到设备，使用`ssh终端`运行`pip install xxx.whl`或者执行代码`import os;os.system("xxx.whl")` 来安装文件。

时间比较长，需要耐心等待。
