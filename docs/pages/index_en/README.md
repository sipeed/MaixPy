
---
title: MaixPy
id: home_page
---

<div>
<script src="/static/css/tailwind.css"></script>
</div>

<style>
.md_page #page_content
{
    padding: 1em;
}
.md_page #page_content > div
{
    width: 100%;
    max-width: 100%;
    text-align: left;
}
@media (min-width: 1280px) {
    .md_page #page_content > div
    {
        width: 1440px;
        max-width: 1440px;
    }
}
h1 {
    font-size: 3em;
    font-weight: 600;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
}
h2 {
    font-size: 1.6em;
    font-weight: 600;
    margin-top: 1em;
    margin-bottom: 0.67em;
}
h3 {
    font-size: 1.5em;
    font-weight: 400;
    margin-top: 0.5em;
    margin-bottom: 0.5em;
}
#tags > p {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    padding: 1em;
}
#tags > p a {
    margin: 0.2em 0.2em;
}
#feature video, #feature img {
    height: 15em;
}
.feature_item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    margin: 1em;
    border: 2px solid #EEEEEE;
    border-radius: 0.5em;
    overflow: hidden;
    max-width: 20em;
}
.feature_item .feature {
    font-size: 1.2em;
    font-weight: 600;
}
.feature_item .description {
    font-size: 0.8em;
    font-weight: 400;
}
.feature_item video, .feature_item img {
    width: 100%;
    object-fit: cover;
}
.feature_item .img_video {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.feature_item > div {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
}
.feature_item p {
    padding: 0.5em;
}
#page_content li {
    margin: 0.5em;
    list-style-type: disc;
}
</style>

<div class="w-full flex flex-col justify-center text-center">
    <div class="flex justify-center">
        <img src="/static/image/maixpy_banner.png" alt="MaixPy Banner">
    </div>
    <h1><span>MaixPy (v4)</span></h1>
    <h3>Easily create AI projects with Python on edge device</h3>
</div>

<div id="big_btn_wrapper" class="flex flex-wrap justify-center items-center">
    <a class="btn m-1" href="/doc/en/index.html">Quick Start 🚀📖</a>
    <a class="btn m-1" href="/api/">API Reference 📚</a>
    <a class="btn m-1" target="_blank" href="https://wiki.sipeed.com/maixcam">Hardware：MaixCAM 📷</a>
    <a class="btn m-1" target="_blank" href="https://github.com/sipeed/maixpy">Source Code ⭐️</a>
    <a class="btn m-1" target="_blank" href="https://maixhub.com/app">APP Store 📦</a>
</div>

<div id="tags">

