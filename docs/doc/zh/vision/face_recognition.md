---
title: MaixPy 人脸识别
---

## 人脸识别简介

人脸识别就是识别当前画面中的人脸的位置以及是谁。
所以人脸识别除了要检测到人脸，一般会有一个库来保存认识的人和不认识的人。

## 识别原理

* 使用 AI 模型检测人脸，获得坐标和五官的坐标。
* 利用五官的坐标仿射变换将图中的脸拉正对其到标准脸的样子，方便模型提取脸的特征。
* 使用特征提取模型提取脸的特征值。
* 与库中记录的人脸特征值进行对比（计算保存的和当前画面中的脸的特征值的余弦距离，得出最小的距离的库中的人脸，小于设定的阈值就认为当前画面中就是这个库中的人）


## MaixPy 使用

MaixPy maix.nn 模块中提供了人脸识别的 API， 可以直接使用，模型也内置了，也可以到 [MaixHub 模型库](https://maixhub.com/model/zoo) 下载（筛选选则对应的硬件平台，比如 maixcam）。


识别：

```python
from maix import nn

recognizer = nn.Face_Recognizer(model="/root/models/face_recognizer.mud")
if os.path.exists("/root/faces.bin"):
    recognizer.load_faces("/root/faces.bin")
cam = camera.Camera(recognizer.input_width(), recognizer.input_height(), recognizer.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    faces = recognizer.recognize(img)
    for obj in faces:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{recognizer.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

第一次运行这个代码会发现能检测到人脸，但是都不认识，需要我们进入添加人脸模式学习人脸才行。
比如可以在用户按下按键的时候学习人脸：
```python
faces = recognizer.detect_faces(img)
for face in faces:
    print(face)
    # 这里考虑到了一个画面中有多个人脸的情况
    # 可以在这里根据 face 的坐标决定要不要添加到库里面
    recognizer.add_face(face)
recognizer.save_(faces)("/too/faces.bin")
```




