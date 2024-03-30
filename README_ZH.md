MaixPy
======

<div align="center">

![](https://wiki.sipeed.com/maixpy/static/image/maixpy_banner.png)

**Let's Sipeed up, Maximize AI's power!**

**MaixPy**: 快速落地 AI 视觉、听觉应用

<h3>
    <a href="https://wiki.sipeed.com/maixpy/doc/en/index.html"> 快速开始 </a> |
    <a href="https://wiki.sipeed.com/maixpy/en/index.html"> 文档 </a> |
    <a href="https://wiki.sipeed.com/maixpy/api/index.html"> API </a> |
    <a href="https://wiki.sipeed.com/MaixCAM"> 硬件 </a>
</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/sipeed/MaixPy?style=social)](https://github.com/sipeed/MaixPy/stargazers)
[![Apache 2.0](https://img.shields.io/badge/license-Apache%20v2.0-orange.svg)]("https://github.com/sipeed/MaixPy/blob/main/LICENSE.md)
[![PyPI](https://img.shields.io/pypi/v/maixpy.svg)](https://pypi.python.org/pypi/maixpy/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/maixpy?label=pypi%20downloads)](https://pypi.org/project/maixpy/)
![GitHub repo size](https://img.shields.io/github/repo-size/sipeed/maixpy) 
[![Build MaixCAM](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml)
[![Trigger wiki](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml)

[English](./README.md) | 中文

</div>



> 新的 MaixPy (v4) 和新的硬件平台 MaixCAM 来了(2024.4)!<br>
> 如果你有任何建议，请在 [MaixHub](https://maixhub.com/discussion/100073) 上告诉我们，或者 [Telegram/MaixPy](https://t.me/maixpy) 或 QQ 群: 862340358。
>
> 点击右上角的 **Star** 让我们知道你喜欢它，以鼓励我们开发更多功能。

## 介绍

使用 MaixPy 轻松创建 **AI 视觉项目**，只需 **10 行代码**:

```python
from maix import camera, display, image, nn

classifier = nn.Classifier(model="/root/models/mobilenetv2.mud")
cam = camera.Camera(classifier.input_width(), classifier.input_height(), classifier.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_text(10, 10, msg, image.COLOR_RED)
    dis.show(img)
```

效果视频:

<video controls autoplay loop muted preload src="https://github.com/sipeed/MaixPy/assets/8625829/d06e4f0e-31af-4679-b3bc-1f93cd633af0" type="video/mp4">
Classifier Result video
</video>

建议的代码使用串口等 **外设**：

```python
from maix import uart

ports = uart.list_ports()

serial = uart.UART(ports[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

## 硬件平台 MaixCAM

提供性能强劲的硬件平台 **[MaixCAM](https://wiki.sipeed.com/maixcam)**:

![MaixCAM](https://wiki.sipeed.com/maixpy/static/image/maixcam.png)

| CPU | NPU | Memory |
| --- | --- | ------- |
| - 1GHz RISC-V(Linux)/ARM A53<br>- 700MHz RISCV-V(RTOS)<br>- 25~300MHz 8051(LowPower) | 1Tops@INT8 NPU, support BF16<br>support YOLOv5 YOLOv8 etc.| 256MB DDR3 |

| Connecting | Peripheral | MultiMedia | Price |
| ----------- | ----- | --- | ---- |
|  USB2.0/WiFi6/BLE5.4 | IIC/PWM/SPI/UART/WDT/ADC | - 4M Camera<br>- 2.3" 552x368 Touchscreen<br>- H.264/H.265/MJPEG codec | [￥169/￥249](https://wiki.sipeed.com/store) |

详情看 [MaixCAM](https://wiki.sipeed.com/maixcam)

> * 大核在 RISC-V and ARM A53 二选一。
> * **Maix-I K210** 已过时，MaixPy v4 不支持它, 仍要使用请访问 **[MaixPy-v1](https://github.com/sipeed/maixpy-v1)**


## 特点

Python 编程, MaixVision IDE, AI 视觉, 视频串流, 语音识别, 外设使用 等。

**细节和视频展示** 请访问官网: [wiki.sipeed.com/maixpy/](https://wiki.sipeed.com/maixpy/)


## Maix 生态系统


MaixPy 不仅仅是一个 Python SDK，还有一个完整的生态系统，包括硬件、软件、工具、文档、甚至云平台等。
看下面的图片:

![](https://wiki.sipeed.com/maixpy/static/image/maix_ecosystem.png)


## 谁在用 MaixPy？

* **AI 算法工程师**： 轻松将你的 AI 模型部署到嵌入式设备。
> MaixPy 提供了易于使用的 API 来访问 NPU，以及帮助你开发 AI 模型的文档。

* **STEM**：想要教学生 AI 和嵌入式开发的老师。
> MaixPy 提供了易于使用的 API，PC 工具，在线 AI 训练服务... 让你专注于教授 AI，而不是硬件和复杂的软件使用。

* **创客**: 想要制作一些酷炫的项目，但不想学习复杂的硬件和软件。
> MaixPy 提供了 Python API，所以你需要做的就是学习基础 Python 语法，而 MaixPy 的 API 非常易于使用，你甚至可以在几分钟内完成你的项目。

* **工程师**: 想要做一些项目，但希望尽快有一个原型。
> MaixPy 易于构建项目，并提供相应的 C++ SDK，所以你可以直接使用 MaixPy 来部署或在几分钟内将 Python 代码转换为 C++。

* **学生**： 想要学习 AI，嵌入式开发。
> 我们提供了许多文档和教程，以及大量开源代码，帮助你找到学习路线，并逐步成长。从简单的 Python 编程到视觉，AI，音频，Linux，RTOS等。

* **企业**: 想要开发 AI 视觉产品，但没有时间或工程师来开发复杂的嵌入式系统。
> 使用 MaixPy 甚至图形编程来开发你的产品，不需要更多的员工和时间。例如，向你的生产线添加一个 AI QA 系统，或者根据你的需求向你的办公室添加一个 AI 安全监控器。

* **竞赛者**: 想要赢得比赛的比赛人们。
> MaixPy 集成了许多功能，易于使用，加快你作品产出速度，以在有限的时间内赢得比赛，国内常见比赛都有很多同学使用 MaixPy 赢得比赛。

## 性能对比

相比上两代 Maix 系列产品有限的 NPU 算子支持和内存限制，MaixCAM 在保持超高性价比的同时，性能和体验有了很大的提升，强烈建议升级到最新的 MaixCAM 以及 MaixPy v4。

| 特征 | Maix-I K210 | Maix-II v831 | MaixCAM |
| ------- | ----------- | ------------ | ------- |
| CPU | 400MHz RISC-V x2 | 800MHz ARM7 | **1GHz RISC-V(Linux)<br>700MHz RISC-V(RTOS)<br>25~300MHz 8051(Low Power)** |
| 内存 | 6MB SRAM | 64MB DDR2 | **256MB DDR3** |
| NPU | 0.25Tops@INT8<br>official says 1T but... | 0.25Tops@INT8 | **1Tops@INT8** |
| Encoder | ✖ | 1080p@30fps | **2K@30fps** |
| 屏幕 | 2.4" 320x240 | 1.3" 240x240 | **2.28" 552x368** / 5" 1280x720 / 7" 1280x800 / 10“ 1280x800|
| 触摸屏 | ✖ | ✖ | **2.3" 552x368** |
| 摄像头 | 30W | 200W | **500W** |
| WiFi   | 2.4G | 2.4G | **WiFi6** 2.4G/5G |
| USB    | ✖    | **USB2.0** | **USB2.0** |
| 以太网    | ✖    | 100M(选配)   | 100M(选配) |
| SD 卡接口 | SPI | **SDIO** | **SDIO** |
| BLE    | ✖    | ✖      | **BLE5.4** |
| 操作系统     | RTOS | Tina Linux | **Linux + RTOS** |
| 编程语言 | C / C++ / MicroPython | C / C++ / **Python3** | C / **C++ / Python3** |
| Software | MaixPy | MaixPy3 | **MaixCDK + MaixPy v4 + opencv + numpy + ...**|
| PC 软件 | MaixPy IDE | MaixPy3 IDE | **MaixVision** Workstation |
| 文档   | ⭐️⭐️⭐️⭐️ |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |
| 在线 AI 训练 | ⭐️⭐️⭐️ |  ⭐️⭐️⭐️⭐️ |  🌟🌟🌟🌟🌟 |
| 官方应用   | ⭐️⭐️   |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |
| AI 分类(224x224) | MobileNetv1 50fps<br>MobileNetv2 ✖<br>Resnet ✖ | MobileNet ✖<br>Resnet18 20fps<br>Resnet50 ✖| MobileNetv2 **130fps**<br>Resnet18 **62fps**<br>Resnet50 **28fps** |
| AI 检测   | YOLOv2(224x224) 15fps |  YOLOv2(224x224) 15fps |  **YOLOv5s(224x224) 100fps<br>YOLOv5s(320x256) 70fps<br>YOLOv5s(640x640) 15fps<br>YOLOv8n(640x640) 23fps**|
| 易用性     | ⭐️⭐️⭐️⭐️ |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |

## What difference between MaixPy v1, MaixPy3 and MaixPy v4?

* MaixPy v1 use MicroPython programming language, only support Sipeed Maix-I K210 series hardware, have limited third-party packages.
* MaixPy3 is designed for Sipeed Maix-II-Dock v831, not a long-term support version.
* MaixPy v4 use Python programming language, so there's much package we can use directly. MaixPy v4 support new hardware platforms of Sipeed, it's a long-term support version, the future's hardware platforms will support this version. MaixPy v4 have a MaixPy-v1 compatible API, so you can quickly migrate your MaixPy v1 project to MaixPy v4.

(MaixPy v4 Will not support Maix-I K210 series, if you are using Maix-I K210 series, it's recommended to upgrade hardware platform to use this to get more features and better performance.)

## MaixPy v1, MaixPy3 and MaixPy v4 有什么区别？

* MaixPy v1 使用 MicroPython 编程语言，仅支持 Sipeed Maix-I K210 系列硬件，有限的第三方包。
* MaixPy3 专为 Sipeed Maix-II-Dock v831 设计，不是长期支持版本。
* MaixPy v4 使用 Python 编程语言，因此我们可以直接使用许多包。MaixPy v4 支持 Sipeed 的新硬件平台，这是一个长期支持版本，未来的硬件平台将支持这个版本。MaixPy v4 有一个 MaixPy-v1 兼容的 API，所以你可以快速将你的 MaixPy v1 项目迁移到 MaixPy v4。

(MaixPy v4 不支持 Maix-I K210 系列，如果你正在使用 Maix-I K210 系列，建议升级硬件平台以使用此版本，以获得更多功能和更好的性能。)

## 开源协议


所有在本仓库中的文件都遵循 [Apache License 2.0 Sipeed Ltd.](https://github.com/sipeed/maixpy/blob/main/LICENSE) 协议，除了第三方库或者有自己的协议。

## 社区

* 项目分享: [maixhub.com/share](https://maixhub.com/share)
* 讨论: [maixhub.com/discussion](https://maixhub.com/discussion)
* QQ 群: 862340358
* Telegram: [t.me/maixpy](https://t.me/maixpy)




