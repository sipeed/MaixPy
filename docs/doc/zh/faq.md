---
title: MaixCAM MaixPy FAQ(常见问题)
---

>! 此页面列出了 MaixPy 相关的常见问题和解决方案，如果你遇到了问题，请先在这里找寻答案。
> 另外还有其它途径：
> * [MaixHub 讨论版块](https://maixhub.com/discussion): 交流讨论，支持红包打赏。
> * [MaixPy issue](https://github.com/sipeed/MaixPy/issues?q=): 源码相关问题。
> * [MaixCAM 硬件 FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html): MaixCAM 硬件常见问题。

## MaixVision 无法搜索到设备？

先确认连接方式是 WiFi 还是 USB 线，
**WiFi**:
* 确认 WiFi 是否正确连接上并且获取到 IP 地址， 可以在 `设置->设备信息` 或者`设置->WiFi` 里面看到 `ip`。

**USB线**:
* 确保设备通过 Type-C 数据线连接到电脑，设备处于开机状态并且进入了功能选择界面。
* 确保设备驱动已经安装：
  * Windows 下可以在`设备管理器`中查看是否有 USB 虚拟网卡设备，如果有感叹号则是去动没有安装好，按照[快速开始](./README.md) 中的方法安装驱动即可。
  * Linux 下可以通过`ifconfig`或者`ip addr`查看是否有`usb0`设备或者`lsusb`查看所有 USB 设备。 Linux 已经自带去动，所以识别不到检查硬件连接，设备系统是否是最新，以及设备是否已经正常启动即可。
  * Mac OS 同 Linux 方法，或者在`系统设置` -> `网络` 里面看有没有 usb 网卡。
* 另外 检查 USB 线缆的质量，换一个高质量的线缆。
* 另外 检查电脑 USB 口的质量，比如实测某些小主机 USB 口 EMI 设计太糟糕，外接一个质量好点的 USB HUB 反而可以使用了，也可以换 USB 口 或者直接换台电脑。

## MaixVision 运行摄像头例程显示图像卡顿

默认配的 GC4653 摄像头最高帧率为 30 帧，摄像头例程正常情况下 MaixVision 的显示肉眼不会有卡顿感，如果卡顿，首先考虑传输问题：
* 检查网络连接质量，比如 WiFi。
* 如果用的 USB 连接，检查 USB 线质量， 电脑 USB 口质量，可以尝试换台电脑或者 USB 口 或者 USB 线缆尝试对比。

## MaixVision MacOS 无法运行

对于 MacOS，由于前期还没有用开发者账号签名，可能会遇到 提示权限不足或者文件损坏问题，
请参考[这里](https://maixhub.com/discussion/100301) 解决（在终端中执行命令sudo xattr -dr com.apple.quarantine /Applications/应用名称.app来移除这个属性）。


## 此产品适合量产吗

答案：适合。
* 软件上使用 Python 即可稳定运行，方便开发也可靠。
* 软件上另外支持和 MaixPy 相同 API 的 C++ SDK（MaixCDK），满足高效率和稳定要求。
* 硬件上提供各种形式的 PCB 和外壳，核心板和整板都有，芯片供货稳定，如果有量产需求可以联系 support@sipeed.com 咨询。
* 量大价更优。

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

## 通过 USB 连接了电脑和 MaixCAM 为什么电脑没有出现串口？

MaixCAM 的 USB 口是芯片的 USB2.0 接口，不是 USB 转串口接口，所以插上电脑不会出现串口，这是正常现象。
没有 USB 转串口怎么通信呢？
默认 USB 会模拟出 USB 网卡，所以当你将 USB 插上电脑时会出现虚拟网卡，按照 [快速开始](./README.md) 中的说明可以使用 MaixVision 与 MaixCAM 通信实现代码运行、图像预览、文件管理等功能。
另外，因为 USB 模拟了网卡，所以你也可以用通用的 SSH 软件连接 MaixCAM，实现通信。
或者你也可以连接 WiFi 和电脑在同一个局域网下通信。

如果你要使用串口，分为两种情况：
1. 串口和电脑通信：需要自行购买任意一款 USB 转串口模块来连接电脑的 USB 和板子的串口（对于MaixCAM 是 UART0 的 A16(TX) 和 A17(RX) 引脚，或者连接 MaixCAM 套餐送的 USB 转接板引出的两个 TX RX 引脚，也是 A16 A17 引脚，是等效的）
2. 串口和其它 MCU/SOC 通信: 直接连接 MaixCAM 的 A16(TX)和 A17(RX) 到 单片机的 RX 和 TX 引脚即可。


## 红色屏幕，提示初始化显示失败，请查看FAQ

从子面意思可以看到是显示驱动初始化失败了。
MaixCAM 的底层的显示驱动目前（2024.7）是和摄像头驱动绑定在一起初始化的，所以遇到这个问题多半是摄像头驱动初始化失败了。
解决方法：
* 尝试更新到最新的系统，安装最新的运行库（重要！！！）因为运行库需要和系统里面的驱动配合工作，版本不一致可能会出错，所以更新到最新的镜像安装最新运行库即可一般就能解决。
* 有可能是多个进程一起企图占用驱动，最简单粗暴的方法就是重启。
* 硬件上摄像头连接有问题，检查摄像头硬件连接，以及摄像头是否损坏。


## Runtime、MaixPy、系统镜像有什么区别，我应该升级哪个？

* **Runtime** 是运行时环境，系统很多功能依赖这个，包括 MaixPy 也依赖此环境，遇到无法运行程序的问题首先联网检查更新这个。
* 系统镜像包含了基本的操作系统、硬件驱动、内置应用，以及 MaixPy 固件等，是基础环境，最好是保持最新, 特别是在[Release](https://github.com/sipeed/MaixPy/releases)页面中版本更新中提到了系统有更新，则强烈建议更新系统，因为有些 MaixPy 功能可能依赖系统里面的驱动。
> 更新系统会格式化所有之前的数据，更新前请备份好设备系统中有用的数据。
* **MaixPy** 是运行 MaixPy 程序的依赖库，如果不需要更新系统功能，以及更新日志中没有提到系统有重要更新比如驱动，那可以单独更新 MaixPy 即可，不过以防有驱动变化，最好是直接重新烧录系统。


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

## MaixVision import maix 显示红色波浪线 "maix" is not accessed

MaixVision 显示 `no maix moudle` `"maix" is not accessed` 或者 `Import "maix" could not be resolved`。

这是 MaixVision 的代码提示功能报错找不到 maix 模块。
这里需要搞清楚一个概念： MaixVision 的代码提示依赖的是电脑本地的 Python 包，代码运行依赖的设备端的 Python 包，所以要让 MaixVision 能够提示就要在电脑上也安装 Python 和 `MaixPy` 包。具体请看[MaixVision 使用文档](./basic/maixvision.md)。

## MaixVision 如何编写多个文件，一个文件导入另一个文件的代码

仔细阅读 [MaixVision 使用文档](./basic/maixvision.md)。


## MaixCAM 启动非常缓慢，甚至超过了 1 分钟，或者屏幕在闪动

多半是由于供电不足造成的， MaixCAM 需要 5v 150mA~500mA 左右的电压和点流，如果你遇到了这种现象，可以使用 USB 转 TTL 模块连接 MaixCAM 的串口到电脑，可以看到`Card did not respond to voltage select! : -110` 这样的字样，说明供电不足，换一个更加的稳定的供电设备即可。
对于 MaixCAM，在开机会有 400mA 的电流，待机且屏幕有显示需要 250mA，全速运行 AI 模型需要 400mA~500mA 的电流，所以保证电源的稳定性十分重要！

## MaixCAM 黑屏无法启动，或者卡在 LOGO 界面

参考[MaixCAM FAQ](https://wiki.sipeed.com/hardware/zh/maixcam/faq.html)

## MaixVision 启动程序一直“卡在“ start running ...

MaixVision 的日志输出窗口在开始启动程序是会打印一句`start running ...`代表程序开始发送到设备并开始执行，
后面再打印（输出）什么取决于你的程序，比如你调用了`print("hello")` 则会打印`hello`，如果你的程序没有任何打印那就不会有任何日志。。。
所以实际上不是卡住了，而是你的程序就没有输出过任何东西，自然也就不会显示任何日志了，可以尝试在自己的程序中加`print("xxx")`来打印，这也是我们调试程序最简单的方法。


## 为什么硬件有 256MB 内存，在系统里只能用 128MB 内存呢？

因为其它内存给底层驱动和内核预留了，用于摄像头、屏幕、硬件编解码、NPU 等驱动使用，可以通过 `cat /sys/kernel/debug/ion/cvi_carveout_heap_dump/summary` 看到驱动使用的内存（算能特有，叫 ION 内存），以及其它内存可以通过`cat /proc/meminfo`看到，如果你想调整内存分配，需要自己编译系统，修改系统的`LicheeRV-Nano-Buildbuild/boards/sg200x/sg2002_licheervnano_sd/memmap.py` 文件中的 `ION_SIZE` 来调整（看[定制系统文档](./pro/compile_os.md)）。


## 为什么无法安装运行库，提示错误 请求失败!

* 请保证设备已经成功连接到互联网，可以换一个手机热点试试。
* 确保系统镜像是烧录的最新的。
* 如果提示 DNS 解析失败，可能时网络 DNS 设置问题，可以换一个手机热点试试，或者手动修改 `/boot/resolv.conf`(只修改这个文件需要重启) 和 `/etc/resolv.conf`（修改了这个文件不用重启，重启就是把前者拷贝覆盖到这个文件）中的 DNS 服务器设置。
* 确保你是从 Sipeed 购买的正版 MaixCAM。
* 咨询客服，带上系统版本可以 device_key （可以连接上 MaixVision 点击断开连接按钮后看到，有屏幕的也可以在`系统设置->系统信息`中看到）

## 编译报错: type not registered yet?

```
from ._maix.peripheral.key import add_default_listener
ImportError: arg(): could not convert default argument into a Python object (type not registered yet?). #define
```

显示有对象没有定义成 python 对象，在 MaixPy 中一般是由于自动扫描API生成时的顺序问题造成的，比如在`a.hpp`中有一个`@maixpy`声明的`API`， 在`b.hpp` 中有另一个`API`而且参数使用了`a.hpp`中的定义，那么可以说`b.hpp`需要依赖`a.hpp`，但目前`MaixPy`的编译脚本不会做依赖关系扫描，所以需要在`MaixPy`项目中的`components/maix/headers_priority.txt`文件中手动指定一下，`a.hpp`在`b.hpp`前面扫描就可以了。

## MaixVision 画面有延迟

一般情况下应该是因为用了 WiFi 传输，信号不好时或者图像分辨率过大时就会有延迟。
解决方法就是：
* 更换有线方式连接，具体看快速入门文档。
* 减小图像分辨率，在代码中 `disp.show(img)` `img` 的分辨率小一点。

## 运行应用时提示: Runtime error: mmf vi init failed

提示信息的意思是摄像头初始化失败了，可能的原因有:1. 摄像头被其他应用占用了; 2. 摄像头没有排线松了; 3. 没有安装运行库

解决步骤：
1. 检查maixvision的程序和板子自带程序是否同时运行，确保只有一个地方占用摄像头(注：一般情况连接maixvision后板子自带的程序会主动退出)
2. 将摄像头排线取下来重新插一下
3. 更新最新的运行库

## 运行应用时提示：`maix multi-media driver released`或者`maix multi-media driver destroyed`

这不是错误日志，这是多媒体框架释放资源时的提示信息，一般在程序退出时会打印

## 为什么不能显示中文

默认只有英文字体，如果要显示中文，需要更换中文字体，具体请看[基本图像操作 中文支持和自定义字体 部分](./vision/image_ops.md#中文支持和自定义字体)


## 程序退出并提示 app exit with code: 1, log in /maixapp/tmp/last_run.log

这是因为程序出错异常退出了，需要尝试看日志来找到问题所在。
看日志方法：
* 方法一： 出错后立即查看 `/maixapp/tmp/last_run.log` 文件，查看方式：
  1. MaixVision 运行 `MaixPy/examples/tools/show_last_run_log.py` 代码查看。
  2. 在 ssh 终端中 `cat /maixapp/tmp/last_run.log` 查看。
* 方法二：
  * 先使用 MaixVision 连接上设备以让所有占用显示和摄像头的程序退出。
  * 然后通过 ssh 连接设备进入 ssh 终端，进入方法见[Linux 基础](./basic/linux_basic.md) 中描述。
  * 执行命令手动运行程序
    * 如果是 Python 程序 `cd /maixapp/apps/xxx && python main.py` 这里 `xxx`是出错应用的 ID。
    * 如果不是 Python 程序 `cd /maixapp/apps/xxx && ./xxx` 这里 `xxx`是出错应用的 ID。
  * 仔细查看日志看有没有报错，注意报错可能不在最后一行，可以从后往前仔细查找。
* 方法三：如果是 Python 编写的应用，使用 MaixVision 运行源码查看运行错误并修正，注意报错可能不在最后一行，可以从后往前仔细查找。


## 如何读写 SD/TF 卡，保存数据到 SD/TF 卡

MaixPy 基于 Linux 和 标准 Python3，操作系统在 SD/TF 卡上，同时文件系统也在 SD 卡上，保存和读取数据都从文件系统操作。
使用 Python 的标准 API 即可操作，比如读取文件：
```python
with open("/root/a.txt", "r") as f:
  content = f.read()
  print(content)
```

类似的，其它在文档中没介绍的功能可以尝试搜一艘是不是 Python 自带的库，可以直接调用。

## 取图时出现`camera read timeout`的错误

这可能是在取图时摄像头缓存的图片缓存区没有新图片,导致取图超时.大部分情况是由于读图太快, 或者有多个Camera通道在同时读图时会遇到, 例如将一个Camera通道绑定到Rtsp服务后, 又在另一个线程从第二个Camera通道取图. 解决方法是捕获到异常后稍等片刻再次尝试取图, 参考代码:

```python
img = None
try:
    img = cam.read()
except:
    time.sleep_ms(10)
    continue
```

## 程序运行时出现 CVI_VENC_GetStream failed with 0xc0078012

这是因为上次程序没有正常退出，导致venc模块资源没有释放，再次启动应用就拿不到venc的资源了。 目前解决方法是：
1. 重启系统
2. 关掉maixvision的预览视图，或者切换到png流
由于这是底层框架上遗留的问题，目前只能从应用层解决，尽量保证程序正常的退出


## 如何卸载已经安装的应用

在开发板 `应用商店` 中可以直接卸载已经安装的应用，请看[应用使用文档](./basic/app.md)。

## 画面怎么很模糊，像加了高斯模糊一样

对于 MaixCAM， 镜头是需要手动对焦的，物理上拧镜头即可实现调焦。


## No module named 'lcd' 'sensor'，OpenMV 的代码如何移植/兼容 OpenMV 的代码

MaixPy (v4) 兼容了 OpenMV 和 MaixPy-v1 的代码，都放到了`maix.v1`模块下，比如 OpenMV 和 MaixPy-v1 中：
```python
import lcd, sensor
```

在 MaixPy (v4) 中：
```python
from maix.v1 import lcd, sensor
```

或者直接导入所有兼容包（不推荐，程序可读性变差）：
```python
from maix.v1 import *
import lcd, sensor
```

最新的 MaixPy 兼容 OpenMV/MaixPy-v1 的方式是在新 API 的基础上封装了一个兼容层，源码在[https://github.com/sipeed/MaixPy/tree/main/maix/v1](https://github.com/sipeed/MaixPy/tree/main/maix/v1)。
所以**强烈推荐升级到新的 MaixPy API**，API 更丰富而且更高效。
如果一定要用旧的 API 而且发现某个 API 官方没有实现，可以尝试修改上述源码支持，底层调用新的API即可，然后提交贡献到[https://github.com/sipeed/MaixPy](https://github.com/sipeed/MaixPy) 即可，方法可以参考[参与 MaixPy 项目文档](./source_code/contribute.md)


## MaixCAM 自带的相机 APP 拍摄的照片和视频存在哪儿，怎么导出到电脑

MaixCAM 自带的**相机**应用拍摄的照片和视频可以在自带的**相册**应用看到照片，点击`Info`按钮可以看到照片路径。
通过 [MaixVision 的文件管理功能](./basic/maixvision.md) 或者其它拷贝工具（比如scp 或者 winscp）即可拷贝到电脑上。


## 没有网络，文档有离线版本吗

有的。

提供 HTML 格式的离线文档，到[MaixPy release 页面](https://github.com/sipeed/MaixPy/releases) 找到`maixpy_v*.*.*_doc.zip` 下载。
解压后有`html`文件夹，保证电脑安装了`Python`，执行下面的`chmod +x ./view_doc.sh && view_doc.sh`(Linux/MacOS)或者`view_doc.bat`(Windows)。
然后访问`http://电脑IP:8000/maixpy/index.html`即可离线查看文档。

另外如果你只是想离线查看某一篇文档，你也可以在文档页面按`Ctrl+ P` 选择打印为 PDF 来保存单页面为 PDF到本地。
