---
title: MaixCAM MaixPy 应用开发和应用商店
---

## 哪里找应用

开机后会自动进入应用选择界面，内置各种应用均发布在 [MaixHub 应用商店](https://maixhub.com/app)， 可以在这里找到对应应用的介绍和使用说明。

## 哪里找源码

源码可以在应用商店应用页面看到源码链接（如果有）。
官方集成的应用源码都在 [MaixPy/projects](https://github.com/sipeed/MaixPy/tree/main/projects) 目录 或者 [MaixCDK/projects](https://github.com/sipeed/MaixCDK/tree/main/projects) 。

## 安装应用

可以先设置语言 `设置 -> 语言`， 以及 `设置 -> WiFi`。

`应用商店`应用可以用来升级和安装应用，连接上可以连接互联网的 WiFi 后即可在[MaixHub 应用商店](https://maixhub.com/app)扫码安装应用。


## 应用生态简介

为了让开发板做到开箱即用，以及方便用户无门槛地使用，以及方便开发者分享自己的有趣应用，并且能有有效的渠道获取到反馈甚至是收益，我们推出了一个简易的应用框架，包括：

* **[应用商店](https://maixhub.com/app)**： 开发者上传分享应用，用户无需开发直接下载使用，开发者可以获取到一定的现金收益（来自 MaixHub 官方以及用户打赏）。
* **出厂内置大量应用**： 官方提供了一些常用的应用，比如找色块、AI 物体检测追踪、找二维码、人脸识别等等，用户可以直接使用，也可以作为串口模块直接使用。
* **MaixPy + MaixCDK** 软件开发包：使用 [MaixPy](https://github.com/sipeed/maixpy) 或者 [MaixCDK](https://github.com/sipeed/MaixCDK) 可以用 Python 或者 C/C++ 语言快速开发嵌入式 AI 视觉听觉应用，超高效率实现你的有趣想法。
* **MaixVision** 配套电脑端开发工具: 全新的电脑端代码开发工具，快速上手、调试、运行、上传代码、安装应用到设备，一键式开发，甚至支持图像化积木式编程，小学生也能轻松上手。

大家可以多多关注应用商店，也可以在应用商店中分享自己的应用，大家一起共建活跃的社区。


## 打包应用

参考[MaixVision 使用文档](./maixvision.md) 打包应用部分。

## 退出应用

如果你只是写了比较简单的应用，没有做界面和返回按钮，默认可以按设备上的功能按键（一般是 USER 或者 FUNC 或者 OK 按钮）或者返回按钮（如果有这个按键，MaixCAM 默认没有这个按键）来退出应用。

## 安装应用

* **方法一**： 设备使用`应用商店`应用，从[应用商店](https://maixhub.com/app)找到应用，设备联网后，扫码安装。
* **方法二**： 使用安装包本地安装，将安装包传输到设备文件系统，比如`/root/my_app_v1.0.0.zip`，然后执行`examples/tools/install_app.py`代码，注意修改`pkg_path`变量的路径。

* **方法三**:
  * 如果是使用`MaixPy`开发的应用，在项目根目录（包含`app.yaml`和`main.py`）执行`maixtool deploy`会弹出一个二维码，保持设备和电脑在同一局域网，设备使用应用商店扫描对应的局域网地址二维码就能在线安装。
  * 如果是使用`MaixCDK`开发的应用，在项目根目录执行`maixcdk deploy`也会出现二维码，保持设备和电脑在同一局域网，设备使用应用商店扫描对应的局域网地址二维码就能在线安装。

## 应用开发基本准则

* 因为默认都配了触摸屏幕，推荐都写一个简单的界面显示，最好有触摸交互。实现方法可以在例子里面找找参考。
* 界面和按钮不要太小，因为 MaixCAM 默认的屏幕是 2.3寸 552x368分辨率，PPI 比较高屏幕比较小，要让手指能很容易戳到并且不会点错。
* 每个应用实现的主要功能实现一个简单的串口交互，基于[串口协议](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) （[例程](https://github.com/sipeed/MaixPy/tree/main/examples/communication/protocol)）,这样用户可以直接当成串口模块使用，比如人脸检测应用，可以在检测到人脸后通过串口输出坐标。


## 设置应用开机自动启动

参考 [应用开机自启](./auto_start.md)

## 系统设置

系统设置应用里面有一些设置项，比如语言、屏幕亮度等，我们可以通过`maix.app.get_sys_config_kv(item, key)`来获取这些设置项的值。
比如获取语言设置项：

```python
from maix import app
locale = app.get_sys_config_kv("language", "locale")
print("locale:", locale)

backlight = app.get_sys_config_kv("backlight", "value")
print("backlight:", backlight, ", type:", type(backlight))
```

这里注意，所有设置项的值都是字符串类型，使用时需要注意。


```ini
# All configs user can edit easily
# Format: maix_<item>_<key>=value
#         all key charactors should be lowercase
# Full supported items see documentation of maixpy at:
#      https://wiki.sipeed.com/maixpy/doc/zh/basic/app.html

### [language]
maix_language_locale=en

### [wifi]
# can be "ap" or "sta" or "off"
maix_wifi_mode=sta
maix_wifi_ssid=Sipeed_Guest
maix_wifi_passwd=qwert123
# encrypt default auto detect, you can also set it manually:
#   can be "NONE", "WPA-PSK", "WPA-EAP", "SAE"
# maix_wifi_encrypt="WPA-PSK"

### [comm] Maix comm protocol
# can be "uart" or "none"
maix_comm_method=uart

## [backlight] Screeen backlight, from 0 to 100
maix_backlight_value = 50

### [npu]
# for maixcam2, enable AI ISP(1) or not(0),
# enalbe AI ISP will get better camera quality and occupy half of NPU.
maix_npu_aiisp=0

```








