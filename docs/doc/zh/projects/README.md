---
title: MaixCAM MaixPy 项目实战 介绍和汇总
---

## 简介

这里提供：
* 一些常见的项目实战示例，方便社区成员可以参考复现使用，也方便激发大家的灵感做出更多更好的应用和项目出来。
* 一些社区成员的开源项目，方便大家参考学习。

除了这里，要找到用 MaixPy 实现的相关的项目，还有有几种方式：

### MaixPy 官方文档

也就是本文档左边目录可以找到的项目实战，比如`小车巡线`。

如果你有好的项目，或者好的项目推荐，也可以点击右上角编辑文档，添加 PR（Pull Request） 添加到文档，非常欢迎。


### MaixHub 项目分享广场


在[MaixHub 项目分享](https://maixhub.com/share?type=project) 栏目可以找到项目分享。

有高质量的分享也会被链接到 MaixPy 官方文档。

你也可以分享你的项目制作方法，会获得官方（必获得）以及社区成员的现金打赏（通常高质量能解决急需需求的更容易被打赏）。


### MaixHub 应用分享

除了项目分享以外，还可以在[MaixHub 应用商店](https://maixhub.com/app) 找到可以直接运行的应用，有部分应用可能是用 MaixPy 编写的，如果作者提供了源码或者写了详细的教程也都可以参考。

### GitHub 搜索

在 [GitHub](https://github.com) 上搜索 `MaixPy` 或者 `MaixCAM` 也可以找到一些高质量的开源项目。


## 开源项目汇总

通常是完整的项目，包含代码、文档、演示视频等。

### 工具类

* [MaixPy-UI-Lib](https://github.com/aristorechina/MaixPy-UI-Lib): 一款基于 MaixPy 编写的轻量 UI 库，纯 Python 实现，支持多种控件，使用简单方便，也方便学习扩展，里面还有很多示例代码，比如 LAB/HSV 脱机阈值调试工具。
* [基于 MaixPy 实现的脱机阈值调试](https://maixhub.com/share/103)：实现了一个类封装脱机阈值调试工具，无三方依赖，直接调用即可使用。
* [maixcam 脱机使用串口屏调节阈值](https://maixhub.com/share/104)：外接一个串口屏，实现了脱机调节阈值的功能，适合需要外接屏幕的场景。
* [CAM脱机手动阈值编辑器](https://maixhub.com/share/102)： 又一个脱机手动阈值编辑器，代码简单易懂，适合学习和参考。

### 竞赛类

* [MaixCam-Tic-Tac-Toe 2024年全国大学生电子设计竞赛（E题 - 三子棋游戏装置）](https://github.com/HYK-X/MaixCam_Tic_Tac_Toe_2024): 基于 Sipeed Maix 系列开发板，使用计算机视觉技术实现的三子棋（井字棋）对弈机器人项目。该项目是 2024年全国大学生电子设计竞赛（E题 - 三子棋游戏装置） 的一个完整解决方案。

### 拍摄类

等你来分享。

### 监控和智能家居类

等你来分享。

### 自动化提高效率

等你来分享。

### 机器人

等你来分享。

### 更多

更多分类提交 issue 讨论添加。



## 经验分享汇总

通常是比较简单的经验和代码片段分享，方便大家学习和参考。

### UI 相关

* [MaixPy-UI-Lib](https://github.com/aristorechina/MaixPy-UI-Lib): 一款基于 MaixPy 编写的轻量 UI 库，纯 Python 实现，支持多种控件，使用简单方便，也方便学习扩展，里面还有很多示例代码，比如 LAB/HSV 脱机阈值调试工具。
* [基于 MaixPy 实现的脱机阈值调试](https://maixhub.com/share/103)：实现了一个类封装脱机阈值调试工具，无三方依赖，直接调用即可使用。
* [maixcam 脱机使用串口屏调节阈值](https://maixhub.com/share/104)：外接一个串口屏，实现了脱机调节阈值的功能，适合需要外接屏幕的场景。
* [CAM脱机手动阈值编辑器](https://maixhub.com/share/102)： 又一个脱机手动阈值编辑器，代码简单易懂，适合学习和参考。

### 外设相关

* [MaixCam驱动WS2812进行补光和颜色补偿](https://maixhub.com/share/90): 使用 MaixCAM 驱动 WS2812 LED 灯（使用了硬件 SPI驱动）。
* [使用 MaixCAM-Pro 捕获 PWM 的频率和占空比](https://maixhub.com/share/98): 使用 SPI 捕获 PWM 的频率和占空比，适合需要测量 PWM 信号的场景。
* [使用MaixCAM的蓝牙功能 · 硬件篇](https://maixhub.com/share/58)
* [使用MaixCAM的蓝牙功能 · 软件篇](https://maixhub.com/share/62)

### 图像算法相关

* [MaixCam-Tic-Tac-Toe 2024年全国大学生电子设计竞赛（E题 - 三子棋游戏装置）](https://github.com/HYK-X/MaixCam_Tic_Tac_Toe_2024): 基于 Sipeed Maix 系列开发板，使用计算机视觉技术实现的三子棋（井字棋）对弈机器人项目。该项目是 2024年全国大学生电子设计竞赛（E题 - 三子棋游戏装置） 的一个完整解决方案。
* [开源一个很简单的通过cv2.solvePnP实现透视投影下的位姿估计](https://maixhub.com/share/93): 检测物体的3D位姿。
* [使用MaixPy生成二维码](https://maixhub.com/share/79): 使用 qrcode 库生成二维码。



## 更多

这里收录不是很及时，更多请按照本文开头的方式寻找。
