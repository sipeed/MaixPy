---
title: MaixCAM MaixPy 摄像头使用
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
  - date: 2024-08-21
    author: YWJ
    version: 1.0.1
    content: 修正文档部分bug,增加部分内容
  - date: 2024-10-24
    author: neucrack
    version: 1.1.0
    content: 增加 USB 摄像头支持说明
---


## 简介

对于 MaixCAM 默认搭载了 GC4653 摄像头，或者可选的 OS04A10 摄像头或者全局快门摄像头，甚至是 HDMI 转 MIPI 模块，都可以直接用简单的 API 调用。

## API 文档

本文介绍常用方法，更多 API 使用参考 [maix.camera](/api/maix/camera.html) 模块的文档。

## 摄像头切换

目前支持的摄像头：
* **GC4653**：M12 通用镜头, 1/3" 传感器，画质清晰， 4M 像素。
* **OS04A10**：M12 通用镜头，1/1.8" 大底传感器，画质超清， 4M像素。
* **OV2685**：不支持镜头更换，1/5"传感器，2M 像素，画质最差，成本最低，一般不建议使用。
* **SC035HGS**：黑白全局快门摄像头，30W黑白像素，适合拍摄高速物体。

系统会自动切换，只接硬件换上即可使用。


## 获取摄像头的图像信息

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

GC4653最大支持`2560x1440 30fps`、`1280x720 60fps`和`1280x720 80fps`三种配置，由创建`Camera`对象时传入的`width`，`height`，`fps`参数来选择帧率。

OS04A10最大支持`2560x1440 30fps`、`1280x720 90fps`两种配置，其中`1280x720`是基于`2560x1440`居中裁剪的画面

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
4. 摄像头需要看体制，有些体制无法设置到80fps，会出现画面有奇怪的纹路，请换会正常的 60fps使用。

## 图像矫正

对于画面存在鱼眼等畸变的情况，可以使用`Image`对象下的`lens_corr`函数对图片进行畸变矫正。一般情况只需要调大和调小`strength`的值来将画面调整到合适效果即可。

```python
from maix import camera, display,app,time

cam = camera.Camera(320, 240)
disp = display.Display()
while not app.need_exit():
    t = time.ticks_ms()
    img = cam.read() 
    img = img.lens_corr(strength=1.5)	# 调整strength的值直到画面不再畸变
    disp.show(img)

```

注意由于是软件矫正，需要耗费一定时间，另外也可以只接用无畸变镜头（询问商家）从硬件层面解决。


## 跳过 开头的帧

摄像头初始化的一小段时间，可能图像采集还没稳定出现奇怪的画面，可以通过`skip_frames`函数跳过开头的几帧：
```python
cam = camera.Camera(640, 480)
cam.skip_frames(30)           # 跳过开头的30帧
```

## 显示摄像头获取的图像

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
### 更改图片长宽

```python
cam = camera.Camera(width=640, height=480)
```
或

```python
cam = camera.Camera()
cam.set_resolution(width=640, height=480)
```

### 读取原始raw图

注意输出的`raw`图是原始的`bayer`图，并且不同摄像头模组输出的`bayer`图格式可能不一样。

```python
cam = camera.Camera(raw=true)
raw_img = cam.read_raw()
print(raw_img)
```

如果需要在第三方软件打开`raw`图，需要额外在PC端进行转换，可以参考[bayer_to_tiff](https://github.com/sipeed/MaixPy/blob/dev/examples/tools/bayer_to_tiff.py)的示例代码

## 使用 USB 摄像头

除了使用开发板自带的 MIPI 接口摄像头，你也可以使用 USB 外接 USB 摄像头。
方法：
* 先在开发板设置里面`USB设置`中选择`USB 模式`为`HOST`模式。如果没有屏幕，可以用`examples/tools/maixcam_switch_usb_mode.py`脚本进行设置。
* `maix.camera` 模块目前(2024.10.24) 还不支持 USB 摄像头，不过你可以参考 [OpenCV 使用 USB 摄像头](./opencv.md)。