[![GitHub Repo stars](https://img.shields.io/github/stars/sipeed/MaixPy?style=social)](https://github.com/sipeed/MaixPy)[![Apache 2.0](https://img.shields.io/badge/license-Apache%20v2.0-orange.svg)]("https://github.com/sipeed/MaixPy/blob/main/LICENSE.md)[![PyPI](https://img.shields.io/pypi/v/maixpy.svg)](https://pypi.python.org/pypi/maixpy/)[![PyPI - Downloads](https://img.shields.io/pypi/dm/maixpy?label=pypi%20downloads)](https://pypi.org/project/maixpy/)[![GitHub downloads](https://img.shields.io/github/downloads/sipeed/maixpy/total?label=GitHub%20downloads)](https://github.com/sipeed/MaixPy) [![Build MaixCAM](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml)[![Trigger wiki](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml)

</div>

<div class="text-center">

English | [中文](/)

</div>


<div class="mt-16"></div>

> MaixPy-v1 (Maix-I K210) refer to <a target="_blank" href="https://wiki.sipeed.com/soft/maixpy/zh/">MaixPy-v1 doc</a>。 MaixPy v4 not support Maix-I Maix-II, please upgrade to [MaixCAM](https://wiki.sipeed.com/maixcam) 硬件平台。
> Give a star ⭐️ to [ MaixPy source code](https://github.com/sipeed/MaixPy) on GitHub to let us known you love it, and encourage us to add more features.


<div class="mt-6"></div>
<div id="id1" class="flex flex-row justify-start flex-wrap">
<div class="w-full">
<h2>Easy-to-use API, AI vision classify in 10 lines</h2>

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
    img.draw_string(10, 10, msg, image.COLOR_RED)
    dis.show(img)
```

</div>
<video playsinline controls autoplay loop muted preload  class="pl-6 pb-4 self-end" src="/static/video/classifier.mp4" type="video/mp4">
Classifier Result video
</video>
</div> <!-- id1 -->


<!-- div start-->
<div class="w-full">
<h2>Hardware peripheral control:</h2>
<div class="flex flex-row justify-start flex-wrap">
<div class="w-full mr-4">

Serial send and receive:

```python
from maix import uart

dvices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))
```

</div>
<div class="w-full">

I2C send and receive:

```python
from maix import i2c

devices = i2c.list_devices()
dev1 = i2c.I2C(devices[0], freq=100000)
slaves = dev1.scan()
print("find slaves:", slaves)
dev1.writeto(0x12, b'hello')
print("received:", dev1.readfrom(0x12, 5))
```

</div>
</div>
</div>
<!-- div end-->

<!-- start -->
<h2>MaixVision Workstation</h2>

Simplify the development environment, make development easier and faster:

<video playsinline controls muted preload src="/static/video/maixvision.mp4" type="video/mp4" style="height:20em;">
MaixVision
</video>

<h2>Online AI training platform MaixHub</h2>

One-click training AI model and deployment to MaixCAM even you have no AI knowledge and expensive training equipment.

<img style="height:20em;" src="/static/image/maixhub.jpg">

<!-- end -->

## Powerful MaixCAM hardware platform

![MaixCAM](/static/image/maixcam.png)

<br>

* **CPU**: 1GHz RISC-V(Linux)/ARM A53 + 700MHz RISC-V(RTOS) + 25~300MHz 8051(Low Power)
> Big core can choose one of RISC-V and ARM A53.
* **NPU**: 1Tops@INT8 NPU, support BF16, support YOLOv5 YOLOv8 etc.
* **Memory**: 256MB DDR3.
* **Connecting**: USB2.0/WiFi6/BLE5.4.
* **Peripheral**: IIC/PWM/SPI/UART/WDT/ADC
* **MultiMedia**: 4M Camera, 2.3" 552x368 Touchscreen, H.264/H.265/MJPEG codec.
* **Price**: [169/249 RMB](https://wiki.sipeed.com/store) (out of stock, please consult the store)

More detalils: [MaixCAM](https://wiki.sipeed.com/maixcam)

> Attention, only MaixCAM is supported, other boards with the same chip are not supported, including Sipeed's boards with the same chip, please be careful not to waste time and money by buying the wrong one.


<!-- feature 介绍 -->

<div id="feature">

## Features

Below are some of the features, for more please see the [documentation](/doc/en/index.html), [app store](https://maixhub.com/app) or community sharing [MaixHub](https://maixhub.com/share).

<div class="flex flex-wrap justify-between">
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/maixvision.mp4"></video>
            <p class="feature">Python + MaixVision IDE</p>
            <p class="description">Simple API, with hardware acceleration, including many libraries, such as numpy, opencv, MaixVision IDE programming</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/maixcdk.png">
            <p class="feature">C++ Version</p>
            <p class="description"><a href="https://github.com/sipeed/MaixCDK">MaixCDK</a> C++ version SDK，API the same as MaixPy's</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/serial_module.png">
            <p class="feature">As a serial module</p>
            <p class="description">Other MCU control by serial command</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/app_store.mp4"></video>
            <p class="feature">App Store</p>
            <p class="description">Share your APP to community, and one-click install <a href="https://maixhub.com/app">APPs</a>.</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/maixpy-v1-square.png">
            <p class="feature">MaixPy-v1 compatible package</p>
            <p class="description">Quickly migrate from MaixPy-v1(K210) to MaixPy-v4</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/classifier.mp4"></video>
            <p class="feature">AI Classifier</p>
            <p class="description">Classify object type</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/detector.mp4"></video>
            <p class="feature">AI Object Detection</p>
            <p class="description">Classify object type and position</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/face_recognize.jpg">
            <p class="feature">AI Face Recognition</p>
            <p class="description">Recognize different face</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/body_keypoint.jpg">
            <p class="feature">AI Body Keypoint Detection</p>
            <p class="description">Pose recognition, body sense game</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/self_learn_classifier.jpg">
            <p class="feature">AI Self Learning Classifier</p>
            <p class="description">No need to train on PC, learning any object on device in a flash</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/self_learn_tracker.mp4"></video>
            <p class="feature">AI Self Learning Detector</p>
            <p class="description">No need to train on PC, learning any object on device in a flash</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/object_track.jpg">
            <p class="feature">AI Object Tracking</p>
            <p class="description">Trajectory tracking, traffic statistics</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/monitor.jpg">
            <p class="feature">AI Monitor, Stream</p>
            <p class="description">Security monitor, can stream, even can live to platforms like Bilibili.com</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/find_blobs.mp4"></video>
            <p class="feature">Find Blobs</p>
            <p class="description">Find color blobs</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/line_track.mp4"></video>
            <p class="feature">Line Tracking</p>
            <p class="description">Car line tracking, logistics handling</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/qr_apriltag.mp4"></video>
            <p class="feature">QR Code and AprilTag</p>
            <p class="description">Recognize QR code and AprilTag</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/ocr.jpg">
            <p class="feature">OCR</p>
            <p class="description">Recognize characters in the image, digitize old items</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/voice_recognize.jpg">
            <p class="feature">Speech Recognition</p>
            <p class="description">Real-time continuous speech recognition</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/desktop_monitor.mp4"></video>
            <p class="feature">Desktop Monitor</p>
            <p class="description">Monitor PC information, such as CPU, memory, network, etc.</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/weather_station.jpg">
            <p class="feature">Weather Station</p>
            <p class="description">Monitor weather information, such as temperature, humidity, etc.</p>
        </div>
        <div>
        </div>
    </div>
        <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/thermal.jpg">
            <p class="feature">Thermal Camera</p>
            <p class="description">Optional camera, temperature image capture/measure</p>
        </div>
        <div>
        </div>
    </div>
        <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/hdmi_capture.jpg">
            <p class="feature">HDMI Capture Video</p>
            <p class="description">Optional, Capture HDMI image, as server monitor(KVM), external AI, streaming device etc.</p>
        </div>
        <div>
        </div>
    </div>
        <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/video_play.mp4"></video>
            <p class="feature">Big Screen Video Play</p>
            <p class="description">Many screen size choices(2.3" 2.4" 5" 7" etc.), hardware decode support</p>
        </div>
        <div>
        </div>
    </div>

</div>

</div>


## Who are using MaixPy?

* **AI Algorithm Engineer** who want to deploy your AI model to embedded devices.
> MaixPy provide easy-to-use API to access NPU, and docs to help you develop your AI model.
* **STEM** teacher who want to teach AI and embedded devices to students.
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

## Maix ecosystem

![](/static/image/maix_ecosystem.png)


## What difference between MaixPy v1, MaixPy3 and MaixPy v4?

* MaixPy v1 use MicroPython programming language, only support Sipeed Maix-I K210 series hardware, have limited third-party packages.
* MaixPy3 is designed for Sipeed Maix-II-Dock v831, not a long-term support version.
* MaixPy v4 use Python programming language, so there's much package we can use directly. MaixPy v4 support new hardware platforms of Sipeed, it's a long-term support version, the future's hardware platforms will support this version. MaixPy v4 have a MaixPy-v1 compatible API, so you can quickly migrate your MaixPy v1 project to MaixPy v4.

(MaixPy v4 Will not support Maix-I K210 series, if you are using Maix-I K210 series, it's recommended to upgrade hardware platform to use this to get more features and better performance.)

## License

All files in this repository are under the terms of the [Apache License 2.0 Sipeed Ltd.](./LICENSE) except the third-party libraries or have their own license.


## Community

* Project sharing: [maixhub.com/share](https://maixhub.com/share)
* Discussion: [maixhub.com/discussion](https://maixhub.com/discussion)
* QQ group: 862340358
* Telegram: [t.me/maixpy](https://t.me/maixpy)
