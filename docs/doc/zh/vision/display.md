---
title: MaixPy 屏幕使用
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
img.draw_rectangle(0, 0, disp.width(), disp.height(), color=image.Color.from_rgb(255, 0, 0), thickness=-1)
img.draw_rectangle(10, 10, 100, 100, color=image.Color.from_rgb(255, 0, 0))
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


## 显示到 MaixVision

在使用 MaixVision 运行代码时，能够将图像显示到 MaixVision 上，方便调试和开发。

在调用`show`方法时，会自动压缩图像并发送到 MaixVision 显示。

当然，如果你没有屏幕，或者为了节省内存不想初始化屏幕，也可以直接调用`image.Image`对象的`send_to_maixvision`方法发送图像到 MaixVision 显示。
```python
from maix import image

img = image.Image(320, 240)
img.draw_rectangle(0, 0, img.width(), img.height(), color=image.Color.from_rgb(255, 0, 0), thickness=-1)
img.draw_rectangle(10, 10, 100, 100, color=image.Color.from_rgb(255, 0, 0))
img.draw_string(10, 10, "Hello MaixPy!", color=image.Color.from_rgb(255, 255, 255))
img.send_to_maixvision()
```

