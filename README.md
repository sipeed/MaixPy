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
    <a href="https://wiki.sipeed.com/maixcam"> Hardware </a>
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

MaixPy offers simple Python programming combined with powerful edge computing hardware. Integrated hardware peripheral operations, video streaming, AI vision algorithms, audio algorithms, and LLM / VLM etc. With its plug-and-play design, MaixPy enables you to quickly implement your intelligent projects.

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

And we provide two powerful hardware platform **[MaixCAM2](https://wiki.sipeed.com/maixcam2)**, **[MaixCAM](https://wiki.sipeed.com/maixcam)** and **[MaixCAM-Pro](https://wiki.sipeed.com/maixcam-pro)**.

![MaixCAM](https://wiki.sipeed.com/maixpy/static/image/maixcams.png)


## Performance comparison

K210 and v831 are outdated, they have many limitations in memory, performance, NPU operators missing etc.<br>
No matter you are using them or new comer, it's recommended to upgrade to MaixCAM and MaixPy v4.<br>

Here's the comparison between them:

| Feature      | Maix-I K210 | MaixCAM | MaixCAM2 |
| --------- | ----------- | ------- | ------- |
| CPU       | 400MHz RISC-V x2 |  **1GHz RISC-V(Linux)<br>700MHz RISC-V(RTOS)<br>25~300MHz 8051(Low Power)** | <span class="strong2">1.2GHz A53 x2(Linux)</span><br>RISC-V 32bit E907(RTT) |
| Memory      | 6MB SRAM         | **256MB DDR3** | <span class="strong2">1GB / 4GB LPDDR4</span> |
| NPU       | 0.25Tops@INT8<br>official says 1T but... | **1Tops@INT8** | <span class="strong2">3.2Tops@INT8</span> |
| Encoder   | ❌               | **2880x1620@30fps H.254/H.265/JPEG** | <span class="strong2">3840*2160@30fps H.254/H.265/JPEG</span> |
| Decoder   | ❌               | **2880x1620@30fps H.264/JPEG** | **1080p@60fps H.264/JPEG** |
| Screen      | 2.4" 320x240     | **2.3" 552x368**(MaixCAM)<br/>**2.4" 640x480**(MaixCAM-Pro)<br/>5" 1280x720<br/>7" 1280x800<br/>10“ 1280x800| **2.4" 640x480**<br/>5" 1280x720<br/>7" 1280x800<br/>10“ 1280x800 |
| Touchscree    | ❌               | **2.3" 552x368**/**2.4" 640x480** | **2.4" 640x480** |
| Camera    | 30W              | **500W(5M)** | <span class="strong2">800W(8M)</span> |
| AI ISP    | ❌               | ❌           | <span class="strong2">✅</span> |
| WiFi      | 2.4G             | **WiFi6** 2.4G/5G | **WiFi6** 2.4G/5G |
| BLE       | ❌               | **BLE5.4** | **BLE5.4** |
| USB       | ❌               | **USB2.0** | **USB2.0** |
| Ethernet    | ❌               | 100M(Optional) | <span class="strong2">100M(on board FPC, can convert to RJ45 module)</span> |
| SD Card | SPI              | **SDIO** | **SDIO** |
| OS  | RTOS             | **Linux(BuildRoot) + RTOS** | Linux(<span class="strong2">Ubuntu</span>) + RTT |
| Porgraming Language  | C / C++ / MicroPython | C / **C++ / Python3** | C / **C++ / Python3** |
| SDK    | MaixPy-v1             | **MaixCDK + MaixPy v4<br>+ opencv + numpy + ...**<br>Pure Python package or cross-compile manually | **MaixCDK + MaixPy v4<br>+ opencv + numpy + scipy + ...**<br><span class="strong2">Many AArch64 pre-compiled packages, and support compile on board</span> |
| PC Software   | MaixPy IDE            | **MaixVision** Workstation | **MaixVision** Workstation |
| Documentation             | ⭐️⭐️⭐️⭐️     |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| Online AI train       | ⭐️⭐️⭐️        |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| Official APPs         | ⭐️             |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| Ease of use           | ⭐️⭐️⭐️⭐️      |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| AI classify(224x224) | MobileNetv1 50fps<br>MobileNetv2 ❌<br>Resnet ❌ | MobileNetv2 **130fps**<br>Resnet18 **62fps**<br>Resnet50 **28fps** | MobileNetv2 <span class="strong2">1218fps</span><br>Resnet50 <span class="strong2">200fps</span> |
| AI detect<div class="comment">only forward part /<br>\[include pre-post process parts(Python)\] /<br>\[dual buff mode(Python)\]</div> | <div class="main_items">**YOLOv2**:<div class="sub_items">224x224: 15fps</div></div> |  <div class="main_items">**YOLOv5s**:<div class="sub_items">224x224: **100fps**<br>320x256 **70fps**<br>640x640: **15fps**</div></div>       <div class="main_items">**YOLOv8n**:<div class="sub_items">640x640: **23fps**</div></div>      <div class="main_items">**YOLO11n**:<div class="sub_items">224x224: **175fps**<br>320x224: **120fps**<br>320x320: **95fps**<br>640x640: **23fps**</div></div>                |                <div class="main_items">**YOLOv5s**:<div class="sub_items">224x224: <span class="strong2">495fps</span><br>320x256: <span class="strong2">400fps</span><br>640x480: <span class="strong2">106fps / 73fps / 103fps</span><br>640x640: <span class="strong2">80fps</span></div></div>                <div class="main_items">**YOLO11n**:<div class="sub_items">224x224: <span class="strong2">1214fps</span><br>640x480: <span class="strong2">168fps / 77fps / 143fps</span><br>640x640: <span class="strong2">113fps / 56fps / 98fps</span></div></div>    <div class="main_items">**YOLO11s**:<div class="sub_items">640x480: <span class="strong2">87fps / 53fps / 83fps</span><br>640x640: <span class="strong2">62fps / 39fps / 59fps</span></div></div>   <div class="main_items">**YOLO11l**:<div class="sub_items">640x640: <span class="strong2">19fps / 16fps / 19fps</span></div></div>                     |
| LLM           | ❌              |  ❌           |  <span class="strong2">Qwen/DeepSeek 0.5B(fftf: 640ms, 9 tokens/s)<br>Qwen/DeepSeek 1.5B(fftf: 1610ms, 4 tokens/s) <br> VLM(InterVL 1B) <br>Mode models</span> |
| OpenMV algorithms |  <div class="comment">test image refer to <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a>  |                    <div class="comment">test image refer to <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>test date: 2025.8.22，update may have optimization</div>              |       <div class="comment">test image refer to <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>test date: 2025.8.22，update may have optimization</div>                             |
|   <div class="right second">Binary</div>  | Gray 320x240: 7.4ms (135fps)<br>Gray 640x480: ❌<br>RGB 320x240: 11.3ms (88.5fps)<br>RGB 640x480: ❌ | Gray 320x240: **3.1ms (326fps)**<br>Gray 640x480: **11ms (90fps)**<br>RGB 320x240: **13.2ms (75fps)**<br>RGB 640x480: **52.8ms (18fps)**        | Gray 320x240: <span class="strong2">1.3ms (799fps)</span> <br>Gray 640x480: <span class="strong2">4.8ms (206fps)</span><br>RGB 320x240: <span class="strong2">3.4ms (294fps)</span><br>RGB 640x480: <span class="strong2">13.3ms (75fps)</span> |
|   <div class="right second">Find blobs</div>        | 320x240: 8.8ms (114fps) <br>640x480: ❌| 320x240: **7ms (143fps)**  <br>640x480: **20ms (50fps)**         | 320x240: <span class="strong2">3.7ms (271fps)</span><br>640x480: <span class="strong2">11.1ms (89fps)</span>  |
|   <div class="right second">1channel histogram</div>  | 320x240: **7.7ms (130fps)**<br>640x480: ❌ | 320x240: **10.9ms (91fps)**<br>640x480: **42.8ms (23fps)**       | 320x240: <span class="strong2">1.5ms (661fps)</span><br>640x480: <span class="strong2">5.9ms (168fps)</span>    |
|   <div class="right second">QR Code</div>        | 320x240: **130.8ms (7.6fps)** <br>640x480: ❌| 640x480: 136.9ms (7fps)<br>NPU acceleration：<br>&nbsp;&nbsp;320x240: **22.1ms (45fps)**<br>&nbsp;&nbsp;640x480: 57.6ms (17fps)  | 640x480: 57.9ms (17fps)<br>NPU acceleration：<br>&nbsp;&nbsp;320x240: <span class="strong2">9.2ms (109fps)</span>   <br>&nbsp;&nbsp;640x480: <span class="strong2">23.2ms (43fps)</span> |
| OpenCV algorithms     |   | <div class="comment">test image refer to <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>test date: 2025.8.22，update may have optimization</div>    | <div class="comment">test image refer to <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>test date: 2025.8.22，update may have optimization</div>  |
|   <div class="right second">Binary</div>             | ❌  | Gray 320x240: **2.2ms (463fps)**     <br>Gray 640x480: **7.1ms (140fps)** | Gray 320x240: <span class="strong2">0.1ms (8174fps)</span>  <br>Gray 640x480: <span class="strong2">0.3ms (2959fps)</span>  |
|   <div class="right second">Gray adaptive binary</div> | ❌  | 320x240: **5.8ms (171fps)**     <br>640x480: **21.3ms (46fps)**  | 320x240: <span class="strong2">1.6ms (608fps)</span>  <br>640x480: <span class="strong2">6.3ms (159fps)</span> |
|   <div class="right second">1channel histogram</div>       | ❌  | 320x240: **1ms (1000fps)**     <br>640x480: **6.2ms (160fps)**   | 320x240: <span class="strong2">0.4ms (2308fps)</span>  <br>640x480: <span class="strong2">1.7ms (604fps)</span>  |
|   <div class="right second">Find Contours</div>           | ❌  | 320x240: **2.8ms (351fps)**    <br>640x480: **8.6ms (116fps)**   | 320x240: <span class="strong2">0.4ms (2286fps)</span>  <br>640x480: <span class="strong2">1.4ms (692fps)</span>  |

## Maix Ecosystem

MaixPy not only a Python SDK, but have a whole ecosystem, including hardware, software, tools, docs, even cloud platform etc.
See the picture below:

![](https://wiki.sipeed.com/maixpy/static/image/maix_ecosystem.png)


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



