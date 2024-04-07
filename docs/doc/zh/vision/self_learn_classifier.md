---
title: MaixPy 自学习分类器
---


## MaixPy 自学习分类器介绍

一般情况下我们要识别新的类别，需要在电脑端重新采集数据集并训练，步骤很麻烦，难度较高，这里提供一种不需要电脑端训练，而是直接在设备端就能秒学习新的物体，适合场景不太复杂的使用场景。

比如眼前有饮料瓶和手机，使用设备分别拍一张它们的照片作为两个分类的依据，然后再采集几张他们各个角度的照片，提取它们的特征保存，然后识别时根据图像的特征值分别和保存的特征值进行对比，和保存的哪个更相近就认为是对应的分类。


## MaixPy 中使用自学习分类器

步骤：
* 采集 n 张分类图。
* 采集 n*m 张图，每个分类采集 m 张，顺序无所谓。
* 启动学习。
* 识别图像输出结果。


简洁版本代码，完整版本请看例程里面的完整代码。
```python
from maix import nn, image

classifier = nn.SelfLearnClassifier(model="/root/models/mobilenetv2.mud", feature_layer=None)

img1 = image.load("/root/1.jpg")
img2 = image.load("/root/2.jpg")
img3 = image.load("/root/3.jpg")
sample_1 = image.load("/root/sample_1.jpg")
sample_2 = image.load("/root/sample_2.jpg")
sample_3 = image.load("/root/sample_3.jpg")
sample_4 = image.load("/root/sample_4.jpg")
sample_5 = image.load("/root/sample_5.jpg")
sample_6 = image.load("/root/sample_6.jpg")


classifier.add_class(img1)
classifier.add_class(img2)
classifier.add_class(img3)
classifier.add_sample(sample_1)
classifier.add_sample(sample_2)
classifier.add_sample(sample_3)
classifier.add_sample(sample_4)
classifier.add_sample(sample_5)
classifier.add_sample(sample_6)

classifier.learn()

img = image.load("/root/test.jpg")
max_idx, max_score = classifier.classify(img)
print(maix_idx, max_score)
```



