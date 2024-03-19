
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

> 关于 MaixPy 介绍请看 [MaixPy 官网首页](../../README.md)

## 获得 MaixCAM 设备

在 [Sipeed 淘宝](https://sipeed.taobao.com) 或者 [Sipeed 速卖通](https://sipeed.aliexpress.com) 店铺购买 `MaixCAM` 开发板。

**建议购买带 `TF 卡`、`摄像头`、`2.3寸触摸屏`、`外壳`、`Type-C一转二小板`、`4P串口座子+线`的套餐**，方便后续使用和开发，后面的教程都默认你已经有了这些配件。

另外需要准备一根 `Type-C` 数据线，尽量买质量好点的防止供电和连接不稳定。


## 上手体验

插入套餐里面的 TF 卡，使用 `Type-C` 数据线连接 `MaixCAM` 设备给设备供电，等待设备开机，开机会显示 `MaixCAM` LOGO，然后进入功能选择界面。
> 如果屏幕没有显示，请咨询卖家。
> 如果你没有购买 TF 卡套餐，你需要按照[升级和烧录系统](./basic/os.md)的方法烧录最新的系统到 TF 卡。

开机后可以看到功能选择界面，在设置中可以切换语言，可以自行尝试内置的各种应用和功能。

## 作为串口模块使用

内置的各种应用可以直接当成串口模块使用，比如`找色块`、`找人脸`、`找二维码`等等，
> 如果是想把设备当成主控使用（或者你还不懂什么是串口模块）可以跳过这一步。

使用方法：
* 硬件连接： 可以给设备接上`Type-C一转二小板`，这样我们就能将设备通过串口连接到你的主控上了，比如`Arduino`、`树莓派`、`STM32`等等。
* 打开你想用的应用，比如二维码识别，当设备扫描到二维码就会通过串口把结果发送给你的主控了。
> 发送的串口波特率是 `115200`，数据格式是 `8N1`，协议遵循 [Maix 串口通信协议标准](https://wiki.sipeed.com/maixcdk/doc/convention/protoco.md)，可以在[MaixHub APP](https://maixhub.com/app) 找到对应的应用介绍查看协议。


## 开发环境准备

* 下载 [MaixVision](https://wiki.sipeed.com/maixvision) 并安装。 Linux 下推荐安装 deb 包。
* 使用 Type-C 连接设备和电脑，打开 MaixVision，点击左下角的`“连接”`按钮，会自动搜索设备，稍等一下就能看到设备，点击设备有点的连接按钮以连接设备。
> 如果找不到设备，请在[FAQ](./faq.md)中查找解决方法。
> 如果 USB 驱动确实没法安装，可以在设备设置里面连接和电脑同一局域网的 WiFi 即可。


## 运行例程

点击 MaixVision 左侧的`示例代码`，选择一个例程，点击左下角`运行`按钮将代码发送到设备上运行。

比如：
* `hello.py`，点击`运行`按钮，就能看到 MaixVision 终端有来自设备打印的`Hello MaixPy!`了。
* `camera_display.py`，这个例程会打开摄像头并在屏幕上显示摄像头的画面。
```python
from maix import camera, display, app

disp = display.Display()          # 构造一个显示对象，并初始化屏幕
cam = camera.Camera(640, 480)     # 构造一个摄像头对象，手动设置了分辨率为 640x480, 并初始化摄像头
while not app.need_exit():        # 一直循环，直到程序退出（可以通过按下设备上方的按键退出或者 MaixVision 点击停止按钮退出）
    img = cam.read()              # 读取摄像头画面保存到 img 变量，可以通过 print(img) 来打印 img 的详情
    disp.show(img)                # 将 img 显示到屏幕上
```
* `yolov5.py` 会检测摄像头画面中的物体框出来并显示到屏幕上，支持 80 种物体的检测。

其它例程可以自行尝试。

## 安装应用到设备

点击 MaixVision 左下侧的安装应用按钮，填写应用信息，会将应用安装到设备上，然后在设备上就能看到应用了。
也可以选择打包应用，将你的应用分享到[MaixHub 应用商店](https://maixhub.com/app)。

> 默认例程没有显式编写退出功能，进入应用后按下设备上方的按键即可退出应用。


## 下一步

看到这里，如果你觉得不错，务必来 [github](https://github.com/sipeed/MaixPy) 给 MaixPy 开源项目点一个 star, 你的 star 和认同是我们不断维护和完善的动力！

到这里你已经体验了一遍使用和开发流程了，接下来可以学习 MaixPy 语法和功能相关的内容，请按照左边的目录进行学习，如果遇到 API 使用问题，可以在[API 文档](/api/)中查找。

学习前最好带着自己学习的目的学，比如做一个有趣的小项目，这样学习效果会更好，项目和经验都可以分享到[MaixHub 分享广场](https://maixhub.com/share)，会获得现金奖励哦！

