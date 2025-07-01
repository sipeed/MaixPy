---
title: MaixVision -- MaixCAM MaixPy 编程 IDE + 图形化积木编程
---


## 简介

[MaixVision](https://wiki.sipeed.com/maixvision) 是专为 Maix 生态打造的一款开发者编程工具，支持 MaixPy 编程和图形化积木编程，同时支持在线运行和调试，以及实时预览图像，可以同步设备显示屏的图像，方便调试和开发。

以及支持打包应用和安装应用到设备，方便用户一键生成、安装应用。

同时还集成一些方便开发的小工具，比如文件管理，阈值编辑器，二维码生成等等。

## 下载

访问 [MaixVision 主页](https://wiki.sipeed.com/maixvision) 下载。


## 使用 MaixPy 编程和在线运行

按照[快速开始](../README.md)的步骤连接设备，我们可以很方便地使用 MaixPy 编程和在线运行。

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


## 代码自动补全


代码提示依赖电脑本地的 Python 包，为了实现代码提示，我们需要在电脑中安装 Python，并且安装需要提示的 Python 包。
> 不安装则会显示红色下划波浪线错误提示，代码仍然能在设备正常运行，只是编辑器没有代码补全提示。

* 安装 Python 请访问 [Python 官网](https://python.org/)安装。
* 安装需要提示的包，比如对于 MaixPy， 你需要在电脑也安装一份 MaixPy 包，在电脑使用`pip install MaixPy`即可安装好，如果`MaixPy`更新了，你也需要在电脑和设备更新到`MaixPy`，电脑手动在终端执行`pip install MaixPy -U`即可，设备更新直接在`设置`应用中更新即可。
> 中国国内用户可以使用国内镜像`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple MaixPy`。
* 重启 MaixVision 就能够看到代码提示了。
> 如果仍然不能提示，可以手动在设置中设置 python 可执行文件的路径后重启。

>! 注意在电脑安装 Python 包这里只是为了用作代码提示，实际代码运行还是在设备（开发板）上，设备上也要有对应的包才能正常运行。


> 另外，虽然你在电脑上安装了 MaixPy 包，但是由于我们精力有限，我们不确保你能直接在电脑的 Python 导入 maix 包进行使用，请在支持的设备上运行。


另外，除了 MaixPy 软件包，其它的代码提示，比如 `numpy/opencv` 都同样的需要在电脑也安装一份来实现代码提示。

## 运行单文件

在编写代码时，一般两种模式，执行单个文件，或者执行一个完成项目（包含多个 py 文件或者其它资源文件比如图片/模型等）。
对于简单的代码，我们**一个文件就能包含所有代码**，直接创建或者打开一个 `.py`格式的文件，编辑后点击左下角运行即可执行代码。

## 创建项目（多个 py 文件项目/模块化）

对于稍微复杂一点的程序，比如代码多了，需要模块化，或者需要在应用里包含一些资源文件比如图片/模型等，就需要建立项目了。

* 在系统文件管理器创建一个空文件夹，MaixVision 点击`打开文件夹/项目`打开这个空文件夹。或者直接点击新建项目（如果新版本有这个功能）。
* 创建一个`main.py`的主程序入口（名字必须是`main.py`），如果`main.py`想引用其它`.py`文件，在项目文件夹下建立一个`.py`文件比如`a.py`
```python
def say_hello():
  print("hello from module a")
```
* 在 `main.py` 中引用
```python
from a import say_hello
say_hello()
```
* 运行项目，点击左下角`运行项目`按钮将整个项目文件夹所有文件自动打包发送到设备中运行。
* 如果你打开了一个文件夹/项目，仍想单独运行某个文件，可以打开想要运行的文件，然后点击左下角`运行当前文件`只发送当前文件到设备运行，注意不会发送其它文件到设备，所以不要引用其它`.py`文件。


## 计算图像的直方图

在上一步中我们可以在 MaixVision 中实时看到图像，我们用鼠标框选一个区域，图像下方就能看到这个区域的直方图了，选择不同的颜色表示方法，可以看到不同的颜色通道的直方图。

这个功能方便我们在做某些图像处理算法时找到一些合适的参数。

## 区分`设备文件系统`和`电脑文件系统`

这里我们有一个比较重要的概念需要掌握：**分清楚`设备文件系统`和`电脑文件系统`**。
* **电脑文件系统**：运行在电脑上，在 MaixVision 中打开文件或者工程都是打开的电脑里面的文件（比如 C 盘 D 盘等），保存也是自动保存到电脑的文件系统。
* **设备文件系统**：程序运行时会将程序发送到设备上运行，所以代码里面读取的文件都是从设备文件系统读取。

所以常见的问题是有同学在电脑上保存了文件`D:\data\a.jpg`，然后在设备上使用这个文件`img = image.load("D:\data\a.jpg")`，这样当然是找不到文件的，因为设备上没有`D:\data\a.jpg`这个文件。

正确的方法是：
* 用`MaixVision`的文件管理器将这个文件从电脑上传到设备的`/root/`目录下。参考后文。
* 代码加载设备文件系统内的文件`img = image.load("/root/a.jpg")`。



## 传输文件到设备

先连接设备，然后点击浏览设备文件系统的按钮，有两个入口，如下图，然后就能上传文件到设备，或者从设备下载文件到电脑了。

![maixvision_browser2](../../assets/maixvision_browser2.jpg)

![maixvision_browser](../../assets/maixvision_browser.jpg)


.. details::也可以用其它工具代替，点击展开
    先知道设备的 ip 地址或者设备名称，MaixVision 就可以搜索到, 或者在设备`设置->系统信息`中看到，比如类似 `maixcam-xxxx.local` 或者 `192.168.0.123`。
    用户名和密码都是 `root`, 使用 `SFTP` 协议传输文件，端口号是 `22`。

    然后不同系统下都有很多好用的软件：

    ### Windows 下

    使用 [WinSCP](https://winscp.net/eng/index.php) 或者 [FileZilla](https://filezilla-project.org/) 等工具连接设备，将文件传输到设备上，选择 `SFTP` 协议填写设备和账号信息连接即可。

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

    * **方法二**：使用 [FileZilla](https://filezilla-project.org/) 等工具连接设备，将文件传输到设备上，选择 `SFTP` 协议填写设备和账号信息连接即可。

## 打包应用和安装应用到设备

使用 MaixPy + MaixVison 可以方便地开发、打包、安装应用，方便离线运行：
* 在 MaixVision 中使用 MaixPy 开发应用程序，可以是单个文件，也可以是一个工程目录。
* 连接设备。
* 点点击 MaixVision 左下角的 安装 按钮，会弹出一个界面填写应用的基本信息，id 是用来判别应用的 id，一个设备不能同时安装相同 id 的不同应用，所以 id 应该与 MaixHub 上面已经有的应用 id 不同，应用名字可以重复。以及图标等。
* 点击打包应用，会将应用打包成一个安装包，如果你要上传到 [MaixHub 应用商店](https://maixhub./com/app)，用这个打包好的文件即可。
* 点击 安装应用，这会将打包好的应用安装到设备。
* 断开与设备的连接，就能看到设备功能选择界面多了一个你的应用，直接点进去就能运行。

> 如果你用 MaixCDK 开发，使用 `maixcdk relrease` 就能打包出来一个应用，具体看 MaixCDK 的文档。

## 终端使用

MaixVision 支持直接操作设备的终端，点击右侧`设备终端`按钮即可打开。
当然你也可以使用第三方的 shell 工具，比如系统自带的终端使用`ssh`工具连接。


## 使用图形化积木编程

开发中，敬请期待。

