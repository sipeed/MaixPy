MaixPy (v4)
======

<div align="center">

![](https://wiki.sipeed.com/maixpy/static/image/maixpy_banner.png)

**Let's Sipeed up, Maximize AI's power!**

**MaixPy** (v4): Easily create AI projects with Python on edge device

<h3>
    <a href="https://wiki.sipeed.com/maixpy/doc/en/index.html"> Quick Start </a> |
    <a href="https://wiki.sipeed.com/maixpy/en/index.html"> Documentation </a> |
    <a href="https://wiki.sipeed.com/maixpy/api/index.html"> API </a> |
    <a href="https://wiki.sipeed.com/maixcam-pro"> Hardware </a>
</h3>

[![GitHub Repo stars](https://img.shields.io/github/stars/sipeed/MaixPy?style=social)](https://github.com/sipeed/MaixPy/stargazers)
[![Apache 2.0](https://img.shields.io/badge/license-Apache%20v2.0-orange.svg)]("https://github.com/sipeed/MaixPy/blob/main/LICENSE.md)
[![PyPI](https://img.shields.io/pypi/v/maixpy.svg)](https://pypi.python.org/pypi/maixpy/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/maixpy?label=pypi%20downloads)](https://pypi.org/project/maixpy/)
![GitHub repo size](https://img.shields.io/github/repo-size/sipeed/maixpy) 
[![Build MaixCAM](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml)
[![Trigger wiki](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml)

English | [中文](./README_ZH.md)

</div>

![MaixCAM](https://wiki.sipeed.com/maixpy/static/image/maixcams.png)


## Feature Overview

MaixPy offers simple Python programming combined with powerful edge computing hardware. Integrated hardware peripheral operations, video streaming, AI vision algorithms, and audio algorithms etc. With its plug-and-play design, MaixPy enables you to quickly implement your intelligent projects.

Additionally, MaixPy provides the MaixVision IDE, MaixHub online training platform, detailed documentation, and even a C/C++ SDK with identical APIs, ensuring seamless development and production deployment.

Here is a partial video demonstration of the features. For more documentation, please visit the **official website: [wiki.sipeed.com/maixpy/](https://wiki.sipeed.com/maixpy/)**

> If you like this project, please click **Star** on the top right of the [MaixPy Project](https://github.com/sipeed/maixpy) to encourage us to develop more exciting content!

[![](./docs/static/image/maixcam_play.jpg)](https://www.youtube.com/watch?v=qV1lw0UVUYI)


## Concise and Efficient Code (API) Design

With MaixPy you can easily create **AI vision project** within **10 lines of code**:

```python
from maix import camera, display, image, nn

classifier = nn.Classifier(model="/root/models/mobilenetv2.mud")
cam = camera.Camera(classifier.input_width(), classifier.input_height(), classifier.input_format())
disp = display.Display()

while 1:
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_string(10, 10, msg, image.COLOR_RED)
    disp.show(img)
```

Result:
![](https://wiki.sipeed.com/maixpy/static/video/classifier.gif)

## Edge(embeded) friendly

Simply use hardware **peripheral** like serial port:

```python
from maix import uart

devices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

## MaixVision workstation

We also provide a handy **[MaixVision](https://wiki.sipeed.com/en/maixvision)** workstation software to make development easier and faster:

<video playsinline controls muted preload src="https://github.com/sipeed/MaixPy/assets/8625829/1168a282-d7c2-45bc-9ffb-c00de1ca24f5" type="video/mp4">
MaixVision
</video>

## MaixHub online platform

**[MaixHub](https://maixhub.com)** provide free online AI train service, one click to train AI model and deploy to MaixCAM even you have no AI knowledge and expensive training equipment.

![MaixHub](https://wiki.sipeed.com/maixpy/static/image/maixhub.jpg)


## Hardware platform MaixCAM

And we provide two powerful hardware platform **[MaixCAM](https://wiki.sipeed.com/maixcam)** and **[MaixCAM-Pro](https://wiki.sipeed.com/maixcam-pro)**, with datasheet register level open.

![MaixCAM](https://wiki.sipeed.com/maixpy/static/image/maixcams.png)

| CPU | NPU | Memory |
| --- | --- | ------- |
| - 1GHz RISC-V(Linux)<br>- 700MHz RISCV-V(RTOS)<br>- 25~300MHz 8051(LowPower) | 1Tops@INT8 NPU, support BF16<br>support YOLOv5 YOLOv8 etc.| 256MB DDR3 |

| Connecting | Peripheral | MultiMedia | Buy |
| ----------- | ----- | --- | ---- |
|  USB2.0/WiFi6/BLE5.4 | IIC/PWM/SPI/UART/WDT/ADC | - 4M Camera<br>- 2.3" 552x368 Touchscreen<br>- H.264/H.265/MJPEG codec | [Sipeed Official Store](https://wiki.sipeed.com/store) |


## Who are using MaixPy?

* **AI Algorithm Engineer** who want to deploy your AI model to embedded devices.
> MaixPy provide easy-to-use API to access NPU, and docs to help you develop your AI model.
* **STEM** teacher who wants to teach AI and embedded devices to students.
> MaixPy provide easy-to-use API, PC tools, online AI train service ... Let you focus on teaching AI, not the hardware and complicated software usage.
* **Maker** who want to make some cool projects but don't want to learn complicated hardware and software.
> MaixPy provide Python API, so all you need is learn basic Python syntax, and MaixPy's API is so easy to use, you can make your project even in a few minutes.
* **Engineer** who want to make some projects but want a prototype as soon as possible.
> MaixPy is easy to build projects, and provide corresponding C++ SDK, so you can directly use MaixPy to deploy or transfer Python code to C++ in a few minutes.
* **Students** who want to learn AI, embedded development.
> We provide many docs and tutorials, and lot of open source code, to help you find learning route, and grow up step by step. From simple Python programming to `Vision`, `AI`, `Audio`, `Linux`, `RTOS` etc.
* **Enterprise** who want to develop AI vision products but have no time or engineers to develop complicated embedded system.
> Use MaixPy even graphic programming to develop your products with no more employees and time. For example, add a AI QA system to your production line, or add a AI security monitor to your office as your demand.
* **Contestants** who want to win the competition.
> MaixPy integrate many functions and easy to use, fasten your work to win the competition in limited time. There are already many contestants win the competition with MaixPy.


## Performance comparison

K210 and v831 are outdated, they have many limitations in memory, performance, NPU operators missing etc.<br>
No matter you are using them or new comer, it's recommended to upgrade to MaixCAM and MaixPy v4.<br>

Here's the comparison between them:

| Feature | Maix-I K210 | Maix-II v831 | MaixCAM |
| ------- | ----------- | ------------ | ------- |
| CPU | 400MHz RISC-V x2 | 800MHz ARM7 | **1GHz RISC-V(Linux)<br>700MHz RISC-V(RTOS)<br>25~300MHz 8051(Low Power)** |
| Memory | 6MB SRAM | 64MB DDR2 | **256MB DDR3** |
| NPU | 0.25Tops@INT8<br>official says 1T but... | 0.25Tops@INT8 | **1Tops@INT8** |
| Encoder | ✖ | 1080p@30fps | **2K@30fps** |
| Screen | 2.4" 320x240 | 1.3" 240x240 | **2.28" 552x368** / 5" 1280x720 / 7" 1280x800 / 10“ 1280x800|
| TouchScreen | ✖ | ✖ | **2.3" 552x368** |
| Camera | 30W | 200W | **500W** |
| WiFi   | 2.4G | 2.4G | **WiFi6** 2.4G/5G |
| USB    | ✖    | **USB2.0** | **USB2.0** |
| Eth    | ✖    | 100M(Optional)   | 100M(Optional) |
| SD Interface | SPI | **SDIO** | **SDIO** |
| BLE    | ✖    | ✖      | **BLE5.4** |
| OS     | RTOS | Tina Linux | **Linux + RTOS** |
| Language | C / C++ / MicroPython | C / C++ / **Python3** | C / **C++ / Python3** |
| Software | MaixPy | MaixPy3 | **MaixCDK + MaixPy v4 + opencv + numpy + ...**|
| PC software | MaixPy IDE | MaixPy3 IDE | **MaixVision** Workstation |
| Docs   | ⭐️⭐️⭐️⭐️ |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |
| Online AI train | ⭐️⭐️⭐️ |  ⭐️⭐️⭐️⭐️ |  🌟🌟🌟🌟🌟 |
| Official APPs   | ⭐️⭐️   |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |
| AI classify(224x224) | MobileNetv1 50fps<br>MobileNetv2 ✖<br>Resnet ✖ | MobileNet ✖<br>Resnet18 20fps<br>Resnet50 ✖| MobileNetv2 **130fps**<br>Resnet18 **62fps**<br>Resnet50 **28fps** |
| AI detect(NPU forward part)   | YOLOv2(224x224) 15fps |  YOLOv2(224x224) 15fps |  **YOLOv5s(224x224) 100fps<br>YOLOv5s(320x256) 70fps<br>YOLOv5s(640x640) 15fps<br>YOLOv8n(640x640) 23fps<br>YOLO11n(224x224)175fps<br>YOLO11n(320x224)120fps<br>YOLO11n(320x320)95fps<br>YOLO11n(640x640)23fps**|
| Ease of use     | ⭐️⭐️⭐️⭐️ |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |

## Maix Ecosystem

MaixPy not only a Python SDK, but have a whole ecosystem, including hardware, software, tools, docs, even cloud platform etc.
See the picture below:

![](https://wiki.sipeed.com/maixpy/static/image/maix_ecosystem.png)


## What difference between MaixPy v1, MaixPy3 and MaixPy v4?

* MaixPy v1 use MicroPython programming language, only support Sipeed Maix-I K210 series hardware, have limited third-party packages.
* MaixPy3 is designed for Sipeed Maix-II-Dock v831, not a long-term support version.
* MaixPy v4 use Python programming language, so there's much package we can use directly. MaixPy v4 support new hardware platforms of Sipeed, it's a long-term support version, the future's hardware platforms will support this version. MaixPy v4 have a MaixPy-v1 compatible API, so you can quickly migrate your MaixPy v1 project to MaixPy v4.

(MaixPy v4 Will not support Maix-I K210 series, if you are using Maix-I K210 series, it's recommended to upgrade hardware platform to use this to get more features and better performance.)

## Compile Source Code

If you want to compile MaixPy firmware from source code, refer to [Build MaixPy source code](https://wiki.sipeed.com/maixpy/doc/en/source_code/build.html) page.


## License

All files in this repository are under the terms of the [Apache License 2.0 Sipeed Ltd.](./LICENSE) except the third-party libraries or have their own license.


## Community

* Project sharing: [maixhub.com/share](https://maixhub.com/share)
* App sharing: [maixhub.com/app](https://maixhub.com/app)
* Discussion: [maixhub.com/discussion](https://maixhub.com/discussion)
* QQ group: 862340358
* Telegram: [t.me/maixpy](https://t.me/maixpy)
* Github issues: [github.com/sipeed/maixpy/issues](https://github.com/sipeed/maixpy/issues)



