
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
.strong2 {
    font-weight: bolder;
    color: #c33d45;
}
.sub_items {
    margin-left: 1em;
}
.main_items {
    margin-top: 1em;
}
.comment {
    font-size: 0.7em;
    color: gray;
}
.right {
    text-align: right;
}
.second {
    font-size: 0.9em;
}
    #page_content .h1 {
        font-size: 2.2em;
        font-weight: 800;
    }
    .flex_center {
        display:flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    #page_content .card_item {
        color: #f0f5f9;
        background: linear-gradient(90deg, #26d0ce, #1a2980);
        border-radius: 1em;
        padding: 1em;
        margin: 1em 0.1em;
    }
    #page_content .card_item img {
        transition: transform 0.4s ease;
    }
    #page_content .item2 {
        width: 90%;
        align-self: start;
        background: linear-gradient(-45deg, #c471ed,  #f64f59);
    }
    #page_content .item3 {
        width: 90%;
        align-self: end;
        background: linear-gradient(-45deg, #12c2e9, #c471ed);
    }
    #page_content .card_item:visited {
        color: #f0f5f9;
    }
    #page_content .card_item:hover {
        border-radius: 1em;
        background: linear-gradient(70deg, #26d0ce, #1a2980);
        padding: 1em;
        margin: 1em 0.1em;
    }
    #page_content .item2:hover {
        background: linear-gradient(-20deg, #c471ed,  #f64f59);
    }
    #page_content .item3:hover {
        background: linear-gradient(-20deg, #12c2e9, #c471ed);
    }
    #page_content .card_item:hover > img {
        transform: rotate(10deg) scale(1.3) ;
    }
    .cams_wrapper {
        width: 70%;
    }
    .mask_wrapper {
        position: relative;
    }
    .mask {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    .item_name {
        font-size: larger;
        font-weight: 800;
    }
    #page_content .btn_blue {
        margin: 1em;
        color: white;
        font-size: 0.9em;
        border-radius: 0.3em;
        padding: 0.5em 2em;
        background-color: #0b4294;
    }
    #page_content .btn_blue:visited {
        color: white;
    }
    #page_content .btn_blue:hover {
        margin: 1em;
        color: white;
        font-size: 0.9em;
        border-radius: 0.3em;
        padding: 0.5em 2em;
        background-color: #082a5e;
    }
    #page_content .btn_red {
        margin: 1em;
        color: white;
        font-size: 0.9em;
        border-radius: 0.3em;
        padding: 0.5em 2em;
        background-color: #ad3838
    }
    #page_content .btn_red:visited {
        color: white;
    }
    #page_content .btn_red:hover {
        margin: 1em;
        color: white;
        font-size: 0.9em;
        border-radius: 0.3em;
        padding: 0.5em 2em;
        background-color: #630606;
    }

    .dark #page_content .card_item {
        color: #f0f5f9;
    }
    .dark #page_content a.card_item:visited {
        color: #f0f5f9;
    }
    .dark .card_item {
        background: #292929;
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
    .cams_wrapper {
        width: 100%;
    }
    #page_content .item1 {
        flex-direction: column-reverse;
    }
    #page_content .item1 img {
        padding-bottom: 1em;
    }
    #page_content .item2 {
        width: 98%;
    }
    #page_content .item3 {
        width: 98%;
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
    <a class="btn m-1" target="_blank" href="https://wiki.sipeed.com/maixcam">硬件平台：MaixCAM 📷</a>
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

<br>

目前有`MaixCAM / MaixCAM-Pro` 和 `MaixCAM2` 两代硬件产品，从性能、配件、外观提供不同选择

后文有性能对比



<div class="flex_center cams_wrapper">
    <div class="flex flex-row w-full">
        <a href="https://wiki.sipeed.com/maixcam2" target="_blank" class="flex flex-row items-center justify-around w-full card_item mask_wrapper item1">
            <div class="item_name">MaixCAM2</div>
            <img src="https://wiki.sipeed.com/static/image/maixcam2_small.png">
            <div class="mask"></div>
        </a>
    </div>
    <div class="flex flex-row w-full justify-between">
        <div class="flex_center flex-row justify-start w-1/2">
            <a href="https://wiki.sipeed.com/hardware/zh/maixcam/maixcam.html" target="_blank" class="flex_center card_item mask_wrapper item2">
                <img src="https://wiki.sipeed.com/static/image/maixcam_small.png">
                <div class="item_name pt-8">MaixCAM</div>
                <div class="mask"></div>
            </a>
        </div>
        <div class="flex_center flex-row justify-end w-1/2">
            <a href="https://wiki.sipeed.com/maixcam-pro" target="_blank" class="flex_center card_item mask_wrapper item3">
                <img src="https://wiki.sipeed.com/static/image/maixcam_pro_small.png">
                <div class="item_name pt-8">MaixCAM-Pro</div>
                <div class="mask"></div>
            </a>
        </div>
    </div>
