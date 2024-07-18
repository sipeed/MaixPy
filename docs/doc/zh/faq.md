---
title: MaixPy FAQ(常见问题)
---

此页面列出了 MaixPy 相关的常见问题和解决方案，如果你遇到了问题，请先在这里找寻答案。
如果这个页面找不到答案，可以到 [MaixHub 讨论版块](https://maixhub.com/discussion) 将问题的详细步骤发贴提问。

如果你使用的是 MaixCAM, 也可以参考 [MaixCAM FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html)

## MaixVision 无法搜索到设备？

先确认连接方式是 WiFi 还是 USB 线，
**WiFi**:
* 确认 WiFi 是否正确连接上并且获取到 IP 地址， 可以在 `设置->设备信息` 或者`设置->WiFi` 里面看到 `ip`。

**USB线**:
* 确保设备通过 Type-C 数据线连接到电脑，设备处于开机状态并且进入了功能选择界面。
* 确保设备驱动已经安装：
  * Windows 下可以在`设备管理器`中查看是否有 USB 虚拟网卡设备，如果有感叹号则是去动没有安装好，按照[快速开始](./README.md) 中的方法安装驱动即可。
  * Linux 下可以通过`ifconfig`或者`ip addr`查看是否有`usb0`设备或者`lsusb`查看所有 USB 设备。 Linux 已经自带去动，所以识别不到检查硬件连接，设备系统是否是最新，以及设备是否已经正常启动即可。
  * Mac OS 同 Linux 方法。
* 另外 检查 USB 线缆的质量，换一个高质量的线缆。
* 另外 检查电脑 USB 口的质量，比如实测某些小主机 USB 口 EMI 设计太糟糕，外接一个质量好点的 USB HUB 反而可以使用了，也可以换 USB 口 或者直接换台电脑。

## MaixVision 运行摄像头例程显示图像卡顿

默认配的 GC4653 摄像头最高帧率为 30 帧，摄像头例程正常情况下 MaixVision 的显示肉眼不会有卡顿感，如果卡顿，首先考虑传输问题：
* 检查网络连接质量，比如 WiFi。
* 如果用的 USB 连接，检查 USB 线质量， 电脑 USB 口质量，可以尝试换台电脑或者 USB 口 或者 USB 线缆尝试对比。


## MaixPy v4 和 v1 v3 有什么区别？

* MaixPy v4 使用 Python 语言，是吸取了 v1 v3 经验的集大成之作，有更好的配套软件和生态，更多的功能，更简单的使用方式和更完善的文档；硬件有很大提升的同时加个和另外两者的硬件价格想当甚至更便宜；另外也做了兼容 K210 的使用体验和 API，方便用户从 v1 快速迁移到 v4。
* v1 使用了 Micropython 语言，有很多局限性，比如第三方库支持有限；同时受限于 Maix-I (K210) 的硬件性能，内存不够用，AI 模型支持有限，很多编解码不支持硬件加速等缺点。
* v3 也是使用了 Python 语言，基于 Maix-II-Dock (v831) 硬件，硬件 AI 模型支持有限，而且全志的基础生态不够开放，API 也不够完善，此版本仅作为 Maix-II-Dock (v831)上面使用，不会继续更新。

## MaixPy 目前只支持 MaixCAM 吗，用其它同款芯片的板子行不行？

MaixPy 目前仅支持 MaixCAM 系列板子，其它同款芯片的板子也不支持（包括 Sipeed 的同款芯片板子 比如 LicheeRV-Nano），强烈不建议尝试，导致设备损坏（比如冒烟烧屏等）后果自负。

未来 Sipeed 出的 Maix 系列的产品都将继续得到 MaixPy 支持，目前如果 MaixCAM 有什么无法满足的需求，可以到 [MaixHub 讨论版块](https://maixhub.com/discussion) 提出需求或者发送邮件到 support@sipeed.com.

## 可以用除了官方搭配的摄像头或者屏幕以外的自己的摄像头或者屏幕吗？

不建议这样操作，除非你有够丰富的软硬件知识和经验，否则可能导致设备损坏。

官方搭配的配件对应的软硬件是调教过的，表现效果是最好的，上手即可使用，其它配件可能接口不同，驱动不同，软件不同，需要自己去调教，这是一个非常复杂的过程，不建议尝试。

当然，如果你是大佬，我们也欢迎你提交 PR！


## 运行模型报错 cvimodel built for xxxcv181x CANNOT run on platform cv181x

解析模型文件失败了，一般情况是模型文件损坏造成的，确保你的模型文件是没有损坏的。
比如：
* 用编辑器编辑了二进制文件导致文件损坏。比如用 maixvision 打开了 cvimodel 文件，由于 maixvision 的自动保存功能会破坏二进制文件，所以不要用 maixvision 等文本编辑器打开二进制文件并保存（后面 MaixVision 会修复这个问题，即去掉 maixvision 的自动保存功能）。
* 如果是从网上下载的，保证下载没有出问题，一般网上的文件提供 sha256sum/md5 校验值，下载下来后可以对比一下，具体方法请自行搜索或者问 ChatGPT。
* 如果是来自压缩包，请确认解压过程没有出错，可以从压缩包重新解压一遍保证中间没有出错。
* 保证传输到设备的过程没有造成文件损坏，可以对比一下设备中的文件和电脑中的文件 sha256sum 值，具体方法请自性搜索或者问 ChatGPT。

## 上电启动黑屏，屏幕无显示

请看 [MaixCAM FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html)

## 红色屏幕，提示初始化显示失败，请查看FAQ

从子面意思可以看到是显示驱动初始化失败了。
MaixCAM 的底层的显示驱动目前（2024.7）是和摄像头驱动绑定在一起初始化的，所以遇到这个问题多半是摄像头驱动初始化失败了。
解决方法：
* 尝试更新到最新的系统，安装最新的运行库（重要！！！）因为运行库需要和系统里面的驱动配合工作，版本不一致可能会出错，所以更新到最新的镜像安装最新运行库即可一般就能解决。
* 硬件上摄像头连接有问题，检查摄像头硬件连接，以及摄像头是否损坏。


## Runtime、MaixPy、系统镜像有什么区别，我应该升级哪个？

* **Runtime** 是运行时环境，系统很多功能依赖这个，包括 MaixPy 也依赖此环境，遇到无法运行程序的问题首先联网检查更新这个。
* 系统镜像包含了基本的操作系统、硬件驱动、内置应用，以及 MaixPy 固件等，是基础环境，最好是保持最新, 特别是在[Release](https://github.com/sipeed/MaixPy/releases)页面中版本更新中提到了系统有更新，则强烈建议更新系统，因为有些 MaixPy 功能可能依赖系统里面的驱动。
> 更新系统会格式化所有之前的数据，更新前请备份好设备系统中有用的数据。
* **MaixPy** 是运行 MaixPy 程序的依赖库，如果不需要更新系统功能，以及更新日志中没有提到系统有重要更新比如驱动，那可以单独更新 MaixPy 即可。


## 加载 MUD 模型文件报错 *****.cvimodel not exists， load model failed

* 检查设备中（注意不是电脑里面，需要传到设备里面去）是否真的存在你加载的 .mud 文件。
* 检查你写的模型路径写错没有。
* 如果你改过文件名，需要注意： MUD 文件是一个模型描述文件，可以用文本编辑器编辑，实际的模型文件是 .cvimodel 文件（对于MaixCAM)，.mud 文件中指定了 .cvimodel 的文件名和路径，所以如果你改动了 `.cvimodel`的文件名，那么也要修改`.mud`文件中的`model`路径，比如这里 Yolov5 模型的 mud：
```ini
[basic]
type = cvimodel
model = yolov5s_224_int8.cvimodel

[extra]
model_type = yolov5
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
anchors = 10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```
这里制定了 `model` 为相对这个`.mud`文件目录的 `yolov5s_224_int8.cvimodel` 文件为模型文件，如果你改了`yolov5s_224_int8.cvimodel` 为其它名，那也需要改这里。

## MaixVision import maix 显示红色波浪线

这是 MaixVision 的代码提示功能报错找不到 maix 模块。
这里需要搞清楚一个概念： MaixVision 的代码提示依赖的是电脑本地的 Python 包，代码运行依赖的设备端的 Python 包，所以要让 MaixVision 能够提示就要在电脑上也安装 Python 和 `MaixPy` 包。具体请看[MaixVision 使用文档](./basic/maixvision.md)。

## MaixCAM 启动非常缓慢，甚至超过了 1 分钟，或者屏幕在闪动

多半是由于供电不足造成的， MaixCAM 需要 5v 150mA~500mA 左右的电压和点流，如果你遇到了这种现象，可以使用 USB 转 TTL 模块连接 MaixCAM 的串口到电脑，可以看到`Card did not respond to voltage select! : -110` 这样的字样，说明供电不足，换一个更加的稳定的供电设备即可。
对于 MaixCAM，在开机会有 400mA 的电流，待机且屏幕有显示需要 250mA，全速运行 AI 模型需要 400mA~500mA 的电流，所以保证电源的稳定性十分重要！