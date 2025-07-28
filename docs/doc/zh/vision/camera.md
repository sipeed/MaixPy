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
  - date: 2025-07-28
    author: neucrack & lxo
    version: 1.2.0
    content: 添加 AWB 和镜头使用文档。
---


## 简介

对于 MaixCAM 默认搭载了 GC4653 摄像头，或者可选的 OS04A10 摄像头或者全局快门摄像头，甚至是 HDMI 转 MIPI 模块，都可以直接用简单的 API 调用。

## API 文档

本文介绍常用方法，更多 API 使用参考 [maix.camera](/api/maix/camera.html) 模块的文档。

## 摄像头切换

目前支持的摄像头：
* **GC4653**：M12 通用镜头, 1/3" 传感器，画质清晰， 4M 像素。适合常见场景，比如AI识别、图像处理等。
* **OS04A10**：M12 通用镜头，1/1.8" 大底传感器，画质超清， 4M像素。适合对画质有要求的场景，比如拍照、视频录制等，注意发热量也会更大。
* **OV2685**：不支持镜头更换，1/5"传感器，2M 像素，画质最差，成本最低，一般不建议使用。
* **SC035HGS**：黑白全局快门摄像头，30W黑白像素，适合拍摄高速物体。

系统会自动切换，只接硬件换上即可使用。

## 镜头盖

镜头盖遮灰尘用，**请先取下镜头盖！！**再使用。

## 摄像头调焦距

对于 MaixCAM，默认配的是**手动调焦镜头**，物理上拧镜头可以实现调整焦距。
如果你发现**画面模糊**，可以尝试拧镜头（顺时针和逆时针进行尝试）来对焦使画面清晰。

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


## 设置摄像头的分辨率

代码中直接指定宽高即可：

```python
from maix import camera
cam = camera.Camera(width=640, height=480)
```
或

```python
from maix import camera
cam = camera.Camera()
cam.set_resolution(width=640, height=480)
```

### 分辨率大小选择

不同板子和摄像头模组支持的分辨率不同，首先请使用偶数分辨率值。

重要的一点需要明确，分辨率不是越高越高，根据使用场景选择合适的分辨率。
* 拍照/摄影/监控: 这种场景我们可能希望更大分辨率更清晰。
  GC4653和OS04A10最大支持`2560x1440`分辨率，也就是 `2K/4M像素`，不过更大分辨率对编程能力和内存要求更高，可以稍微用小一点的分辨率比如`1920x1080`，`1280x720`，`640x480`等。
  注意：使用 `MaixVision` 在线运行代码，如果设置了很高的分辨率（例如`2560x1440`），需要关闭 MaixVision 的图像预览功能，否则可能会因为内存不足导致代码运行异常。
* AI 识别 / 图像处理：为了让模型和算法运行更快，我们需要在能识别到的情况下尽量降低分辨率。
  * `640x480`：VGA 分辨率，对于 AI 和算法来说是比较大的分辨率了，能满足大部分 AI 识别和图像**清晰处理**的需求。对于 MaixCAM 很多算法比较吃力，对于 MaixCAM2 则比较轻松。
  * `320x320`：正方形，适合一些 AI 模型，但是一般屏幕是长方形的，显示起来两边会有黑边。
  * `320x240`: QVGA 分辨率，对于 AI 和视觉算法来说比较容易运算，同时也能满足大部分清晰度要求。
  * `320x224`: 宽高都是 32 的倍数，比较适合想要分辨率小，同时适合 AI 模型输入，同时宽高比和 MaixCAM 自带的屏幕 `552x368` 比较相近的分辨率方便显示。
  * `224x224`：正方形，宽高都是 32 的倍数，比较适合想要分辨率小，同时适合 AI 模型输入，比如 `MobileNetV2`，`MobileNetV3` 等模型输入。

### 分辨率宽高比

分辨率宽高比会影响视野范围，比如传感器最大是`2560x1440`，即`16:9`的宽高比，使用`640x480`分辨率时，宽高比变成了`4:3`，视野范围会变小，如果你想要视野最大化，则建议使用和传感器相同的分辨率比例，比如`1280x720`，`2560x1440`等。

一般宽高比不同，会对画面进行居中裁剪。


## 设置摄像头的帧率

摄像头会设置在特定的帧率下工作，MaixPy 支持设置摄像头的帧率。不同摄像头模组支持的帧率不同。


| GC4653 | OS04A10 | OV2685 | SC035HGS |
|--------|---------|--------|----------|
| 2560x1440@30fps<br>1280x720@60fps<br>1280x720@80fps | 2560x1440@30fps<br>1280x720@80fps | 1920x1080@30fps | 640x480@180fps|


由创建`Camera`对象时传入的`width`，`height`，`fps`参数来选择帧率。


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
4. 摄像头需要看体制，有些体制无法设置到80fps，会出现画面有奇怪的纹路，请换回正常的60fps使用。

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

注意由于是软件矫正，运行需要耗费一定时间，另外也可以只接用无畸变镜头（询问商家）从硬件层面解决。


