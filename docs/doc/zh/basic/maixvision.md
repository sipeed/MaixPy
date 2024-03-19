---
title: MaixVision -- MaixPy 编程 + 图形化积木编程
---


## 简介



## 使用 MaixPy 编程和在线运行

按照[快速开始](../README.md)的步骤连接设备，我们可以很方便地使用 MaixPy 编程和在线运行。

## 区分`设备文件系统`和`电脑文件系统`

这里我们有一个比较重要的概念需要掌握：**分清楚`设备文件系统`和`电脑文件系统`**。
* **电脑文件系统**：运行在电脑上，在 MaixVision 中打开文件或者工程都是打开的电脑里面的文件，保存也是自动保存到电脑的文件系统。
* **设备文件系统**：程序运行时会将程序发送到设备上运行，所以代码里面使用的文件都是从设备文件系统读取，

## 实时预览图像

MaixPy 提供`display`模块，可以将图像显示到屏幕上，同时，在调用`display`模块的`show`方法时，会将图像发送到 MaixVision 显示，比如代码：
```python
from maix import display, camera

cam = camera.Camera(640, 480)
disp = display.Display()
while 1:
    disp.show(cam.read())
```

这里我们用摄像头读取了图像，然后通过`disp.show()`方法将图像显示到屏幕上，同时也会发送到 MaixVision 显示。

当我们点击了右上角的`暂停`按钮，就会停止发送图像到 MaixVision 显示。



## 计算图像的直方图

在上一步中我们可以在 MaixVision 中实时看到图像，我们用鼠标框选一个区域，图像下方就能看到这个区域的直方图了，选择不同的颜色表示方法，可以看到不同的颜色通道的直方图。

这个功能方便我们在做某些图像处理算法时找到一些合适的参数。


## 使用图形化积木编程

开发中，敬请期待。


## 传输文件到设备

开发中，敬请期待。

目前可以用其它工具代替，比如：

> 先知道设备的 ip 地址或者设备名称，MaixVision 就可以搜索到, 或者在设备`设置->系统信息`中看到，比如 `maixcam-xxxx.local`。
> 用户名和密码都是 `root`, 使用 `SFTP` 协议传输文件，端口号是 `22`。

### Windows 下

使用 `WinSCP` 或者 `FileZilla` 等工具连接设备，将文件传输到设备上，选择 `SFTP` 协议填写设备和账号信息连接即可。

具体不懂的可以自行搜索。

### Linux 下

终端使用 `scp` 命令传输文件到设备上，比如：

```bash
scp /path/to/your/file.py root@maixcam-xxxx.local:/root
```

### Mac 下

* **方法一**：终端使用 `scp` 命令传输文件到设备上，比如：
```bash
scp /path/to/your/file.py root@maixcam-xxxx.local:/root
```

* **方法二**：使用 `FileZilla` 等工具连接设备，将文件传输到设备上，选择 `SFTP` 协议填写设备和账号信息连接即可。







