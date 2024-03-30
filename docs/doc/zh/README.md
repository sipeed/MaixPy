
---
title: MaixPy 快速开始
---

<div style="font-size: 1.2em;border: 2px solid green; border-color:#c33d45;padding:1em; text-align:center; background: #c33d45; color: white">
    MaixPy 唯一官网: <a target="_blank" style="color: white" href="https://wiki.sipeed.com/maixpy">
        wiki.sipeed.com/maixpy
    </a>
    <br>
    <div style="height:0.4em"></div>
    MaixPy 例程和源码: <a target="_blank" style="color: white" href="https://github.com/sipeed/MaixPy">
        github.com/sipeed/MaixPy
    </a>
</div>
<br>

> 关于 MaixPy 介绍请看 [MaixPy 官网首页](../README.md)

## 获得 MaixCAM 设备

在 [Sipeed 淘宝](https://sipeed.taobao.com) 或者 [Sipeed 速卖通](https://sipeed.aliexpress.com) 店铺购买 <a href="https://wiki.sipeed.com/maixcam" target="_blank">MaixCAM</a> 开发板。

**建议购买带 `TF 卡`、`摄像头`、`2.3寸触摸屏`、`外壳`、`Type-C一转二小板`、`4P串口座子+线`的套餐**，方便后续使用和开发，**后面的教程都默认你已经有了这些配件**（包括屏幕）。

另外需要准备一根 `Type-C` 数据线，尽量买质量好点的防止供电和连接不稳定。

>! 注意，目前只支持 MaixCAM 开发板，其它同型号芯片的开发板均不支持，包括 Sipeed 的同型号芯片开发板，请注意不要买错造成不必要的时间和金钱浪费。


## 上手体验

插入套餐里面的 TF 卡，使用 `Type-C` 数据线连接 `MaixCAM` 设备给设备供电，等待设备开机，开机会进入功能选择界面。
> 如果屏幕没有显示，请确认购买了配套的 TF 卡，如果确认有 TF 卡，可以尝试[更新系统](./basic/os.md)。
> 如果你没有购买 TF 卡套餐，你需要按照[升级和烧录系统](./basic/os.md)的方法烧录最新的系统到 TF 卡。

开机后可以看到功能选择界面，在设置中可以切换语言，可以自行尝试内置的各种应用和功能。

## 作为串口模块使用

内置的各种应用可以直接当成串口模块使用，比如`找色块`、`找人脸`、`找二维码`等等，
> 如果是想把设备当成主控使用（或者你还不懂什么是串口模块）可以跳过这一步。

使用方法：
* 硬件连接： 可以给设备接上`Type-C一转二小板`，这样我们就能将设备通过串口连接到你的主控上了，比如`Arduino`、`树莓派`、`STM32`等等。
* 打开你想用的应用，比如二维码识别，当设备扫描到二维码就会通过串口把结果发送给你的主控了。
> 发送的串口波特率是 `115200`，数据格式是 `8N1`，协议遵循 [Maix 串口通信协议标准](https://wiki.sipeed.com/maixcdk/docs/doc/convention/protoco.md)，可以在[MaixHub APP](https://maixhub.com/app) 找到对应的应用介绍查看协议。

## 准备连接电脑和设备

为了后面电脑（PC）能和 设备（MaixCAM）通信，我们要让它们在同一个局域网内，提供了两种方式：
* **方法一**：无线连接， 设备使用 WiFi 连接到电脑连接的同一个路由器或者 WiFi 热点下： 在设备的`设置 -> WiFi 设置`中连接到你的 WiFi 即可。
* **方法二**：有线连接， 设备通过 USB 线连接到电脑，设备会虚拟成一个 USB 网卡，这样和电脑就通过 USB 在同一局域网了。

方案二在不同电脑系统中有不同设置方法：
* **Linux**: 无需额外设置，插上 USB 线即可， 使用 `ifconfig` 或者 `ip addr` 查看到 `usb0` 网卡
* **Windows**: 可以先确认`网络适配器`里面是否多了一个 RNDIS 设备，如果有就直接能用。否则需要手动安装 RNDIS 网卡驱动：
  * 打开电脑的`设备管理器`。
  * 然后在`其它设备`里面找个一个带问号的 RNDIS 设备，右键选择`更新驱动程序`。
  * 选择`浏览计算机以查找驱动程序`，然后选择`让我从计算机上的可用驱动程序列表中选择`。
  * 选择`网络适配器`，然后点击`下一步`。
  * 左边选择`Microsoft`，右边选择`远程 NDIS 兼容设备`，然后点击`下一步`, 选择`是`。
  * 装好后的效果
  ![RNDIS](../../static/image/rndis_windows.jpg)
* **MacOS**: 无需额外设置，插上 USB 线即可， 使用 `ifconfig` 或者 `ip addr` 查看到 `usb0` 网卡

## 开发环境准备

* 下载 [MaixVision](https://wiki.sipeed.com/maixvision) 并安装。
* 使用 Type-C 连接设备和电脑，打开 MaixVision，点击左下角的`“连接”`按钮，会自动搜索设备，稍等一下就能看到设备，点击设备有点的连接按钮以连接设备。

如果没有扫描到设备，你也可以在设备的 `设置 -> 设备信息` 中查看设备的 IP 地址手动输入。

这里有 MaixVision 的使用示例视频:

<video style="width:100%" controls muted preload src="/static/video/maixvision.mp4"></video>

## 运行例程

点击 MaixVision 左侧的`示例代码`，选择一个例程，点击左下角`运行`按钮将代码发送到设备上运行。

比如：
* `hello.py`，点击`运行`按钮，就能看到 MaixVision 终端有来自设备打印的`Hello MaixPy!`了。
* `camera_display.py`，这个例程会打开摄像头并在屏幕上显示摄像头的画面。
```python
from maix import camera, display, app

disp = display.Display()          # 构造一个显示对象，并初始化屏幕
cam = camera.Camera(640, 480)     # 构造一个摄像头对象，手动设置了分辨率为 640x480, 并初始化摄像头
while not app.need_exit():        # 一直循环，直到程序退出（可以通过按下设备的功能按键退出或者 MaixVision 点击停止按钮退出）
    img = cam.read()              # 读取摄像头画面保存到 img 变量，可以通过 print(img) 来打印 img 的详情
    disp.show(img)                # 将 img 显示到屏幕上
```
* `yolov5.py` 会检测摄像头画面中的物体框出来并显示到屏幕上，支持 80 种物体的检测，具体请看[YOLOv5 物体检测](./vision/yolov5.md)。

其它例程可以自行尝试。

## 安装应用到设备

上面是在设备中运行代码，`MaixVision` 断开后代码就会停止运行，如果想让代码出现在开机菜单中，可以打包成应用安装到设备上。

点击 `MaixVision` 左下侧的安装应用按钮，填写应用信息，会将应用安装到设备上，然后在设备上就能看到应用了。
也可以选择打包应用，将你的应用分享到[MaixHub 应用商店](https://maixhub.com/app)。

> 默认例程没有显式编写退出功能，进入应用后按下设备的功能按键即可退出应用。（对于 MaixCAM 是 user 键）

如果想让程序开机自启动，可以在 `设置 -> 开机启动` 中设置。


## 下一步

看到这里，如果你觉得不错，**请务必来 [github](https://github.com/sipeed/MaixPy) 给 MaixPy 开源项目点一个 star（需要先登录 github）, 你的 star 和认同是我们不断维护和添加新功能的动力！**

到这里你已经体验了一遍使用和开发流程了，接下来可以学习 `MaixPy` 语法和功能相关的内容，请按照左边的目录进行学习，如果遇到 `API` 使用问题，可以在[API 文档](/api/)中查找。

学习前最好带着自己学习的目的学，比如做一个有趣的小项目，这样学习效果会更好，项目和经验都可以分享到[MaixHub 分享广场](https://maixhub.com/share)，会获得现金奖励哦！

## 分享交流

* **[MaixHub 项目和经验分享](https://maixhub.com/share)** ：分享你的项目和经验，获得现金打赏，获得官方打赏的基本要求：
  * **可复现型**：较为完整的项目制作复现过程。
  * **炫耀型**：无详细的项目复现过程，但是项目展示效果吸引人。
  * Bug 解决经验型：解决了某个难题的过程和具体解决方法分享。
* [MaixPy 官方论坛](https://maixhub.com/discussion/maixpy)（提问和交流）
* QQ 群： （建议在 QQ 群提问前先发个帖，方便群友快速了解你需要了什么问题，复现过程是怎样的）
  * MaixPy (v4) AI 视觉交流大群: 862340358
* Telegram: [MaixPy](https://t.me/maixpy)。
* 商业合作或批量购买请联系 support@sipeed.com 。

