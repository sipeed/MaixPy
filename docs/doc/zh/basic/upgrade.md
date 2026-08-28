---
title: 升级和烧录系统
---

## 系统和 MaixPy 介绍

首先需要区分一下  `系统` 和 `MaixPy`:
* **系统**： 运行所有软件的基础，包含了操作系统和驱动等，所有软件运行的基石。
* **MaixPy**: 软件包，依赖系统的驱动运行。

## 获得最新系统并烧录到硬件

烧录前请先确认设备型号和系统存储位置。MaixCAM / MaixCAM-Pro 的系统运行在 TF 卡中，需要准备 TF 卡；MaixCAM2 默认运行在板载 eMMC 中，日常升级通常不需要 TF 卡。常规升级建议优先使用对应烧录页面中的 USB 烧录流程；需要从 TF 卡启动、恢复系统或更换存储介质时，再按页面说明选择对应方式。

确认后，按下表选择对应的系统镜像和烧录页面。

| 设备型号 | 下载入口 | 选择文件 | 烧录页面 |
| --- | --- | --- | --- |
| MaixCAM | [GitHub 下载](https://github.com/sipeed/MaixPy/releases) | `maixcam-*.img.xz` | [MaixCAM 系统烧录](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) |
| MaixCAM-Pro | [GitHub 下载](https://github.com/sipeed/MaixPy/releases) | `maixcam-pro-*.img.xz` | [MaixCAM 系统烧录](https://wiki.sipeed.com/hardware/zh/maixcam/os.html) |
| MaixCAM2 | [百度网盘（提取码：dshn）](https://pan.baidu.com/s/1nk60bNu5QhdNAsp7e_c-xw) | `maixcam2-*-maixpy-*_sd.img.7z.*` | [MaixCAM2 系统烧录](https://wiki.sipeed.com/hardware/zh/maixcam/maixcam2_os.html) |

> 国内用户如果访问 GitHub 较慢，也可以到 MaixPy (v4) AI 视觉交流大群（QQ：862340358）的群文件中下载对应型号的系统镜像。

<span style="color: #e91e63; font-weight: 800">注意一定要下载对应型号的系统镜像</span>，下载错误可能导致设备异常，甚至需要重新救砖烧录。

下载时请按表格里的“选择文件”列选择同型号的最新文件。MaixCAM 和 MaixCAM-Pro 请在 GitHub 下载页面中选择对应镜像；MaixCAM2 镜像为分卷压缩包，请在百度网盘中下载同一版本的全部 `.7z.00x` 文件后再解压烧录。

## 备份数据

**更新（烧录）系统会抹掉所有数据**。
如果你已经在系统里面存了重要数据，请先将数据拷贝到电脑备份。

建议按下面顺序选择备份方式。完成备份后，请先在电脑上打开备份目录确认文件存在，再继续烧录。

1. **推荐：使用 MaixVision 文件管理器备份**。用 USB 连接设备并在 MaixVision 中连接设备，打开“设备文件管理器”，进入 `/maixapp` 和 `/root` 目录，将需要保留的工程、模型、图片、配置文件下载到电脑本地文件夹。
2. **进阶：使用 `scp` 命令备份**。如果你已经熟悉终端和 SSH，可以在电脑终端执行下面命令。先将 `<设备IP或设备名>` 替换为设备信息，设备名可以在设备的“设置 -> 设备信息”中查看。MaixCAM / MaixCAM-Pro 默认密码为 `root`，MaixCAM2 默认密码为 `sipeed`。

   ```bash
   mkdir maix_backup
   scp -r root@<设备IP或设备名>:/maixapp ./maix_backup/
   scp -r root@<设备IP或设备名>:/root ./maix_backup/
   ```

   如果不了解 SSH 或 `scp`，请先阅读 [Linux 基础知识](./linux_basic.md) 中的连接说明。
3. **备用：使用 WinSCP / FileZilla 图形工具备份**。适合不想使用命令行的用户。先在电脑安装并打开 `WinSCP` 或 `FileZilla`，输入连接信息：协议选择 `SFTP`，主机填写设备 IP 或设备名，端口填写 `22`，用户名填写 `root`，密码按设备型号填写（MaixCAM / MaixCAM-Pro 为 `root`，MaixCAM2 为 `sipeed`）。连接成功后，左侧是电脑目录，右侧是设备目录，进入设备的 `/maixapp` 和 `/root`，把需要保留的文件拖到电脑备份文件夹中。
4. **备用：使用 TF 卡读卡器备份**。关机后取出设备正在使用的 TF 卡，用读卡器插到电脑，再复制需要保留的文件；如果需要读取 Linux 根分区，Windows 默认无法读取 `ext4`，请使用 Linux 电脑或 DiskGenius 等支持 `ext4` 的工具读取。


## 什么时候需要更新系统

更新系统会重新写入系统镜像，适合处理底层系统、驱动、系统库或启动异常相关问题。出现以下任意情况时，请优先更新系统：

1. 设备无法正常启动、系统文件损坏，或已经更换 / 格式化系统存储介质，需要重新烧录系统镜像。
2. 第一次拿到设备，出厂系统版本可能较旧，建议先更新到最新系统，再按照当前文档学习和开发。
3. 第一次准备一张 TF 卡给 MaixCAM / MaixCAM-Pro 使用时，建议按上方表格进入对应烧录页面，完整烧录一次最新系统镜像。
4. 想升级 MaixPy，并且 [GitHub 下载页面](https://github.com/sipeed/MaixPy/releases) 中从当前版本到目标版本之间有任意版本发布了系统镜像更新。操作时先在设备设置的设备信息中查看当前系统或 MaixPy 版本，再到 GitHub 下载页面查看目标版本及中间版本说明；如果无法判断是否跨过系统更新版本，建议直接更新系统。
5. 需要使用的新功能明确依赖新版系统、驱动或系统库，例如文档、示例或更新说明中要求先更新系统。

> 比如设备现在运行的 `maixcam_os_20240401_maixpy_v4.1.0`，想要升级到 `4.7.8`，如果 `4.1.0` 到 `4.7.8` 中间任意一个版本系统有更新，则需要更新系统，否则可能导致 `MaixPy` 或相关功能无法正常使用。

如果当前功能已经满足需求，并且设备正在比赛、演示、产品部署等重要场景中稳定运行，可以暂时不升级；需要升级时，请先完成数据备份，再选择对应型号的烧录页面操作。

## 什么时候可以只更新 MaixPy

只更新 MaixPy 不会重新烧录系统，适合在系统环境已经满足要求时更新 Python 软件包。建议同时满足以下条件时再选择这种方式：

1. 设备可以正常启动，摄像头、屏幕、网络、文件读写等基础功能工作正常。
2. 只需要更新 MaixPy 的 Python API、示例程序或问题修复，不涉及系统镜像、驱动或底层库更新。
3. 已经查看 [GitHub 下载页面](https://github.com/sipeed/MaixPy/releases) 的目标版本及中间版本说明，确认没有必须同步更新系统的要求。
4. 已经按上文完成数据备份；如果只更新 MaixPy 后出现兼容问题，可以回到更新系统流程重新烧录恢复。

如果不确定是否满足以上条件，建议直接更新系统，这样对新手更稳妥。

## 如何单独升级 MaixPy

确认可以只更新 MaixPy 后，可以选择下面任意一种方式。新手优先使用方法 1；如果升级失败或不确定系统是否匹配，请回到上文直接更新系统。

1. **在 MaixVision 终端在线升级**：连接设备，在 MaixVision 中打开“设备终端 / ssh 终端”，执行：

   ```bash
   pip install -U MaixPy
   ```

   国内网络下载较慢时可执行：

   ```bash
   pip install -U MaixPy -i https://pypi.mirrors.ustc.edu.cn/simple
   ```

   命令执行完成且没有报错后，重启应用或重启设备，再运行程序确认版本已更新。
2. **运行 MaixVision 示例脚本升级**：在 MaixVision 示例中找到 `examples/tools/install_maixpy.py`，连接设备后点击运行。脚本会自动下载并安装 MaixPy，运行完成后按提示重启应用或设备。
3. **手动安装 `.whl` 文件**：在 [GitHub 下载页面](https://github.com/sipeed/MaixPy/releases) 下载 `MaixPy-x.x.x-py3-none-any.whl`，用 MaixVision 文件管理器上传到设备 `/root` 目录，然后在 MaixVision 终端执行：

   ```bash
   pip install /root/MaixPy-x.x.x-py3-none-any.whl
   ```

   请将命令中的文件名替换为实际下载的文件名。安装完成后重启应用或设备。

时间比较长，需要耐心等待。
