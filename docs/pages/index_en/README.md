---
title: MaixPy
id: home_page
---

<div>
<script src="/static/css/tailwind.css"></script>
</div>

<style>
h2 {
    font-size: 1.6em;
    font-weight: 600;
    font-weight: bold;
}
#page_wrapper
{
    background: #f2f4f3;
}
.dark #page_wrapper
{
    background: #1b1b1b;
}
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
h1 {
    font-size: 3em;
    font-weight: 600;
    margin-top: 0.67em;
    margin-bottom: 0.67em;
}
#page_content h2 {
    font-size: 1.6em;
    font-weight: 600;
    margin-top: 1em;
    margin-bottom: 0.67em;
    font-weight: bold;
    text-align: center;
    margin-top: 3em;
    margin-bottom: 1.5em;
}
#page_content h3 {
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
    border: 1em solid white;
    background: white;
    border-radius: 0.5em;
    overflow: hidden;
    max-width: 20em;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}
.dark .feature_item {
    border: 1em solid #2d2d2d;
    background: #2d2d2d;
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
.white_border {
    border: 1em solid white;
}
.dark .white_border {
    border: 1em solid #2d2d2d;
}
.code-toolbar pre {
    margin: 0;
}
.code_wrapper {
    overflow: auto;
}
@media screen and (min-width: 1280px) {
    .md_page #page_content > div
    {
        width: 1440px;
        max-width: 1440px;
    }
}
@media screen and (max-width: 768px) {
    .code_wrapper {
        font-size: 0.6em;
    }
}
</style>

<!-- wrapper -->
<div class="flex flex-col justify-center items-center">

<div class="w-full flex flex-col justify-center text-center">
    <div class="flex justify-center">
        <img src="/static/image/maixpy_banner.png" alt="MaixPy Banner">
    </div>
    <h1><span>MaixPy (v4)</span></h1>
    <h3>Fast implementation of AI vision and auditory applications</h3>
</div>

<div id="big_btn_wrapper" class="flex flex-wrap justify-center items-center">
    <a class="btn m-1" href="/doc/zh/index.html">Quick Start 🚀📖</a>
    <a class="btn m-1" href="/api/">API Reference 📚</a>
    <a class="btn m-1" target="_blank" href="https://wiki.sipeed.com/maixcam-pro">Hardware Platform: MaixCAM 📷</a>
    <a class="btn m-1" target="_blank" href="https://github.com/sipeed/maixpy">Open Source Code ⭐️</a>
    <a class="btn m-1" target="_blank" href="https://maixhub.com/app">App Store 📦</a>
</div>

<div id="tags">

[![GitHub Repo stars](https://img.shields.io/github/stars/sipeed/MaixPy?style=social)](https://github.com/sipeed/MaixPy)[![Apache 2.0](https://img.shields.io/badge/license-Apache%20v2.0-orange.svg)]("https://github.com/sipeed/MaixPy/blob/main/LICENSE.md)[![PyPI](https://img.shields.io/pypi/v/maixpy.svg)](https://pypi.python.org/pypi/maixpy/)[![PyPI - Downloads](https://img.shields.io/pypi/dm/maixpy?label=pypi%20downloads)](https://pypi.org/project/maixpy/)[![GitHub downloads](https://img.shields.io/github/downloads/sipeed/maixpy/total?label=GitHub%20downloads)](https://github.com/sipeed/MaixPy) [![Build MaixCAM](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml)[![Trigger wiki](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml)

</div>

<div class="text-center">

English | [中文](../)

</div>


<div class="mt-16"></div>

<img class="text-center" src="/static/image/maixcams.png">

<div class="mt-6"></div>

<div class="text-gray-400 text-center">

MaixPy-v1 (K210) usage refer to <a target="_blank" style="color: #546e7a" href="https://wiki.sipeed.com/soft/maixpy/zh/">MaixPy-v1</a>. MaixPy v4 does not support Maix-I Maix-II series hardware, please upgrade to the [MaixCAM](https://wiki.sipeed.com/maixcam-pro) platform.

If you like MaixPy, please give a star ⭐️ to the [MaixPy open source project](https://github.com/sipeed/MaixPy) to encourage us to develop more features.

</div>


<div class="mt-6"></div>

<h2 class="text-center font-bold">Simple API Design, AI Image Recognition with Just 10 Lines of Code</h2>
<div id="id1" class="flex flex-row justify-center items-end flex-wrap">
<div class="shadow-xl">

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

</div>
<video playsinline controls autoplay loop muted preload  class="p-0 mx-2 rounded-md shadow-xl white_border" src="/static/video/classifier.mp4" type="video/mp4">
Classifier Result video
</video>
</div> <!-- id1 -->


<!-- div start-->
<div class="text-center font-bold">
<h2>Hardware Peripheral Control, No Big Deal</h2>
<div class="flex flex-row justify-center flex-wrap">
<div class="mr-4 shadow-xl">

Serial Communication:

```python
from maix import uart

devices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))

```

</div>
<div class="shadow-xl">

I2C Communication:

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
<div class="flex flex-col justify-center items-center">
<h2>Convenient MaixVision Workstation</h2>
<p class="text-center">Simplify the development environment to make development easier and faster<p>

<div class="mt-3"></div>

<video playsinline controls muted preload src="/static/video/maixvision.mp4" type="video/mp4" class="p-0 mx-2 rounded-md shadow-xl white_border">
MaixVision
</video>

<h2>Online AI Training Platform MaixHub</h2>

No need for AI expertise or expensive training equipment, train models with one click, deploy to MaixCAM with one click.

<div class="mt-3"></div>

<img class="shadow-xl white_border" src="/static/image/maixhub.jpg">
</div>
<!-- end -->

## High-performance MaixCAM Hardware Platform

![MaixCAM](/static/image/maixcam_pro.png)

<br>

* **CPU**: 1GHz RISC-V (Linux) + 700MHz RISC-V (RTOS) + 25~300MHz 8051 (Low Power)
* **NPU**: 1Tops@INT8 NPU, supports BF16, YOLO11, YOLOv8, YOLOv5, etc.
* **Memory**: 256MB DDR3
* **Communication**: USB2.0/WiFi6/BLE5.4
* **Peripherals**: IIC/PWM/SPI/UART/WDT/GPIO/ADC
* **Multimedia**: 4M camera, 2.4" 640x480 HD capacitive touchscreen, H.264/H.265/MJPEG 2K hardware codec.
* **Purchase**: Various hardware versions are available, see [Store](https://wiki.sipeed.com/store) (contact the store for availability)
* **More**: See [MaixCAM](https://wiki.sipeed.com/maixcam) and [MaixCAM-Pro](https://wiki.sipeed.com/maixcam-pro) hardware documentation


<!-- feature introduction -->

<div id="feature" class="flex flex-col justify-center items-center">

## More Features

<div class="flex flex-col justify-center items-center">

Here are some feature highlights, find more in the [Community](#community)

You can create new features using the rich API provided by MaixPy.

</div>

<iframe style="width:100%;min-height:30em" src="https://www.youtube.com/embed/qV1lw0UVUYI?si=g3xUX5v3iT9r7RxJ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

<div class="flex flex-wrap justify-between">
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/opencv_openmv.jpg">
            <p class="feature">OpenCV + OpenMV</p>
            <p class="description">Supports OpenCV, compatible with OpenMV</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/maixcdk.png">
            <p class="feature">C++ Version</p>
            <p class="description"><a href="https://github.com/sipeed/MaixCDK">MaixCDK</a> C++ version SDK, same API as MaixPy, commercial-friendly</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/serial_module.png">
            <p class="feature">As a Serial Module</p>
            <p class="description">Control other MCUs via serial commands</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/app_store.mp4"></video>
            <p class="feature">APP Store</p>
            <p class="description">Share your apps with the community and install them with one click via the <a href="https://maixhub.com/app">APP Store</a>.</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/maixpy-v1-square.png">
            <p class="feature">MaixPy-v1 Compatible API</p>
            <p class="description">Quickly migrate from MaixPy-v1 (K210) to MaixPy-v4</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/classifier.mp4"></video>
            <p class="feature">AI Classification</p>
            <p class="description">Identify object categories</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/detector.mp4"></video>
            <p class="feature">AI Object Detection</p>
            <p class="description">Identify object categories and coordinates</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/face_recognize.jpg">
            <p class="feature">AI Face Recognition</p>
            <p class="description">Recognize different facial features</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/maixcam_face_landmarks.mp4"></video>
            <p class="feature">AI Face Landmarks</p>
            <p class="description">Detect face landmarks, replace face</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/body_keypoint.jpg">
            <p class="feature">AI Body Keypoint Detection</p>
            <p class="description">Posture recognition, body-sensing games</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/hands_landmarks.mp4"></video>
            <p class="feature">AI Hand keypoints</p>
            <p class="description">Detect hand keypoints and recognize gesture</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/self_learn_classifier.jpg">
            <p class="feature">AI Self-learning Classifier</p>
            <p class="description">Instantly learn any object on the device without PC training</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/self_learn_tracker.mp4"></video>
            <p class="feature">AI Self-learning Detector</p>
            <p class="description">Instantly learn any object on the device without PC training</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/tracker.mp4"></video>
            <p class="feature">AI Object Tracking</p>
            <p class="description">Track objects, count traffic</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/monitor.jpg">
            <p class="feature">AI Surveillance, Streaming</p>
            <p class="description">Security monitoring, streaming, even live stream to platforms like Bilibili.com</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/find_blobs.mp4"></video>
            <p class="feature">Color Detection</p>
            <p class="description">Detect color spots</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/line_track.mp4"></video>
            <p class="feature">Line Following</p>
            <p class="description">Line-following car, logistics transportation</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/qr_apriltag.mp4"></video>
            <p class="feature">QR Code and AprilTag</p>
            <p class="description">Recognize QR codes and AprilTag</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/ocr.jpg">
            <p class="feature">OCR</p>
            <p class="description">Recognize characters in images, digitize old items</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/voice_recognize.jpg">
            <p class="feature">Voice Recognition</p>
            <p class="description">Real-time continuous voice recognition</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/desktop_monitor.mp4"></video>
            <p class="feature">Desktop Monitor</p>
            <p class="description">Monitor PC information such as CPU, memory, and network.</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/weather_station.jpg">
            <p class="feature">Weather Station</p>
            <p class="description">Monitor weather information such as temperature and humidity.</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/thermal.jpg">
            <p class="feature">Thermal Infrared Camera</p>
            <p class="description">Optional camera, for temperature image acquisition/measurement</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/hdmi_capture.jpg">
            <p class="feature">HDMI Video Capture</p>
            <p class="description">Optional feature, capture images via HDMI for server monitoring (KVM), remote control, external AI, streaming devices, etc.</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/video_play.mp4"></video>
            <p class="feature">Large Screen Video Playback</p>
            <p class="description">Multiple screen sizes (2.3", 2.4", 5", 7", etc.), hardware decoding support</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/microscope.mp4"></video>
            <p class="feature">Microscope</p>
            <p class="description">Pair with 1/8" large sensor + microscope lens = digital microscope</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/global_shutter.jpg">
            <p class="feature">High-Speed Recognition</p>
            <p class="description">Pair with a global shutter camera to accurately recognize high-speed moving objects</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/time_lapse.mp4"></video>
            <p class="feature">Time-lapse Photography</p>
            <p class="description">Pair with a 1/8" large sensor for all-day time-lapse photography</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/capture_sky.jpg">
            <p class="feature">Astronomical Photography</p>
            <p class="description">Pair with a 1/8" large sensor + high-power lens for astronomical photography, supports long exposure mode and RAW image output</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/gyroflow.mp4"></video>
            <p class="feature">Gyroscope Stabilization</p>
            <p class="description">Onboard gyroscope (MaixCAM-Pro only), supports exporting gyroflow stabilization format for DIY photography</p>
        </div>
        <div>
        </div>
    </div>
</div>

</div>

## Who Uses MaixPy?

<div>

* **AI Algorithm Engineers**: Easily deploy your AI models to embedded devices.
> Easy-to-use API to access NPU, open-source quantization tools, detailed documentation on AI models.

* **STEM**: Teachers who want to teach students AI and embedded development.
> Easy-to-use API, PC tools, online AI training services, allowing you to focus on teaching AI instead of hardware and complex software development.

* **Makers**: Want to create cool projects without spending too much time on complex hardware and software.
> Rich, simple Python and C++ APIs, quick to get started, complete your DIY projects in just minutes.

* **Engineers**: Want to build projects but hope to have prototypes and solutions quickly.
> Rich Python and C++ APIs, efficient, stable, and easy to use, helping you quickly create prototypes and implement projects directly.

* **Students**: Want to learn AI and embedded development.
> Offers rich documentation, tutorials, and open-source code, helping you find learning paths and gradually grow, from simple Python programming to vision, AI, audio, Linux, RTOS, etc.

* **Companies**: Want to develop AI vision products but don’t have the time or engineers to develop complex embedded systems.
> Use MaixPy or even graphical programming to reduce the number of employees and time. For example, adding an AI QA system to the production line, or an AI security monitor to the office.

* **Competitors**: People who want to win competitions.
> MaixPy integrates many features, is easy to use, speeds up the output of your work, and helps you win competitions in a short time. Many students use MaixPy to win common competitions in China.

</div>

## Performance Comparison

Compared to the limited NPU operator support and memory constraints of the previous two generations of Maix series products (K210, V831), MaixCAM offers significant improvements in performance and experience while maintaining an excellent price-performance ratio.

<div class="mt-3"></div>

<div>

| Feature | Maix-I K210 | Maix-II v831 | MaixCAM |
| ------- | ----------- | ------------ | ------- |
| CPU | 400MHz RISC-V x2 | 800MHz ARM7 | **1GHz RISC-V(Linux)<br>700MHz RISC-V(RTOS)<br>25~300MHz 8051(Low Power)** |
| Memory | 6MB SRAM | 64MB DDR2 | **256MB DDR3** |
| NPU | 0.25Tops@INT8<br>official says 1T but... | 0.25Tops@INT8 | **1Tops@INT8** |
| Encoder | ✖ | 1080p@30fps | **2K@30fps** |
| Screen | 2.4" 320x240 | 1.3" 240x240 | **2.3" 552x368**(MaixCAM)<br/>**2.4" 640x480**(MaixCAM-Pro)<br/>5" 1280x720<br/>7" 1280x800<br/>10“ 1280x800|
| Touchscreen | ✖ | ✖ | **2.3" 552x368** |
| Camera | 30W | 200W | **500W** |
| WiFi   | 2.4G | 2.4G | **WiFi6** 2.4G/5G |
| USB    | ✖    | **USB2.0** | **USB2.0** |
| Ethernet    | ✖    | 100M(optional)   | 100M(optional) |
| SD Card Interface | SPI | **SDIO** | **SDIO** |
| BLE    | ✖    | ✖      | **BLE5.4** |
| Operating System     | RTOS | Tina Linux | **Linux + RTOS** |
| Programming Language | C / C++ / MicroPython | C / C++ / **Python3** | C / **C++ / Python3** |
| Software | MaixPy | MaixPy3 | **MaixCDK + MaixPy v4 + OpenCV + Numpy + ...**|
| PC Software | MaixPy IDE | MaixPy3 IDE | **MaixVision** Workstation |
| Documentation   | ⭐️⭐️⭐️⭐️ |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |
| Online AI Training | ⭐️⭐️⭐️ |  ⭐️⭐️⭐️⭐️ |  🌟🌟🌟🌟🌟 |
| Official Apps   | ⭐️   |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |
| AI Classification (224x224) | MobileNetv1 50fps<br>MobileNetv2 ✖<br>Resnet ✖ | MobileNet ✖<br>Resnet18 20fps<br>Resnet50 ✖| MobileNetv2 **130fps**<br>Resnet18 **62fps**<br>Resnet50 **28fps** |
| AI Detection (NPU inference part)   | YOLOv2(224x224) 15fps |  YOLOv2(224x224) 15fps |  **YOLOv5s(224x224) 100fps<br>YOLOv5s(320x256) 70fps<br>YOLOv5s(640x640) 15fps<br>YOLOv8n(640x640) 23fps<br>YOLO11n(224x224)175fps<br>YOLO11n(320x224)120fps<br>YOLO11n(320x320)95fps<br>YOLO11n(640x640)23fps**|
| Ease of Use     | ⭐️⭐️⭐️⭐️ |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |

<div class="mt-6"></div>

<div>

**MaixCAM-Pro** Upgrades compared to MaixCAM:
1. Optimized case design for better aesthetics and heat dissipation
2. Screen upgraded to 2.4 inches with 640x480 resolution
3. Dual-channel PWM servo interface, standard PMOD interface, 6-pin terminal interface
4. Onboard AXP2101 PMU, supports lithium battery charging and discharging, power metering function
5. Onboard six-axis IMU, qmi8658, supports video stabilization
6. Built-in 1W small speaker
7. Added 1/4 inch standard thread mount for easy installation
8. Added auxiliary lighting LED
9. Added RTC chip BM8653 and RTC battery

</div>

</div>

## Maix Ecosystem

<img src="/static/image/maix_ecosystem.png" class="white_border shadow-xl rounded-md">


## Community {#community}

<div>

| Community | Address |
| --- | ---- |
| **Documentation**| [MaixPy Documentation](/doc/en/index.html) |
| **App Store**| [maixhub.com/app](https://maixhub.com/app) |
| **Project Sharing**| [maixhub.com/share](https://maixhub.com/share) |
| **Bilibili**| Search for `MaixCAM` or `MaixPy` on Bilibili |
| **Discussion**| [maixhub.com/discussion](https://maixhub.com/discussion) |
| **MaixPy issues**| [github.com/sipeed/MaixPy/issues](https://github.com/sipeed/MaixPy/issues) |
| **Telegram**| [t.me/maixpy](https://t.me/maixpy) |
| **QQ Group**| 862340358 |

</div>


## What Are the Differences Between MaixPy v1, MaixPy3, and MaixPy v4?

<div class="flex flex-col items-center justify-center">

* MaixPy v1 uses the MicroPython programming language and only supports the Sipeed Maix-I K210 series hardware with limited third-party packages.
* MaixPy3 is specifically designed for Sipeed Maix-II-Dock v831 and is not a long-term support version.
* MaixPy v4 uses the Python programming language, allowing direct use of many packages.<br/>MaixPy v4 supports Sipeed's new hardware platform and is a long-term support version. Future hardware platforms will support this version.<br>MaixPy v4 has a MaixPy-v1 compatible API, so you can quickly migrate your MaixPy v1 projects to MaixPy v4.

(MaixPy v4 does not support the K210 series. It is recommended to upgrade your hardware platform to use this version for more features, better performance,<br/>and a more convenient programming experience.)

</div>

</div>
<!-- wrapper end -->
