---
title: MaixPy 摄像头使用
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
---


## 简介

对于 MaixCAM 默认搭载了 GC4653 摄像头，或者可选的 OS04A10 摄像头或者全局快门摄像头，甚至是 HDMI 转 MIPI 模块，都可以直接用简单的 API 调用。

## API 文档

本文介绍常用方法，更多 API 使用参考 [maix.camera](/api/maix/camera.html) 模块的文档。

## 摄像头切换

不同的摄像头使用不同的驱动，需要在系统中选择正确的驱动。

TODO：如何切换摄像头，比如 GC4653 和 OS04A10 之间的切换。


## 从摄像头获取图像

使用 MaixPy 轻松获取：
```python
from maix import camera

cam = camera.Camera(640, 480)

while 1:
    img = cam.read()
    print(img)
```

这里我们从`maix`模块导入`camera`模块，然后创建一个`Camera`对象，指定图像的宽度和高度。然后在一个循环中不断读取图像， 默认出的图为`RGB`格式，如果需要`BGR`格式，其它格式请看 API 文档。

你还可以获取灰度图像

```python
from maix import camera, image
cam = camera.Camera(640, 480, image.Format.FMT_GRAYSCALE)	# 设置输出灰度图像
```

还可以获取NV21图像

```python
from maix import camera, image
cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)	# 设置输出NV21图像
```

注意：如果设置了很高的分辨率（例如`2560x1440`）时需要关闭MaixVision的在线浏览功能，否则可能会因为内存不足导致代码运行异常。

## 设置摄像头的帧率

目前摄像头支持`30fps`、`60fps`和`80fps`三种配置，由创建`Camera`对象时传入的`width`，`height`，`fps`参数来选择帧率，目前`60/80fps`下最大支持分辨率`1280x720`， `30fps`下最大支持分辨率`2560x1440`。

### 设置帧率为30帧

```python
from maix import camera
cam = camera.Camera(640, 480, fps=30)			# 设置帧率为30帧
# or
cam = camera.Camera(1920, 1280)             # 分辨率高于1280x720时帧率会设置为30帧
```

### 设置帧率为60帧

```python
from maix import camera
cam = camera.Camera(640, 480, fps=60)	        # 设置帧率为60帧
# or
cam = camera.Camera(640, 480)                  # 分辨率低于或等于1280x720时帧率会设置为80fps
```

### 设置帧率为80帧

```python
from maix import camera
cam = camera.Camera(640, 480, fps=80)	        # 设置帧率为80帧
```

注意：

1. 如果`Camera`传入的尺寸大于`1280x720`，例如写成`camera.Camera(1920, 1080, fps=60)`，此时`fps`参数将会失效，帧率将保持在`30fps`。
2. `60/80fps`与`30fps`的画面相比会有几个像素的偏移，在对视角有严格要求的应用下需要注意修正偏移。
3. 需要注意由于`60/80fps`和`30fps`共用了`isp`配置，在某些环境下两种帧率下的画面画质会存在一些偏差。

## 图像矫正

对于画面存在鱼眼等畸变的情况，可以使用`Image`对象下的`lens_corr`函数对图片进行畸变矫正。一般情况只需要调大和调小`strength`的值来将画面调整到合适效果即可。

```python
from maix import camera, display

cam = camera.Camera(320, 240)
disp = display.Display()
while not app.need_exit():
    t = time.ticks_ms()
    img = cam.read() 
    img = img.lens_corr(strength=1.5)	# 调整strength的值直到画面不再畸变
    disp = display.Display()
```

TODO：支持硬件畸变矫正

## 跳过 开头的帧

摄像头初始化的一小段时间，可能图像采集还没稳定出现奇怪的画面，可以通过`skip_frames`函数跳过开头的几帧：
```python
cam = camera.Camera(640, 480)
cam.skip_frames(30)           # 跳过开头的30帧
```

## 显示图像

MaixPy 提供了`display`模块，可以方便的显示图像：
```python
from maix import camera, display

cam = camera.Camera(640, 480)
disp = display.Display()

while 1:
    img = cam.read()
    disp.show(img)
```

## 设置摄像头参数

### 设置曝光时间

注意设置曝光时间后，摄像头会切换到手动曝光模式，如果要切换回自动曝光模式需运行`cam.exp_mode(0)`

```python
cam = camera.Camera()
cam.exposure(1000)
```

### 设置增益

注意设置增益后，摄像头会切换到手动曝光模式，如果要切换回自动曝光模式需运行`cam.exp_mode(0)`。自定义的增益值只能在手动曝光模式下生效。

```python
cam = camera.Camera()
cam.gain(100)
```

### 设置白平衡

```python
cam = camera.Camera()
cam.awb_mode(1)			# 0,开启白平衡;1,关闭白平衡
```

### 设置亮度、对比度和饱和度

```python
cam = camera.Camera()
cam.luma(50)		    # 设置亮度，范围[0, 100]
cam.constrast(50)		# 设置对比度，范围[0, 100]
cam.saturation(50)		# 设置饱和度，范围[0, 100]
```



