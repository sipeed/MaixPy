---
title: MaixCAM MaixPy 二维码识别
update:
  - date: 2024-04-03
    author: lxowalle
    version: 1.0.0
    content: 初版文档
              
---

阅读本文前，确保已经知晓如何开发MaixCAM，详情请阅读[快速开始](../README.md)

## 简介

本文介绍如何使用MaixPy来识别二维码


## 使用 MaixPy 识别二维码

MaixPy的 `maix.image.Image`中提供了`find_qrcodes`方法，用来识别二维码。

### 如何识别二维码

一个简单的示例，实现识别二维码并画框

```python
from maix import image, camera, display

cam = camera.Camera(320, 240)
disp = display.Display()

while 1:
    img = cam.read()
    qrcodes = img.find_qrcodes()
    for qr in qrcodes:
        corners = qr.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        img.draw_string(qr.x(), qr.y() - 15, qr.payload(), image.COLOR_RED)
    disp.show(img)
```

步骤：

1. 导入image、camera、display模块

   ```python
   from maix import image, camera, display
   ```

2. 初始化摄像头和显示

   ```python
   cam = camera.Camera(320, 240) # 初始化摄像头，输出分辨率320x240 RGB格式
   disp = display.Display()
   ```

3. 从摄像头获取图片并显示

   ```python
   while 1:
       img = cam.read()
       disp.show(img)
   ```

4. 调用`find_qrcodes`方法识别摄像头中的二维码

   ```python
   qrcodes = img.find_qrcodes()
   ```

   - `img`是通过`cam.read()`读取到的摄像头图像，当初始化的方式为`cam = camera.Camera(320, 240)`时，`img`对象是一张分辨率为320x240的RGB图。
   - `img.find_qrcodes`用来寻找二维码，并将查询结果保存到`qrocdes`，以供后续处理

5. 处理识别二维码的结果并显示到屏幕上

   ```python
   for qr in qrcodes:
       corners = qr.corners()
       for i in range(4):
           img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
       img.draw_string(qr.x(), qr.y() - 15, qr.payload(), image.COLOR_RED)
   ```

   - `qrcodes`是通过`img.find_qrcodes()`查询二维码的结果，如果找不到二维码则`qrcodes`内部为空
   - `qr.corners()`用来获取已扫描到的二维码的四个顶点坐标，`img.draw_line()`利用这四个顶点坐标画出二维码的形状
   - `img.draw_string`用来显示二维码的内容和位置等信息，其中`qr.x()`和`qr.y()`用来获取二维码左上角坐标x和坐标y，`qr.payload()`用来获取二维码的内容

### 常用参数说明

列举常用参数说明，如果没有找到可以实现应用的参数，则需要考虑是否使用其他算法实现，或者基于目前算法的结果扩展所需的功能

| 参数         | 说明                                                         | 示例                                                         |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| roi          | 设置算法计算的矩形区域，roi=[x, y, w, h]，x，y表示矩形区域左上角坐标，w，h表示矩形区域的宽度和高度，默认为整张图片 | 计算坐标为(50,50)，宽和高为100的区域<br />```img.find_qrcodes(roi=[50, 50, 100, 100])``` |
| qrcoder_type | 设置二维码库解码器类型，可以选择image.QRCodeDecoderType.QRCODE_DECODER_TYPE_ZBAR或者image::QRCodeDecoderType::QRCODE_DECODER_TYPE_QUIRC.  QRCODE_DECODER_TYPE_ZBAR在分辨率较小时识别速度更快，识别精度更高. QRCODE_DECODER_TYPE_QUIRC在分辨率较大时相对速度更快，但识别精度相对较低. 默认使用QRCODE_DECODER_TYPE_ZBAR.<br />v4.7.7及以后的版本有效. | img.find_qrcodes(decoder_type=image.QRCodeDecoderType.QRCODE_DECODER_TYPE_ZBAR) |

本文介绍常用方法，更多 API 请看 API 文档的 [image](../../../api/maix/image.md) 部分。

## 使用硬件加速的方法识别二维码

MaixPy内置了一个`image.QRCodeDetector`对象可以使用硬件加速的方法识别二维码，在320x224分辨率下单帧算法最高速度可以到60+fps

> 注：MaixPy v4.7.8之后的版本支持该方法（不包括v4.7.8）

### 使用方法

```python
from maix import camera, display, app, image

cam = camera.Camera(320, 224)
disp = display.Display()
detector = image.QRCodeDetector()

while not app.need_exit():
    img = cam.read()

    qrcodes = detector.detect(img)
    for q in qrcodes:
        img.draw_string(0, 0, "payload: " + q.payload(), image.COLOR_BLUE)

    disp.show(img)
```

步骤：

1. 导入image、camera、display模块

   ```python
   from maix import camera, display, app, image
   ```

2. 捕获和显示图像

   ```python
   cam = camera.Camera(320, 224)
   disp = display.Display()
   
   while not app.need_exit():
       img = cam.read()
       disp.show(img)
   ```

   - 创建`Camera`和`Display`对象，通过`cam.read()`方法来捕获图像，用`disp.show()`方法来显示图像

3. 创建`QRCodeDetector`对象来检测二维码

   ```python
   detector = image.QRCodeDetector()
   ```

4. 使用`detect`方法来检测二维码，检测结果保存到`qrcodes`变量中

   ```python
   qrcodes = detector.detect(img)
   for q in qrcodes:
       img.draw_string(0, 0, "payload: " + q.payload(), image.COLOR_BLUE)
   ```

   - 注意：检测过程中会占用NPU资源，如果此时有其他模型也再使用，则可能导致意外的结果
   - 检测的结果与`find_qrcodes`返回结果的数据结构一致，参考`QRCode`对象的方法来获取检测结果。例如：调用`q.payload()`即可获取二维码的内容字符串。
