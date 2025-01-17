
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
.biliiframe {
    width: 100%;
    min-height: 40em;
    border-radius: 0.5em;
    border: 1em solid white;
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
    .biliiframe {
        width: 100%;
        min-height: 20em;
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
    <h3>极速落地 AI 视觉、听觉应用</h3>
</div>

<div id="big_btn_wrapper" class="flex flex-wrap justify-center items-center">
    <a class="btn m-1" href="/doc/zh/index.html">快速开始 🚀📖</a>
    <a class="btn m-1" href="/api/">API 参考 📚</a>
    <a class="btn m-1" target="_blank" href="https://wiki.sipeed.com/maixcam-pro">硬件平台：MaixCAM 📷</a>
    <a class="btn m-1" target="_blank" href="https://github.com/sipeed/maixpy">开源代码 ⭐️</a>
    <a class="btn m-1" target="_blank" href="https://maixhub.com/app">应用商店 📦</a>
</div>

<div id="tags">

[![GitHub Repo stars](https://img.shields.io/github/stars/sipeed/MaixPy?style=social)](https://github.com/sipeed/MaixPy)[![Apache 2.0](https://img.shields.io/badge/license-Apache%20v2.0-orange.svg)]("https://github.com/sipeed/MaixPy/blob/main/LICENSE.md)[![PyPI](https://img.shields.io/pypi/v/maixpy.svg)](https://pypi.python.org/pypi/maixpy/)[![PyPI - Downloads](https://img.shields.io/pypi/dm/maixpy?label=pypi%20downloads)](https://pypi.org/project/maixpy/)[![GitHub downloads](https://img.shields.io/github/downloads/sipeed/maixpy/total?label=GitHub%20downloads)](https://github.com/sipeed/MaixPy) [![Build MaixCAM](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/build_maixcam.yml)[![Trigger wiki](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml/badge.svg)](https://github.com/sipeed/MaixPy/actions/workflows/trigger_wiki.yml)

</div>

<div class="text-center">

[English](./en/) | 中文

</div>


<div class="mt-16"></div>

<img class="text-center" src="/static/image/maixcams.png">

<div class="mt-6"></div>

<div class="text-gray-400 text-center">

MaixPy-v1 (K210) 用户请查看 <a target="_blank" style="color: #546e7a" href="https://wiki.sipeed.com/soft/maixpy/zh/">MaixPy-v1 文档</a>。 MaixPy v4 不支持 Maix-I Maix-II 系列硬件，请更新到 [MaixCAM](https://wiki.sipeed.com/maixcam-pro) 硬件平台。

喜欢 MaixPy 请给 [ MaixPy 开源项目](https://github.com/sipeed/MaixPy) 点个 Star ⭐️ 以鼓励我们开发更多功能。

</div>


<div class="mt-6"></div>

<h2 class="text-center font-bold">简易的 API 设计， 10 行代码进行 AI 图像识别</h2>
<div id="id1" class="flex flex-row justify-center items-end flex-wrap max-w-full">
<div class="shadow-xl code_wrapper">

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
<h2>硬件外设控制，不在话下</h2>
<div class="flex flex-row justify-center flex-wrap max-w-full">
<div class="mr-4 shadow-xl code_wrapper">

串口收发：

```python
from maix import uart

devices = uart.list_devices()

serial = uart.UART(devices[0], 115200)
serial.write_str("hello world")
print("received:", serial.read(timeout = 2000))

```

</div>
<div class="shadow-xl code_wrapper">

I2C 收发：

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
<h2>便捷的 MaixVision 工作站</h2>
<p class="text-center">简化开发环境，让开发更简单快速<p>

<div class="mt-3"></div>

<video playsinline controls muted preload src="/static/video/maixvision.mp4" type="video/mp4" class="p-0 mx-2 rounded-md shadow-xl white_border">
MaixVision
</video>

<h2>在线 AI 训练平台 MaixHub</h2>

无需 AI 基础和昂贵的训练设备，一键训练模型，一键部署到 MaixCAM

<div class="mt-3"></div>

<img class="shadow-xl white_border" src="/static/image/maixhub.jpg">
</div>
<!-- end -->

## 性能强劲 MaixCAM 硬件平台

![MaixCAM](/static/image/maixcam_pro.png)

<br>

* **CPU**: 1GHz RISC-V(Linux) + 700MHz RISC-V(RTOS) + 25~300MHz 8051(Low Power)
* **NPU**: 1Tops@INT8 NPU, 支持 BF16，支持 YOLO11、 YOLOv8、 YOLOv5 等。
* **内存**: 256MB DDR3。
* **通信**: USB2.0/WiFi6/BLE5.4。
* **外设**: IIC/PWM/SPI/UART/WDT/GPIO/ADC
* **多媒体**：4M 摄像头，2.4" 640x480 高清电容触摸屏，H.264/H.265/MJPEG 2K 硬件编解码。
* **购买**: 有各种版本硬件提供, 详情查看[商城](https://wiki.sipeed.com/store) （缺货时咨询店家）
* **更多**: 请看 [MaixCAM](https://wiki.sipeed.com/maixcam) 和 [MaixCAM-Pro](https://wiki.sipeed.com/maixcam-pro) 硬件文档


<!-- feature 介绍 -->

<div id="feature" class="flex flex-col justify-center items-center">

## 更多特性

<div class="flex flex-col justify-center items-center w-full">

以下为部分功能简介，更多到[社区](#community)找到更多

基于 MaixPy 提供的丰富 API 可以创造出更多新功能

<iframe src="//player.bilibili.com/player.html?isOutside=true&aid=113485669204279&bvid=BV1ncmRYmEDv&cid=26768769718&p=1" scrolling="no" border="0" frameborder="no" framespacing="0" allowfullscreen="true" class="biliiframe"></iframe>

</div>

<div class="flex flex-wrap justify-between">
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/opencv_openmv.jpg">
            <p class="feature">OpenCV + OpenMV</p>
            <p class="description">支持 OpenCV， 兼容 OpenMV</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/maixcdk.png">
            <p class="feature">C++版本</p>
            <p class="description"><a href="https://github.com/sipeed/MaixCDK">MaixCDK</a> C++版本的SDK，与MaixPy的API相同, 商业友好</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/serial_module.png">
            <p class="feature">作为串口模块</p>
            <p class="description">其它 MCU 通过串口命令控制</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/app_store.mp4"></video>
            <p class="feature">APP商店</p>
            <p class="description">将您的APP分享给社区，并一键安装<a href="https://maixhub.com/app">APPs</a>。</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/maixpy-v1-square.png">
            <p class="feature">提供 MaixPy-v1 兼容 API</p>
            <p class="description">快速从MaixPy-v1(K210)迁移到MaixPy-v4</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/classifier.mp4"></video>
            <p class="feature">AI 分类</p>
            <p class="description">识别物体类别</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/detector.mp4"></video>
            <p class="feature">AI 对象检测</p>
            <p class="description">识别物体类别和坐标</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/face_recognize.jpg">
            <p class="feature">AI 人脸识别</p>
            <p class="description">识别不同人脸特征</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/maixcam_face_landmarks.mp4"></video>
            <p class="feature">AI 人脸关键点</p>
            <p class="description">检测人脸关键点，面部特征/动作识别，AI 换脸</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/body_keypoint.jpg">
            <p class="feature">AI 人体关键点检测</p>
            <p class="description">姿态识别、体感游戏</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/hands_landmarks.mp4"></video>
            <p class="feature">AI 手部关键点</p>
            <p class="description">检测手部关键点，手势识别</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/self_learn_classifier.jpg">
            <p class="feature">AI 自学习分类器</p>
            <p class="description">无需在PC上训练，在设备上瞬间学习任意物体</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/self_learn_tracker.mp4"></video>
            <p class="feature">AI 自学习检测器</p>
            <p class="description">无需在PC上训练，在设备上瞬间学习任意物体</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/tracker.mp4"></video>
            <p class="feature">AI 物体轨迹跟踪</p>
            <p class="description">轨迹追踪，流量统计</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/monitor.jpg">
            <p class="feature">AI 监控，串流</p>
            <p class="description">安防监控，可串流，甚至可以向直播平台 比如 Bilibili.com 直播</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/find_blobs.mp4"></video>
            <p class="feature">查找颜色</p>
            <p class="description">查找颜色斑点</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/line_track.mp4"></video>
            <p class="feature">巡线</p>
            <p class="description">小车巡线，物流搬运</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/qr_apriltag.mp4"></video>
            <p class="feature">QR码和AprilTag</p>
            <p class="description">识别QR码和AprilTag</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/ocr.jpg">
            <p class="feature">OCR</p>
            <p class="description">识别图片中的字符，旧物数字化</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/voice_recognize.jpg">
            <p class="feature">语音识别</p>
            <p class="description">实时连续语音识别</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/desktop_monitor.mp4"></video>
            <p class="feature">桌面监视器</p>
            <p class="description">监视PC信息，如CPU，内存，网络等。</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/weather_station.jpg">
            <p class="feature">天气站</p>
            <p class="description">监视天气信息，如温度，湿度等。</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/thermal.jpg">
            <p class="feature">热红外摄像头</p>
            <p class="description">选配摄像头，温度图像获取/测量</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/hdmi_capture.jpg">
            <p class="feature">HDMI 捕获视频</p>
            <p class="description">选配，通过 HDMI 捕获图像，作为服务器监控（KVM）和远程控制、外接 AI、推流设备等</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/video_play.mp4"></video>
            <p class="feature">大屏视频播放</p>
            <p class="description">多种规格屏幕选择(2.3" 2.4" 5" 7"等), 硬件解码支持</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/microscope.mp4"></video>
            <p class="feature">显微镜</p>
            <p class="description">搭配1/8"大底传感器 + 显微镜头 = 数字显微镜</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/global_shutter.jpg">
            <p class="feature">高速识别</p>
            <p class="description">搭配全局摄像头，高速运动物体也能准确识别</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/time_lapse.mp4"></video>
            <p class="feature">延时摄影</p>
            <p class="description">搭配1/8"大底传感器实现全天候延时摄影</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <img src="/static/image/capture_sky.jpg">
            <p class="feature">天文摄影</p>
            <p class="description">搭配1/8"大底传感器+高倍镜头实现天文摄影，支持长曝光模式和RAW 图输出</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/gyroflow.mp4"></video>
            <p class="feature">陀螺仪增稳</p>
            <p class="description">板载陀螺仪(仅MaixCAM-Pro) 支持导出 gyroflow 防抖格式，DIY 摄影</p>
        </div>
        <div>
        </div>
    </div>
</div>

</div>

## 谁在用 MaixPy？

<div>

* **AI 算法工程师**： 轻松将你的 AI 模型部署到嵌入式设备。
> 易用的 API 访问 NPU，开源量化工具，详细的 AI 模型的文档。

* **STEM**：想要教学生 AI 和嵌入式开发的老师。
> 易用的 API，PC 工具，在线 AI 训练服务等，让你专注于教授 AI，而不是硬件和复杂的软件开发。

* **创客**: 想要制作一些酷炫的项目，但不想把事件浪费在太复杂的硬件和软件。
> Python 和 C++ 丰富简易 API，快速上手，甚至可以在几分钟内完成你的 DIY 项目。

* **工程师**: 想要做一些项目，但希望尽快有原型和落地。
> Python 和 C++ 丰富 API，高效稳定易使用，助力快速出原型及直接落地项目。

* **学生**： 想要学习 AI，嵌入式开发。
> 提供丰富文档和教程和开源代码，帮助你找到学习路线，并逐步成长。从简单的 Python 编程到视觉，AI，音频，Linux，RTOS等。

* **企业**: 想要开发 AI 视觉产品，但没有时间或工程师来开发复杂的嵌入式系统。
> 使用 MaixPy 甚至图形编程来，用更少的员工和时间。例如，向生产线添加 AI QA 系统，或为办公室添加一个 AI 安全监控器。

* **竞赛者**: 想要赢得比赛的比赛人们。
> MaixPy 集成了许多功能，易于使用，加快你作品产出速度，助力有限时间内赢得比赛，国内常见比赛都有很多同学使用 MaixPy 赢得比赛。

</div>

## 性能对比

相比上两代 Maix 系列产品(K210, V831)有限的 NPU 算子支持和内存限制，MaixCAM 在保持超高性价比的同时，性能和体验有了很大的提升。

<div class="mt-3"></div>

<div class="max-w-full">

<div class="overflow-auto">

| 特征 | Maix-I K210 | Maix-II v831 | MaixCAM |
| ------- | ----------- | ------------ | ------- |
| CPU | 400MHz RISC-V x2 | 800MHz ARM7 | **1GHz RISC-V(Linux)<br>700MHz RISC-V(RTOS)<br>25~300MHz 8051(Low Power)** |
| 内存 | 6MB SRAM | 64MB DDR2 | **256MB DDR3** |
| NPU | 0.25Tops@INT8<br>official says 1T but... | 0.25Tops@INT8 | **1Tops@INT8** |
| Encoder | ✖ | 1080p@30fps | **2K@30fps** |
| 屏幕 | 2.4" 320x240 | 1.3" 240x240 | **2.3" 552x368**(MaixCAM)<br/>**2.4" 640x480**(MaixCAM-Pro)<br/>5" 1280x720<br/>7" 1280x800<br/>10“ 1280x800|
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
| 官方应用   | ⭐️   |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |
| AI 分类(224x224) | MobileNetv1 50fps<br>MobileNetv2 ✖<br>Resnet ✖ | MobileNet ✖<br>Resnet18 20fps<br>Resnet50 ✖| MobileNetv2 **130fps**<br>Resnet18 **62fps**<br>Resnet50 **28fps** |
| AI 检测(NPU推理部分)   | YOLOv2(224x224) 15fps |  YOLOv2(224x224) 15fps |  **YOLOv5s(224x224) 100fps<br>YOLOv5s(320x256) 70fps<br>YOLOv5s(640x640) 15fps<br>YOLOv8n(640x640) 23fps<br>YOLO11n(224x224)175fps<br>YOLO11n(320x224)120fps<br>YOLO11n(320x320)95fps<br>YOLO11n(640x640)23fps**|
| 易用性     | ⭐️⭐️⭐️⭐️ |  ⭐️⭐️⭐️   |  🌟🌟🌟🌟🌟 |

</div>

<div class="mt-6"></div>

<div>

**MaixCAM-Pro** 相比 MaixCAM 的升级点：
1. 优化外壳设计，更美观，散热更好
2. 屏幕升级到2.4寸 640x480分辨率
3. 板载双路PWM舵机接口，标准PMOD接口，6pin端子接口
4. 板载AXP2101 PMU，支持锂电池充放电，电量计功能
5. 板载六轴IMU，qmi8658，可支持视频防抖
6. 内置1W小喇叭
7. 增加1/4英寸标准螺纹口，便于安装
8. 增加辅助照明LED
9. 增加RTC芯片 BM8653 和 RTC电池

</div>

</div>

## Maix 生态

<img src="/static/image/maix_ecosystem.png" class="white_border shadow-xl rounded-md">


## 社区 {#community}

<div class="max-w-full">
<div class="overflow-auto">

| 社区 | 地址 |
| --- | ---- |
| **文档**| [MaixPy 文档](/doc/zh/index.html) |
| **应用商店**| [maixhub.com/app](https://maixhub.com/app) |
| **项目分享**| [maixhub.com/share](https://maixhub.com/share) |
| **Bilibili**| B站搜索 `MaixCAM` 或者 `MaixPy` |
| **讨论**| [maixhub.com/discussion](https://maixhub.com/discussion) |
| **MaixPy issues**| [github.com/sipeed/MaixPy/issues](https://github.com/sipeed/MaixPy/issues) |
| **Telegram**| [t.me/maixpy](https://t.me/maixpy) |
| **QQ 群**| 862340358 |

</div>
</div>


## MaixPy v1, MaixPy3 and MaixPy v4 有什么区别？

<div class="flex flex-col items-center justify-center">

* MaixPy v1 使用 MicroPython 编程语言，仅支持 Sipeed Maix-I K210 系列硬件，有限的第三方包。
* MaixPy3 专为 Sipeed Maix-II-Dock v831 设计，不是长期支持版本。
* MaixPy v4 使用 Python 编程语言，因此我们可以直接使用许多包。<br/>MaixPy v4 支持 Sipeed 的新硬件平台，这是一个长期支持版本，未来的硬件平台将支持这个版本。<br>MaixPy v4 有一个 MaixPy-v1 兼容的 API，所以你可以快速将你的 MaixPy v1 项目迁移到 MaixPy v4。

(MaixPy v4 不支持 K210 系列，建议升级硬件平台以使用此版本，以获得更多功能和更好的性能和更方便的编程体验。)

</div>

</div>
<!-- wrapper end -->

