---
title: MaixCAM MaixPy 条形码识别
update:
  - date: 2024-12-16
    author: lxowalle
    version: 1.0.0
    content: 初版文档
              
---

阅读本文前，确保已经知晓如何开发MaixCAM，详情请阅读[快速开始](../README.md)

## 简介

本文介绍如何使用MaixPy来识别条形码


## 使用 MaixPy 识别条形码

MaixPy的 `maix.image.Image`中提供了`find_barcodes`方法，用来识别条形码

### 如何识别条形码

一个简单的示例，实现识别条形码并画框

```python
from maix import image, camera, display

cam = camera.Camera(480, 320)
disp = display.Display()

while 1:
    img = cam.read()

    barcodes = img.find_barcodes()
    for b in barcodes:
        rect = b.rect()
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE, 2)
        img.draw_string(0, 0, "payload: " + b.payload(), image.COLOR_GREEN)

    disp.show(img)
```

步骤：

1. 导入image、camera、display模块

   ```python
   from maix import image, camera, display
   ```

2. 初始化摄像头和显示

   ```python
   cam = camera.Camera(480, 320) # 初始化摄像头，输出分辨率480x320 RGB格式
   disp = display.Display()
   ```

3. 从摄像头获取图片并显示

   ```python
   while 1:
       img = cam.read()
       disp.show(img)
   ```

4. 调用`find_barcodes`方法识别摄像头中的条形码

   ```python
   barcodes = img.find_barcodes()
   ```

   - `img`是通过`cam.read()`读取到的摄像头图像，当初始化的方式为`cam = camera.Camera(320, 240)`时，`img`对象是一张分辨率为480x320的RGB图。
   - `img.find_barcodes`用来寻找条形码，并将查询结果保存到`barcodes`，以供后续处理
   - 注意: 条形码的间距较小, 并且一般宽度远大于高度, 所以在调整识别率和识别速度时可以尽量让识别目标图像的宽度更大, 高度更小

5. 处理识别条形码的结果并显示到屏幕上

   ```python
   for b in barcodes:
       rect = b.rect()
       img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_BLUE, 2)
       img.draw_string(0, 0, "payload: " + b.payload(), image.COLOR_GREEN)
   ```
   
   - `barcodes`是通过`img.find_barcodes()`查询条形码的结果，如果找不到条形码则`barcodes`内部为空
   - `b.rect()`用来获取已扫描到的条形码的位置和大小，`img.draw_rect()`利用这些位置信息画出条形码的形状
   - `img.draw_string`用来显示条形码的内容和位置等信息，`b.payload()`用来获取条形码的内容

### 常用参数说明

列举常用参数说明，如果没有找到可以实现应用的参数，则需要考虑是否使用其他算法实现，或者基于目前算法的结果扩展所需的功能

| 参数 | 说明                                                         | 示例                                                         |
| ---- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| roi  | 设置算法计算的矩形区域，roi=[x, y, w, h]，x，y表示矩形区域左上角坐标，w，h表示矩形区域的宽度和高度，默认为整张图片 | 计算坐标为(50,50)，宽和高为100的区域<br />```img.find_barcodes(roi=[50, 50, 100, 100])``` |

本文介绍常用方法，更多 API 请看 API 文档的 [image](../../../api/maix/image.md) 部分。