</div>




<!-- feature 介绍 -->

<div id="feature" class="flex flex-col justify-center items-center">

## 部分功能展示

<div class="flex flex-col justify-center items-center w-full">

以下为部分功能简介，更多到[社区](#community)找到更多

基于 MaixPy 提供的丰富 API 可以创造出更多新功能

(LLM/VLM 相关只 MaixCAM2 支持)

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
            <video playsinline controls autoplay loop muted preload src="/static/video/face_recognition.mp4"></video>
            <p class="feature">AI 人脸识别</p>
            <p class="description">识别不同人脸特征，表情识别等</p>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/keypoints.mp4"></video>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/self_learn_classifier.mp4"></video>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/streaming.mp4"></video>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/ocr.mp4"></video>
            <p class="feature">OCR</p>
            <p class="description">识别图片中的字符，旧物数字化</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/depth_anything_v2.mp4"></video>
            <p class="feature">单目深度估计</p>
            <p class="description">单目摄像头估计深度</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/asr.mp4"></video>
            <p class="feature">语音识别</p>
            <p class="description">实时连续语音识别</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/tts.mp4"></video>
            <p class="feature">语音合成</p>
            <p class="description">TTS生成语音，支持多种语言</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/llm.mp4"></video>
            <p class="feature">离线大语言模型LLM</p>
            <p class="description">玩全离线跑大语言模型LLM</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/vlm.mp4"></video>
            <p class="feature">离线视觉大语言模型VLM</p>
            <p class="description">玩全离线跑视觉大语言模型VLM</p>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/sky.mp4"></video>
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
            <p class="description">板载陀螺仪，支持导出 gyroflow 防抖格式，DIY 摄影</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/tof.mp4"></video>
            <p class="feature">TOF 配件深度测量</p>
            <p class="description">搭配 TOF 模块实现精准深度测量</p>
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

这里列出比较重要的软硬件性能参数供选型参考。

<div class="mt-3"></div>

<div class="max-w-full">

<div class="overflow-auto">

| 特征      | Maix-I K210 | MaixCAM | MaixCAM2 |
| --------- | ----------- | ------- | ------- |
| CPU       | 400MHz RISC-V x2 |  **1GHz RISC-V(Linux)<br>700MHz RISC-V(RTOS)<br>25~300MHz 8051(Low Power)** | <span class="strong2">1.2GHz A53 x2(Linux)</span><br>RISC-V 32bit E907(RTT) |
| 内存      | 6MB SRAM         | **256MB DDR3** | <span class="strong2">1GB / 4GB LPDDR4</span> |
| NPU       | 0.25Tops@INT8<br>official says 1T but... | **1Tops@INT8** | <span class="strong2">3.2Tops@INT8</span> |
| Encoder   | ❌               | **2880x1620@30fps H.254/H.265/JPEG** | <span class="strong2">3840*2160@30fps H.254/H.265/JPEG</span> |
| Decoder   | ❌               | **2880x1620@30fps H.264/JPEG** | **1080p@60fps H.264/JPEG** |
| 屏幕      | 2.4" 320x240     | **2.3" 552x368**(MaixCAM)<br/>**2.4" 640x480**(MaixCAM-Pro)<br/>5" 1280x720<br/>7" 1280x800<br/>10“ 1280x800| **2.4" 640x480**<br/>5" 1280x720<br/>7" 1280x800<br/>10“ 1280x800 |
| 触摸屏    | ❌               | **2.3" 552x368**/**2.4" 640x480** | **2.4" 640x480** |
| 摄像头    | 30W              | **500W(5M)** | <span class="strong2">800W(8M)</span> |
| AI ISP    | ❌               | ❌           | <span class="strong2">✅</span> |
| WiFi      | 2.4G             | **WiFi6** 2.4G/5G | **WiFi6** 2.4G/5G |
| BLE       | ❌               | **BLE5.4** | **BLE5.4** |
| USB       | ❌               | **USB2.0** | **USB2.0** |
| 以太网    | ❌               | 100M(选配) | <span class="strong2">100M(板载FPC, 可外接转RJ45模块)</span> |
| SD 卡接口 | SPI              | **SDIO** | **SDIO** |
| 操作系统  | RTOS             | **Linux(BuildRoot) + RTOS** | Linux(<span class="strong2">Ubuntu</span>) + RTT |
| 编程语言  | C / C++ / MicroPython | C / **C++ / Python3** | C / **C++ / Python3** |
| 软件包    | MaixPy-v1             | **MaixCDK + MaixPy v4<br>+ opencv + numpy + ...**<br>纯Python包或者手动交叉编译 | **MaixCDK + MaixPy v4<br>+ opencv + numpy + scipy + ...**<br><span class="strong2">大量AArch64预编译包直接安装，支持板上编译和交叉编译</span> |
| PC 软件   | MaixPy IDE            | **MaixVision** Workstation | **MaixVision** Workstation |
| 文档             | ⭐️⭐️⭐️⭐️     |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| 在线 AI 训练     | ⭐️⭐️⭐️        |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| 官方应用         | ⭐️             |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| 易用性           | ⭐️⭐️⭐️⭐️      |  🌟🌟🌟🌟🌟 | 🌟🌟🌟🌟🌟 |
| AI 分类(224x224) | MobileNetv1 50fps<br>MobileNetv2 ❌<br>Resnet ❌ | MobileNetv2 **130fps**<br>Resnet18 **62fps**<br>Resnet50 **28fps** | MobileNetv2 <span class="strong2">1218fps</span><br>Resnet50 <span class="strong2">200fps</span> |
| AI 检测<div class="comment">仅推理部分 /<br>\[包含前后处理(Python)\] /<br>\[双缓冲模式(Python)\]</div> | <div class="main_items">**YOLOv2**:<div class="sub_items">224x224: 15fps</div></div> |  <div class="main_items">**YOLOv5s**:<div class="sub_items">224x224: **100fps**<br>320x256 **70fps**<br>640x640: **15fps**</div></div>       <div class="main_items">**YOLOv8n**:<div class="sub_items">640x640: **23fps**</div></div>      <div class="main_items">**YOLO11n**:<div class="sub_items">224x224: **175fps**<br>320x224: **120fps**<br>320x320: **95fps**<br>640x640: **23fps**</div></div>                |                <div class="main_items">**YOLOv5s**:<div class="sub_items">224x224: <span class="strong2">495fps</span><br>320x256: <span class="strong2">400fps</span><br>640x480: <span class="strong2">106fps / 73fps / 103fps</span><br>640x640: <span class="strong2">80fps</span></div></div>                <div class="main_items">**YOLO11n**:<div class="sub_items">224x224: <span class="strong2">1214fps</span><br>640x480: <span class="strong2">168fps / 77fps / 143fps</span><br>640x640: <span class="strong2">113fps / 56fps / 98fps</span></div></div>    <div class="main_items">**YOLO11s**:<div class="sub_items">640x480: <span class="strong2">87fps / 53fps / 83fps</span><br>640x640: <span class="strong2">62fps / 39fps / 59fps</span></div></div>   <div class="main_items">**YOLO11l**:<div class="sub_items">640x640: <span class="strong2">19fps / 16fps / 19fps</span></div></div>                     |
| 大模型           | ❌              |  ❌           |  <span class="strong2">Qwen/DeepSeek 0.5B(fftf: 640ms, 9 tokens/s)<br>Qwen/DeepSeek 1.5B(fftf: 1610ms, 4 tokens/s) <br> VLM(InterVL 1B) <br>更多模型</span> |
| OpenMV 典型算法 |  <div class="comment">测试图像参考 <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a>  |                    <div class="comment">测试图像参考 <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>测试日期: 2025.8.22，更新可能会有优化</div>              |       <div class="comment">测试图像参考 <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>测试日期: 2025.8.22，更新可能会有优化</div>                             |
|   <div class="right second">二值化</div>  | 灰度 320x240: 7.4ms (135fps)<br>灰度 640x480: ❌<br>RGB 320x240: 11.3ms (88.5fps)<br>RGB 640x480: ❌ | 灰度 320x240: **3.1ms (326fps)**<br>灰度 640x480: **11ms (90fps)**<br>RGB 320x240: **13.2ms (75fps)**<br>RGB 640x480: **52.8ms (18fps)**        | 灰度 320x240: <span class="strong2">1.3ms (799fps)</span> <br>灰度 640x480: <span class="strong2">4.8ms (206fps)</span><br>RGB 320x240: <span class="strong2">3.4ms (294fps)</span><br>RGB 640x480: <span class="strong2">13.3ms (75fps)</span> |
|   <div class="right second">找色块</div>        | 320x240: 8.8ms (114fps) <br>640x480: ❌| 320x240: **7ms (143fps)**  <br>640x480: **20ms (50fps)**         | 320x240: <span class="strong2">3.7ms (271fps)</span><br>640x480: <span class="strong2">11.1ms (89fps)</span>  |
|   <div class="right second">单通道直方图</div>  | 320x240: **7.7ms (130fps)**<br>640x480: ❌ | 320x240: **10.9ms (91fps)**<br>640x480: **42.8ms (23fps)**       | 320x240: <span class="strong2">1.5ms (661fps)</span><br>640x480: <span class="strong2">5.9ms (168fps)</span>    |
|   <div class="right second">二维码</div>        | 320x240: **130.8ms (7.6fps)** <br>640x480: ❌| 640x480: 136.9ms (7fps)<br>NPU 加速：<br>&nbsp;&nbsp;320x240: **22.1ms (45fps)**<br>&nbsp;&nbsp;640x480: 57.6ms (17fps)  | 640x480: 57.9ms (17fps)<br>NPU 加速：<br>&nbsp;&nbsp;320x240: <span class="strong2">9.2ms (109fps)</span>   <br>&nbsp;&nbsp;640x480: <span class="strong2">23.2ms (43fps)</span> |
| OpenCV 典型算法     |   | <div class="comment">测试图像参考 <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>测试日期: 2025.8.22，更新可能会有优化</div>    | <div class="comment">测试图像参考 <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a><br>测试日期: 2025.8.22，更新可能会有优化</div>  |
|   <div class="right second">二值化</div>             | ❌  | 灰度 320x240: **2.2ms (463fps)**     <br>灰度 640x480: **7.1ms (140fps)** | 灰度 320x240: <span class="strong2">0.1ms (8174fps)</span>  <br>灰度 640x480: <span class="strong2">0.3ms (2959fps)</span>  |
|   <div class="right second">灰度图自适应二值化</div> | ❌  | 320x240: **5.8ms (171fps)**     <br>640x480: **21.3ms (46fps)**  | 320x240: <span class="strong2">1.6ms (608fps)</span>  <br>640x480: <span class="strong2">6.3ms (159fps)</span> |
|   <div class="right second">单通道直方图</div>       | ❌  | 320x240: **1ms (1000fps)**     <br>640x480: **6.2ms (160fps)**   | 320x240: <span class="strong2">0.4ms (2308fps)</span>  <br>640x480: <span class="strong2">1.7ms (604fps)</span>  |
|   <div class="right second">轮廓提取</div>           | ❌  | 320x240: **2.8ms (351fps)**    <br>640x480: **8.6ms (116fps)**   | 320x240: <span class="strong2">0.4ms (2286fps)</span>  <br>640x480: <span class="strong2">1.4ms (692fps)</span>  |
<!-- //TODO: 注意！！！ 修改此表请同步修改 ../../../README_ZH.md 和 ../../../README.md ！！！！！！！注意 -->

<!--
|   <div class="right second">二值化</div>  | - | 灰度 320x240: 3.1ms (326fps)<br>灰度 640x480: 11ms (90fps)<br>RGB 320x240: 13.2ms (75fps)<br>RGB 640x480: 52.8ms (18fps)        | 灰度 320x240: 1.3ms (799fps) <br>灰度 640x480: 4.8ms (206fps)<br>RGB 320x240: 3.4ms (294fps)<br>RGB 640x480: 13.3ms (75fps) |
|   <div class="right second">边缘检测</div>      | - | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">找色块</div>        | - | 320x240: 7ms (143fps)<br>640x480: 20ms (50fps)              | 320x240: 3.7ms (271fps)  <br>640x480: 11.1ms (89fps)  |
|   <div class="right second">找直线</div>        | - | 320x240:              | 320x240:    |
|   <div class="right second">找圆形</div>        | - | 320x240:              | 320x240:    |
|   <div class="right second">找矩形</div>        | - | 320x240:              | 320x240:    |
|   <div class="right second">单通道直方图</div>  | - | 320x240:              | 320x240:    |
|   <div class="right second">二维码</div>        | - | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">Apriltag</div>      | - | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
| OpenCV 典型算法     |  | <div class="comment">测试图像参考 <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a></div>    | <div class="comment">测试图像参考 <a href="https://github.com/sipeed/MaixPy/tree/main/projects/app_benchmark">Benchmark APP</a></div>  |
|   <div class="right second">二值化</div>       | ❌  | 灰度：320x240:     <br>640x480:         | 灰度：320x240:   <br>640x480:  |
|   <div class="right second">灰度图自适应二值化</div> | ❌  | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">边缘检测</div>           | ❌  | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">高斯模糊</div>           | ❌  | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">轮廓提取</div>           | ❌  | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">霍夫直线</div>           | ❌  | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">霍夫圆形</div>           | ❌  | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
|   <div class="right second">单通道直方图</div>       | ❌  | 320x240:     <br>640x480:         | 320x240:   <br>640x480:  |
 -->

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
| **GitHub**| [GitHub](https://github.com)搜索 `MaixCAM` 或者 `MaixPy` |
| **Bilibili**| B站搜索 `MaixCAM` 或者 `MaixPy` |
| **讨论**| [maixhub.com/discussion](https://maixhub.com/discussion) |
| **MaixPy issues**| [github.com/sipeed/MaixPy/issues](https://github.com/sipeed/MaixPy/issues) |
| **Telegram**| [t.me/maixpy](https://t.me/maixpy) |
| **QQ 群**| 862340358 |

</div>
</div>


</div>
<!-- wrapper end -->

