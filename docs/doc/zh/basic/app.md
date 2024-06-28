---
title: 应用开发和应用商店
---


## 应用生态简介

为了让开发板做到开箱即用，以及方便用户无门槛地使用，以及方便开发者分享自己的有趣应用，并且能有有效的渠道获取到反馈甚至是收益，我们推出了一个简易的应用框架，包括：

* **[应用商店](https://maixhub.com/app)**： 开发者上传分享应用，用户无需开发直接下载使用，开发者可以获取到一定的现金收益（来自 MaixHub 官方以及用户打赏）。
* **出厂内置大量应用**： 官方提供了一些常用的应用，比如找色块、AI 物体检测追踪、找二维码、人脸识别等等，用户可以直接使用，也可以作为串口模块直接使用。
* **MaixPy + MaixCDK** 软件开发包：使用 [MaixPy](https://github.com/sipeed/maixpy) 或者 [MaixCDK](https://github.com/sipeed/MaixCDK) 可以用 Python 或者 C/C++ 语言快速开发嵌入式 AI 视觉听觉应用，超高效率实现你的有趣想法。
* **MaixVision** 配套电脑端开发工具: 全新的电脑端代码开发工具，快速上手、调试、运行、上传代码、安装应用到设备，一键式开发，甚至支持图像化积木式编程，小学生也能轻松上手。

大家可以多多关注应用商店，也可以在应用商店中分享自己的应用，大家一起共建活跃的社区。


## 打包应用


使用 MaixPy + MaixVison 可以方便地开发、打包、安装应用：
* 在 MaixVision 中使用 MaixPy 开发应用程序，可以是单个文件，也可以是一个工程目录。
* 连接设备。
* 点点击 MaixVision 左下角的 安装 按钮，会弹出一个界面填写应用的基本信息，id 是用来判别应用的 id，一个设备不能同时安装相同 id 的不同应用，所以 id 应该与 MaixHub 上面已经有的应用 id 不同，应用名字可以重复。以及图标等。
* 点击打包应用，会将应用打包成一个安装包，如果你要上传到 [MaixHub 应用商店](https://maixhub./com/app)，用这个打包好的文件即可。
* 点击 安装应用，这会将打包好的应用安装到设备。
* 断开与设备的连接，就能看到设备功能选择界面多了一个你的应用，直接点进去就能运行。

> 如果你用 MaixCDK 开发，使用 `maixcdk relrease` 就能打包出来一个应用，具体看 MaixCDK 的文档。

## 退出应用

如果你只是写了比较简单的应用，没有做界面和返回按钮，默认可以按设备上的功能按键（一般是 USER 或者 FUNC 或者 OK 按钮）或者返回按钮（如果有这个按键，MaixCAM 默认没有这个按键）来退出应用。

## 安装应用

* **方法一**： 设备使用`应用商店`应用，从[应用商店](https://maixhub.com/app)找到应用，设备联网后，扫码安装。
* **方法二**： 使用安装包本地安装，将安装包传输到设备文件系统，比如`/root/my_app_v1.0.0.zip`，然后执行代码，注意修改`pkg_path`变量的路径，你也可以在`MaixPy`的 `examples/tools/install_app.py`找到本代码:
```python
import os

def install_app(pkg_path):
    if not os.path.exists(pkg_path):
        raise Exception(f"package {pkg_path} not found")
    cmd = f"/maixapp/apps/app_store/app_store install {pkg_path}"
    err_code = os.system(cmd)
    if err_code != 0:
        print("[ERROR] Install failed, error code:", err_code)
    else:
        print(f"Install {pkg_path} success")

pkg_path = "/root/my_app_v1.0.0.zip"

install_app(pkg_path)
```
* **方法三**:
  * 如果是使用`MaixPy`开发的应用，在项目根目录（包含`app.yaml`和`main.py`）执行`maixtool deploy`会弹出一个二维码，保持设备和电脑在同一局域网，设备使用应用商店扫描对应的局域网地址二维码就能在线安装。
  * 如果是使用`MaixCDK`开发的应用，在项目根目录执行`maixcdk deploy`也会出现二维码，保持设备和电脑在同一局域网，设备使用应用商店扫描对应的局域网地址二维码就能在线安装。

## 应用开发基本准则

* 因为默认都配了触摸屏幕，推荐都写一个简单的界面显示，最好有触摸交互。实现方法可以在例子里面找找参考。
* 界面和按钮不要太小，因为 MaixCAM 默认的屏幕是 2.3寸 552x368分辨率，PPI 比较高屏幕比较小，要让手指能很容易戳到并且不会点错。
* 每个应用实现的主要功能实现一个简单的串口交互，基于[串口协议](https://github.com/sipeed/MaixCDK/blob/master/docs/doc/convention/protocol.md) （[例程](https://github.com/sipeed/MaixPy/tree/main/examples/communication/protocol)）,这样用户可以直接当成串口模块使用，比如人脸检测应用，可以在检测到人脸后通过串口输出坐标。











