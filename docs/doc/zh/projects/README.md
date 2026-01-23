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

### 内置应用

`MaixCAM`, `MaixCAM Pro`, `MaixCAM2`等平台内置的应用

| 内置应用                                               | 已支持的平台 | 说明 | 文档           |
| ------------------------------------------------------------ | ------------ | -------- | -------------- |
| 跑分测试     | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 测试CPU/NPU等硬件的综合性能 | [说明文档](https://maixhub.com/app/188) |
| 本地聊天 | `MaixCAM2` | 离线语音聊天 | [说明文档](https://maixhub.com/app/187) |
| 桌面监视器 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 主机性能监控小工具 | [说明文档](https://maixhub.com/app/13) |
| 人脸情绪 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 情绪识别 | [说明文档](https://maixhub.com/app/189) |
| 人脸关键点 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 关键点识别 | [说明文档](https://maixhub.com/app/186) |
| 人脸识别 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 人脸识别 | [说明文档](https://maixhub.com/app/190) |
| 人脸追踪 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 人脸追踪 | [说明文档](https://maixhub.com/app/31) |
| 手势分类 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 识别不同的手势 | [说明文档](https://maixhub.com/app/192) |
| 手关键点 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 手部的关键点检测 | [说明文档](https://maixhub.com/app/227) |
| HTTP 文件浏览器 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 通过浏览器查看和下载文件 | [说明文档](https://maixhub.com/app/59) |
| 人体姿态 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 人体姿态识别 | [说明文档](https://maixhub.com/app/191) |
| 人体姿态分类 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 识别不同的人体姿态 | [说明文档](https://maixhub.com/app/193) |
| 图像生成 | `MaixCAM2` | 文生图, 图生图 | [说明文档](https://maixhub.com/app/198) |
| 姿态解算 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 解算 IMU 数据 | [说明文档](https://maixhub.com/app/128) |
| MaixHub 客户端 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 与MaixHub交互 | [说明文档](https://maixhub.com/app/48) |
| 深度估计 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 单目深度估计 | [说明文档](https://maixhub.com/app/195) |
| 鼠标模拟 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 将设备作为鼠标使用 | [说明文档](https://maixhub.com/app/196) |
| 文字识别 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 文字识别 | [说明文档](https://maixhub.com/app/70) |
| RTMP 直播 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | RTMP 推流 | [说明文档](https://maixhub.com/app/35) |
| RTSP 推流 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | RTSP 推流 | [说明文档](https://maixhub.com/app/197) |
| 扫描二维码 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 扫描和识别条形码, 二维码, Apriltag标签 | [说明文档](https://maixhub.com/app/199) |
| 自学习分类 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 学习目标并分类 | [说明文档](https://maixhub.com/app/200) |
| 自学习检测器 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 学习目标并检测 | [说明文档](https://maixhub.com/app/62) |
| 语音识别 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 语音转文本 | [说明文档](https://maixhub.com/app/65) |
| 热成像仪256 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 外接热成像模组 | [说明文档](https://maixhub.com/app/208) |
| 热融合夜视仪 | `MaixCAM2` | 热成像仪与AI夜视的融合 | [说明文档](https://maixhub.com/app/228) |
| 跟踪计数 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 人流计数 | [说明文档](https://maixhub.com/app/61) |
| 手势控制鼠标 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 通过手势控制鼠标 | [说明文档](https://maixhub.com/app/223) |
| 姿态控制键盘 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 通过人体姿态控制键盘 | [说明文档](https://maixhub.com/app/178) |
| 本地视觉大模型 | `MaixCAM2` | 图生文 | [说明文档](https://maixhub.com/app/194) |
| WebRTC 推流 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | WebRTC推流 | [说明文档](https://maixhub.com/app/202) |
| OBB 检测 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 图像检测,结果带旋转角度 | [说明文档](https://maixhub.com/app/203) |
| YOLO11 分割 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 图像分割 | [说明文档](https://maixhub.com/app/204) |
| YOLO-World | `MaixCAM2` | YOLO-World 检测 | [说明文档](https://maixhub.com/app/229) |
| 相机 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 拍照, 录像 | [说明文档](https://maixhub.com/app/221) |
| 相册            | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 显示照片     | [说明文档](https://maixhub.com/app/222) |
| AI 分类器       | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | AI分类                                 | [说明文档](https://maixhub.com/app/211) |
| AI 检测器       | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | AI检测                                 | [说明文档](https://maixhub.com/app/213) |
| 寻找色块        | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 找色块 | [说明文档](https://maixhub.com/app/33) |
| 巡线 | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 找直线 | [说明文档](https://maixhub.com/app/215) |
| 语音识别(Maix-Speech)        | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 语音转文本                             | [说明文档](https://maixhub.com/app/216) |
| 语音识别(AI 大模型)        | `MaixCAM2` | 语音转文本     | [说明文档](https://maixhub.com/app/217) |
| 热成像仪        | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 外接红外摄像头模组(PMOD_Thermal32)     | [说明文档](https://maixhub.com/app/218) |
| ToF相机         | `MaixCAM`, `MaixCAM Pro`, `MaixCAM2` | 外接ToF模组(ToF100)       | [说明文档](https://maixhub.com/app/219) |
| UVC相机         | `MaixCAM`, `MaixCAM Pro` | 作为 usb 摄像头 | [说明文档](https://maixhub.com/app/220) |
| 应用商店         | `MaixCAM`, `MaixCAM Pro` | 安装其他应用 | [说明文档](https://maixhub.com/app/225) |
| 设置        | `MaixCAM`, `MaixCAM Pro` | 修改系统设置 | [说明文档](https://maixhub.com/app/224) |







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
