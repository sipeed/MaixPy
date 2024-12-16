---
title: MaixCAM MaixPy 识别 Apriltag 标签
update:
  - date: 2024-04-03
    author: lxowalle
    version: 1.0.0
    content: 初版文档
---

阅读本文前，确保已经知晓如何开发MaixCAM，详情请阅读[快速开始](../README.md)

## 简介

本文介绍如何使用MaixPy来识别Apriltag标签

## 使用 MaixPy 识别Apriltag标签

MaixPy的 `maix.image.Image`中提供了`find_apriltags`方法，可以可以识别apriltag标签。

### 如何识别Apriltag标签

一个简单的示例，实现识别apriltag标签并画框

```python
from maix import image, camera, display

cam = camera.Camera()
disp = display.Display()

families = image.ApriltagFamilies.TAG36H11
x_scale = cam.width() / 160
y_scale = cam.height() / 120

while 1:
    img = cam.read()

    new_img = img.resize(160, 120)
    apriltags = new_img.find_apriltags(families = families)
    for a in apriltags:
        corners = a.corners()

        for i in range(4):
            corners[i][0] = int(corners[i][0] * x_scale)
            corners[i][1] = int(corners[i][1] * y_scale)
        x = int(a.x() * x_scale)
        y = int(a.y() * y_scale)
        w = int(a.w() * x_scale)
        h = int(a.h() * y_scale)

        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        img.draw_string(x + w, y, "id: " + str(a.id()), image.COLOR_RED)
        img.draw_string(x + w, y + 15, "family: " + str(a.family()), image.COLOR_RED)

    disp.show(img)
```

步骤：

1. 导入image、camera、display模块

   ```python
   from maix import image, camera, display
   ```

2. 初始化摄像头和显示

   ```python
   cam = camera.Camera()
   disp = display.Display()
   ```

3. 从摄像头获取图片并显示

   ```python
   while 1:
       img = cam.read()
       disp.show(img)
   ```

4. 调用`find_apriltags`方法识别摄像头图片中的apriltag标签

   ```python
   new_img = img.resize(160, 120)
   apriltags = new_img.find_apriltags(families = families)
   ```

   - `img`是通过`cam.read()`读取到的摄像头图像
   - `img.resize(160, 120)`是用来将图像缩放得更小，用更小的图像来让算法计算得更快
   - `new_img.find_apriltags(families = families)`用来寻找apriltag标签，并将查询结果保存到`apriltags`，以供后续处理。其中families用来选择apriltag族，默认为`image.ApriltagFamilies.TAG36H11`

5. 处理识别标签的结果并显示到屏幕上

   ```python
   for a in apriltags:
       # 获取位置信息（并映射坐标到原图）
       x = int(a.x() * x_scale)
       y = int(a.y() * y_scale)
       w = int(a.w() * x_scale)
       corners = a.corners()
       for i in range(4):
           corners[i][0] = int(corners[i][0] * x_scale)
           corners[i][1] = int(corners[i][1] * y_scale)
   
       # 显示
       for i in range(4):
           img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
           img.draw_string(x + w, y, "id: " + str(a.id()), image.COLOR_RED)
           img.draw_string(x + w, y + 15, "family: " + str(a.family()), image.COLOR_RED)
           img.draw_string(x + w, y + 30, "rotation : " + str(180 * a.rotation() // 3.1415), image.COLOR_RED)
   ```
   
   - 遍历`apriltags`的成员，`apriltags`是通过`img.find_apriltags()`扫描apriltag标签的结果，如果找不到标签则`apriltags`的成员为空
   - `x_scale`和`y_scale`用来映射坐标，由于`new_img`是缩放后的图像，计算apriltag的坐标时需要经过映射后才能正常的画在原图`img`上
   - `a.corners()`用来获取已扫描到的标签的四个顶点坐标，`img.draw_line()`利用这四个顶点坐标画出标签的形状
   - `img.draw_string`用来显示标签的内容，其中`a.x()`和`a.y()`用来获取标签左上角坐标x和坐标y，`a.id()`用来获取标签的id，`a.family()`用来获取标签族类型，`a.rotation()`用来获取标签的旋转角度。

### 常用参数说明

列举常用参数说明，如果没有找到可以实现应用的参数，则需要考虑是否使用其他算法实现，或者基于目前算法的结果扩展所需的功能


