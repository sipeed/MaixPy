---
title: MaixCAM MaixPy 屏幕使用
update:
  - date: 2024-03-31
    author: neucrack
    version: 1.0.0
    content: 初版文档
---


## 简介

MaixPy 提供了`display`模块，可以将图像显示到屏幕上，同时，也可以将图像发送到 MaixVision 显示，方便调试和开发。

## API 文档

本文介绍常用方法，更多 API 请看 API 文档的 [display](/api/maix/display.html) 部分。


## 使用屏幕

* 导入`display`模块：
```python
from maix import display
```

* 创建一个`Display`对象：
```python
disp = display.Display()
```

* 显示图像：
```python
disp.show(img)
```

这里`img`对象是`maix.image.Image`对象，可以通过`camera`模块的`read`方法获取，也可以通过`image`模块的`load`方法加载文件系统中的图像，也可以通过`image`模块的`Image`类创建一个空白图像。

比如：
```python
from maix import image, display

disp = display.Display()
img = image.load("/root/dog.jpg")
disp.show(img)
```
这里需要先把`dog.jpg`文件传到设备的`/root`目录下。


显示文字：
```python
from maix import image, display

disp = display.Display()
img = image.Image(320, 240)
img.draw_rect(0, 0, disp.width(), disp.height(), color=image.Color.from_rgb(255, 0, 0), thickness=-1)
img.draw_rect(10, 10, 100, 100, color=image.Color.from_rgb(255, 0, 0))
img.draw_string(10, 10, "Hello MaixPy!", color=image.Color.from_rgb(255, 255, 255))
disp.show(img)
```

从摄像头读取图像并显示：
```python
from maix import camera, display, app

disp = display.Display()
cam = camera.Camera(320, 240)
while not app.need_exit():
    img = cam.read()
    disp.show(img)
```

> 这里用了一个`while not app.need_exit():` 是方便程序在其它地方调用`app.set_exit_flag()`方法后退出循环。

## 调整背光亮度

在系统的`设置`应用中可以手动调整背光亮度，如果你想在程序中调整背光亮度，可以使用`set_backlight`方法，参数就是亮度百分比，取值范围是 0-100：
```python
disp.set_backlight(50)
```

注意，程序退出回到应用选择界面后会自动恢复到系统设置的背光亮度。

> 如果亮度设置到 `100%` 仍然觉得暗，可以尝试修改`/boot/board`文件中的`disp_max_backlight=50`选项为更大的值，当`disp_max_backlight=100`并且`disp.set_backlight(100)`时硬件上背光控制引脚输出`100%`占空比即高电平。即最终输出到硬件的占空比 = `set_backlight 设置值` * `disp_max_backlight`。
> **注意**，修改最大亮度限制会带来功耗和发热量的上升，按照自己实际需求合理设置，不要盲目追求拉满亮度。


## 显示到 MaixVision

在使用 MaixVision 运行代码时，能够将图像显示到 MaixVision 上，方便调试和开发。

在调用`show`方法时，会自动压缩图像并发送到 MaixVision 显示。

当然，如果你没有屏幕，或者为了节省内存不想初始化屏幕，也可以直接调用`maix.dispaly`对象的`send_to_maixvision`方法发送图像到 MaixVision 显示。
```python
from maix import image,display

img = image.Image(320, 240)
disp = display.Display()

img.draw_rect(0, 0, img.width(), img.height(), color=image.Color.from_rgb(255, 0, 0), thickness=-1)
img.draw_rect(10, 10, 100, 100, color=image.Color.from_rgb(255, 0, 0))
img.draw_string(10, 10, "Hello MaixPy!", color=image.Color.from_rgb(255, 255, 255))
display.send_to_maixvision(img)
```

## 更换其它型号屏幕

如果想换不同尺寸的屏幕，可以到[商城](https://wiki.sipeed.com/store)咨询购买。
对于 MaixCAM，目前支持 4 款屏幕和 1 款 MIPI 转 HDMI 模块：
* 2.3寸 552x368 分辨率电容触摸屏： MaixCAM 带的屏幕。
* 2.4寸 640x480 分辨率电容触摸屏： MaixCAM-Pro 带的屏幕。
* 5寸 854x480 分辨率无触摸屏： 注意无触摸，类似手机屏幕大小。
* 7寸 1280x800 分辨率电容触摸屏：7寸大屏，适合更多需要固定屏幕观看场景。
* LT9611（MIPI转HDMI模块） 支持1280x720等多种分辨率，适合驱动各种HDMI屏。

不同屏幕的刷新图像时间差别在1～5毫秒，差别不是很大，主要的区别在于图像分辨率大了图像处理时间的差别。

更换屏幕需要同时**修改配置文件**，否则可能刷新时序不同会**导致烧屏**（屏幕留下显示过的影子），所以需要注意，最好严格按照下面的步骤操作，如果出现了烧屏的问题也不要紧张，断电放置一晚上一般会恢复。

* 按照烧录系统的文档烧录系统，烧录完成后会有 U 盘出现。
* 打开 U 盘内容，看到有一个 `board` 文件。
* 编辑`board`文件，修改`pannel`键值，取值如下：
  * 2.3寸（MaixCAM 自带屏幕）：`st7701_hd228001c31`。
  * 2.4寸（MaixCAM-Pro 自带屏幕）： `st7701_lct024bsi20`。
  * 5寸：`st7701_dxq5d0019_V0`  早期（2023年）测试屏幕`st7701_dxq5d0019b480854`。
  * 7寸：`mtd700920b`，早期（2023年）测试屏幕用 `zct2133v1`。
  * LT9611（MIPI转HDMI模块）：
    * 接线：
      * LT9611 I2C <---> MaixCAM I2C5
      * LT9611 MIPI IN <---> MaixCAM MIPI OUT
    * 支持的配置
      * `lt9611_1280x720_60hz`: 1280x720 60Hz
      * `lt9611_1024x768_60hz`: 1024x768 60Hz
      * `lt9611_640x480_60hz`:  640x480  60Hz
      * `lt9611_552x368_60hz`:  552x368  60Hz
* 保存`board`，并且**点击弹出 U 盘**，不要直接断电，否则可能文件丢失。
* 按下板子的`reset`按键，或者重新上电启动。


以上的方式最保险，保证上电前已经设置好了屏幕型号，如果你已经烧录好系统了，也可以修改系统的`/boot/board`文件然后重启。
> 早期的系统和二进制应用(< 2024.11.25)依赖的是`uEnv.txt`里面的`panel`键值，如果系统和应用比较老旧，修改了`board` 也可以同时将`uEnv.txt`中一同修改。
