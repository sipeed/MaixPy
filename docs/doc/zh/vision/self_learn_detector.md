---
title: MaixCAM MaixPy 自学习检测跟踪器
---


## MaixPy 自学习检测跟踪器

和自学习分类器类似，不需要训练，直接框选目标物体即可实现检测并且跟踪物体，在简单检测场景下十分好用。
和自学习分类器不同的是因为是检测器，会有物体的坐标和大小。

<video playsinline controls autoplay loop muted preload src="/static/video/self_learn_tracker.mp4" style="width: 100%; min-height: 20em;"></video>

## MaixPy 中使用自学习检测跟踪器

在 MaixPy 目前提供了一种单目标学习检测跟踪算法，即开始框选目标物体，后面会一直跟踪这个物体。
这里使用的算法是[NanoTrack](https://github.com/HonglinChu/SiamTrackers/tree/master/NanoTrack)，有兴趣了解原理的可以自行学习。

可以烧录最新的系统镜像（>=2024.9.5_v4.5.0）后直接使用内置的自学习跟踪应用看效果。

使用`maix.nn.NanoTrack`类即可，初始化对象后，先调用`init`方法指定要检测的目标，然后调用`track`方法连续跟踪目标，以下为简化的代码：
```python
from maix import nn

model_path = "/root/models/nanotrack.mud"
tracker = nn.NanoTrack(model_path)
tracker.init(img, x, y, w, h)
pos = tracker.track(img)
```
注意这里使用了内置的模型，在系统`/root/models`下已经内置了，你也可以在[MaixHub 模型库](https://maixhub.com/model/zoo/437)下载到模型。

具体详细代码请看[MaixPy/examples/vision/ai_vision/nn_self_learn_tracker.py](https://github.com/sipeed/MaixPy/blob/main/examples/vision/ai_vision/nn_self_learn_tracker.py)


## 其它自学习跟踪算法

目前实现了 NanoTrack 算法，在简单场景非常稳定可靠，而且帧率足够高，缺点就是物体出视野再回来需要回到上次消失的附近才能检测到，以及只能检测一个目标。

如果有更好的算法，可以自行参考已有的 NanoTrack 实现方式进行实现，也欢迎讨论或者提交代码PR。

