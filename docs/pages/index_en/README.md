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
    <h3>Fast implementation of AI vision and auditory applications</h3>
</div>

<div id="big_btn_wrapper" class="flex flex-wrap justify-center items-center">
    <a class="btn m-1" href="/doc/zh/index.html">Quick Start 🚀📖</a>
    <a class="btn m-1" href="/api/">API Reference 📚</a>
    <a class="btn m-1" target="_blank" href="https://wiki.sipeed.com/maixcam">Hardware Platform: MaixCAM 📷</a>
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


<br>

Currently, there are two generations of hardware products: `MaixCAM / MaixCAM-Pro` and `MaixCAM2`, offering different options in terms of performance, accessories, and appearance.
A detailed performance comparison provided later.


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

<!-- feature introduction -->

<div id="feature" class="flex flex-col justify-center items-center">

## More Features

<div class="flex flex-col justify-center items-center">

Here are some feature highlights, find more in the [Community](#community)

You can create new features using the rich API provided by MaixPy.

(Only MaixCAM2 support LLM/VLM related functions)

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
            <video playsinline controls autoplay loop muted preload src="/static/video/face_recognition.mp4"></video>
            <p class="feature">AI Face Recognition</p>
            <p class="description">Recognize different facial features, emotion recognition</p>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/keypoints.mp4"></video>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/self_learn_classifier.mp4"></video>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/streaming.mp4"></video>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/ocr.mp4"></video>
            <p class="feature">OCR</p>
            <p class="description">Recognize characters in images, digitize old items</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/depth_anything_v2.mp4"></video>
            <p class="feature">mono depth estimation</p>
            <p class="description">mono camera depth estimation</p>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/tts.mp4"></video>
            <p class="feature">TTS</p>
            <p class="description">TTS generation, support muti-language</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/llm.mp4"></video>
            <p class="feature">Offline LLM</p>
            <p class="description">Fully offline LLM</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/vlm.mp4"></video>
            <p class="feature">LLM VLM</p>
            <p class="description">Fully offline VLM</p>
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
            <video playsinline controls autoplay loop muted preload src="/static/video/sky.mp4"></video>
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
            <p class="description">Onboard gyroscope, supports exporting gyroflow stabilization format for DIY photography</p>
        </div>
        <div>
        </div>
    </div>
    <div class="feature_item">
        <div class="img_video">
            <video playsinline controls autoplay loop muted preload src="/static/video/tof.mp4"></video>
            <p class="feature">TOF module</p>
            <p class="description">Detect depth with TOF module</p>
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
<!-- //TODO: 注意！！！ 修改此表请同步修改 ../../../README_ZH.md 和 ../../../README.md ！！！！！！！注意 -->


<div class="mt-6"></div>



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
| **GitHub**| Search for `MaixCAM` or `MaixPy` on [GitHub](https://github.com) |
| **Bilibili**| Search for `MaixCAM` or `MaixPy` on Bilibili |
| **Discussion**| [maixhub.com/discussion](https://maixhub.com/discussion) |
| **MaixPy issues**| [github.com/sipeed/MaixPy/issues](https://github.com/sipeed/MaixPy/issues) |
| **Telegram**| [t.me/maixpy](https://t.me/maixpy) |
| **QQ Group**| 862340358 |

</div>


</div>
<!-- wrapper end -->