| 参数     | 说明                                                         | 示例                                                         |
| -------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| roi      | 设置算法计算的矩形区域，roi=[x, y, w, h]，x，y表示矩形区域左上角坐标，w，h表示矩形区域的宽度和高度，默认为整张图片 | 计算坐标为(50,50)，宽和高为100的区域<br />```img.find_apriltags(roi=[50, 50, 100, 100])``` |
| families | apriltag标签家族类型                                         | 扫描TAG36H11家族的标签<br />```img.find_apriltags(families = image.ApriltagFamilies.TAG36H11)``` |

本文介绍常用方法，更多 API 请看 API 文档的 [image](../../../api/maix/image.md) 部分。



### 测量摄像头与物体的距离

这里提供一种使用`distance=k/width`的公式来测距, 其中`distance`是摄像头和物体的距离,单位`mm`, `k`是一个常量, `width`是物体在画面中的宽度,单位是像素点. 

测量方法分两步: 1. 测量常量系数k; 2. 通过常量系数和标签宽度来计算物体与摄像头的距离

#### 前期准备

1. `apriltag`标签纸
2. 尺子(或其他测距工具)

#### 测量常量系数k

- 将`apriltag`标签纸固定,并在距离`apriltag`标签20cm处固定`maixcam`

- 使用`maixcam`检测`apriltag`标签并计算标签的宽度, 参考代码:

    ```python
    from maix import camera, display
    import math

    '''
    x1,y1,x2,y2: apriltag宽度的两点坐标, 一般通过corners()方法获取
    返回标签的宽度,单位为像素点
    '''
    def caculate_width(x1, y1, x2, y2):
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) 

    cam = camera.Camera(160, 120)
    disp = display.Display()

    while 1:
        img = cam.read()

        apriltags = img.find_apriltags()
        for a in apriltags:
            corners = a.corners()

            # 通过水平方向的两个坐标点计算宽度
            width = caculate_width(corners[0][0], corners[0][1], corners[1][0], corners[1][1])
            # 打印apriltag标签的实际宽度
            print(f'apriltag width:{width}')
        disp.show(img)
    ```

- 计算常量系数k

    ```python
    '''
    width: 当距离为distance时,检测到apriltag标签的宽度
    distance: 检测apriltag标签时距离apriltag标签的实际距离, 单位mm
    返回常量系数
    '''
    def caculate_k(width, distance):
        return width * distance
    
    # 距离200mm时检测到标签宽度为43个像素
    k = caculate_k(43, 200)
    ```

#### 通过常量系数计算摄像头和物体间的距离

```python
'''
width: apriltag标签的宽度
k: 常量系数
返回摄像头与物体的距离,单位mm
'''
def caculate_distance(width, k):
    return k / width

distance = caculate_distance(55, 8600)
```

#### 完整的代码参考:

```python
from maix import camera, display, image
import math

'''
x1,y1,x2,y2: apriltag宽度的两点坐标, 一般通过corners()方法获取
返回标签的宽度,单位为像素点
'''
def caculate_width(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2) 

'''
width: 当距离为distance时,检测到apriltag标签的宽度
distance: 检测apriltag标签时距离apriltag标签的实际距离, 单位mm
返回常量系数
'''
def caculate_k(width, distance):
    return width * distance

'''
width: apriltag标签的宽度
k: 常量系数
返回摄像头与物体的距离,单位mm
'''
def caculate_distance(width, k):
    return k / width


cam = camera.Camera(192, 108)
disp = display.Display()

# 距离200mm时检测到标签宽度为43个像素
k = caculate_k(43, 200)

while 1:
    img = cam.read()

    apriltags = img.find_apriltags()
    for a in apriltags:
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_GREEN)

        # 通过水平方向的两个坐标点计算宽度
        width = caculate_width(corners[0][0], corners[0][1], corners[1][0], corners[1][1])

        # 计算距离
        distance = caculate_distance(width, k)

        print(f'apriltag width:{width} distance:{distance} mm')

    disp.show(img)

```

上面的方法是通过`apriltag`的宽度计算距离, 同样也可以扩展为使用高度来计算距离. 但需要注意该方法是在对距离估测, 实际应用中会有些许误差存在.