## 跳过 开头的帧

摄像头初始化的一小段时间，可能图像采集还没稳定出现奇怪的画面，如果你不想画面看到这些画面，可以通过`skip_frames`函数跳过开头的几帧或者刚开始读取的图像不用就好了：
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

注意设置曝光时间后，摄像头会切换到手动曝光模式，如果要切换回自动曝光模式需运行`cam.exp_mode(camera.AeMode.Auto)`

```python
from maix import camera
cam = camera.Camera()
cam.exposure(1000)
```

### 设置增益

注意设置增益后，摄像头会切换到手动曝光模式，如果要切换回自动曝光模式需运行`cam.exp_mode(camera.AeMode.Auto)`。自定义的增益值只能在手动曝光模式下生效。

```python
from maix import camera
cam = camera.Camera()
cam.gain(100)
```

### 设置白平衡

一般情况下自动白平衡就足够了，某些特殊情况，比如检测颜色，或者拍摄特定颜色的物体时，可能需要手动设置白平衡来防止颜色偏差。

目前只支持通过设置增益来手动设置白平衡, 先用`cam.awb_mode(camera.AwbMode.Manual)` 禁用自动白平衡，然后通过 `set_wb_gain()` 传入一个长度为4的数组，分别对应`R`,`Gr`,`Gb`,`B`的增益值, 范围为 `[0.0, 1.0]`。
这里有一个默认增益值，可以基于这个值调整：
* `MaixCAM`: `[0.134, 0.0625, 0.0625, 0.1239]`
* `MaixCAM2`: `[0.0682, 0, 0, 0.04897]`

通常只需要调整`R`通道和`B`通道, `Gr`和`Gb`通道可以保持不变

```python
from maix import camera
cam = camera.Camera()
cam.awb_mode(camera.AwbMode.Manual)			# AwbMode.Auto,开启自动白平衡, AwbMode.Manual,开启手动白平衡;
cam.set_wb_gain([0.134, 0.0625, 0.0625, 0.1239])  # 设置r, gr, gb, b四个通道的增益
```

### 设置更低抓图延时

通过设置buff_num来减小抓图的延时, 需要注意修改该参数会改变图片缓存大小,降低后可能会导致图像丢失的情况.
对于maixcam, 由于内部软件框架的限制, 即使设置buff_num为1, 实际至少还是会存在一个双缓存, 测试取图延时最低在30+ms左右
```python
from maix import camera
cam = camera.Camera(buff_num=1)         # 只使用1个缓存
```

### 设置亮度、对比度和饱和度

```python
from maix import camera
cam = camera.Camera()
cam.luma(50)		    # 设置亮度，范围[0, 100]
cam.constrast(50)		# 设置对比度，范围[0, 100]
cam.saturation(50)		# 设置饱和度，范围[0, 100]
```


### 读取原始raw图

在某些特殊场景你可能需要读取摄像头的原始`bayer`图像数据，比如需要进行图像处理或者调试等。可以通过设置`raw=true`来读取原始图像数据。

注意不同摄像头模组输出的`bayer`图格式可能不一样。

```python
from maix import camera
cam = camera.Camera(raw=true)
raw_img = cam.read_raw()
print(raw_img)
```

如果需要在第三方软件打开`raw`图，需要额外在PC端进行转换，可以参考[bayer_to_tiff](https://github.com/sipeed/MaixPy/blob/dev/examples/tools/bayer_to_tiff.py)的示例代码

## 更换镜头

MaixCAM 默认配备了 M12 通用镜头，支持更换镜头。更换镜头时请注意以下几点：
1. 确保新镜头是 M12 接口的镜头。
2. 不同镜头的法兰距（镜头到传感器的距离）不同，自带的镜头座子高度固定的（mm），购买镜头时请确认镜头的法兰距是否适合 MaixCAM 的座子和传感器（不懂可以问商家）。
3. 更换镜头时注意不要刮花或者弄赃传感器表面，否则会严重影响图像质量，如果有毛发灰尘掉上去，可以用气吹轻轻吹掉，吹不掉再考虑用镜头纸轻轻擦拭。
4. 是否可以用变焦镜头？可以，买 M12 接口的变焦镜头即可。
5. 默认都是手动对焦镜头，如果你想用自动对焦，需要购买支持自动对焦的镜头，注意 MaixCAM 的摄像头接口没有自动对焦电路，所以可能需要你自己写程序控制对焦电机。


## 使用 USB 摄像头

除了使用开发板自带的 MIPI 接口摄像头，你也可以使用 USB 外接 USB 摄像头。
方法：
* 先在开发板设置里面`USB设置`中选择`USB 模式`为`HOST`模式。如果没有屏幕，可以用`examples/tools/maixcam_switch_usb_mode.py`脚本进行设置。
* `maix.camera` 模块目前(2024.10.24) 还不支持 USB 摄像头，不过你可以参考 [OpenCV 使用 USB 摄像头](./opencv.md)。

