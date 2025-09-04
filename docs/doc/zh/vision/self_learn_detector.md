---
title: MaixCAM MaixPy 自学习检测跟踪器
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: 初版文档
update:
  - date: 2025-09-03
    author: neucrack
    version: 1.1.0
    content: 增加 MixFormerV2 支持
---


## MaixPy 自学习检测跟踪器

和自学习分类器类似，不需要训练，直接框选目标物体即可实现检测并且跟踪物体，在简单检测场景下十分好用。
和自学习分类器不同的是因为是检测器，会有物体的坐标和大小。

另外也有其它的名字，比如 SOT(单目标追踪) 和 MOT(多目标追踪)，我们将其都归类到 自学习检测追踪器 里面了，目前 MaixPy 支持了两种 SOT 算法，当然你也可以自行移植或创造更多算法，希望能抛砖引玉。

<video playsinline controls autoplay loop muted preload src="/static/video/self_learn_tracker.mp4" style="width: 100%; min-height: 20em;"></video>

## MaixPy 中使用自学习检测跟踪器

在 MaixPy 目前提供了一种单目标学习检测跟踪算法，即开始框选目标物体，后面会一直跟踪这个物体。
这里使用的算法是[NanoTrack](https://github.com/HonglinChu/SiamTrackers/tree/master/NanoTrack) 和 [MixFormerV2](https://github.com/MCG-NJU/MixFormerV2)，有兴趣了解原理的可以自行学习。

可以烧录最新的系统镜像后直接使用内置的自学习跟踪应用看效果。

不同设备支持的模型不太样，以及不同算法各有特点，如下表：

| 模型 | NanoTrack | MixFormerV2 |
| ----------- | --- | --- |
| 特点    | 轻量，运行速度快 | 比 NaonoTrack 速度稍慢，支持在线更新，识别效果更好  |
| 子分类    | SOT  | SOT |
| MaixCAM / MaixCAM-Pro | ✅<br> | ❌  |
| MaixCAM2              | ❌ | ✅<br>模型运行 38fps<br>全流程 640x480 33fps |


### NanoTrack

使用`maix.nn.NanoTrack`类即可，初始化对象后，先调用`init`方法指定要检测的目标，然后调用`track`方法连续跟踪目标，以下为简化的代码：

```python
from maix import nn

model_path = "/root/models/nanotrack.mud"
tracker = nn.NanoTrack(model_path)
tracker.init(img, x, y, w, h)
pos = tracker.track(img, threshold=0.9)
```

这里先从一张图中指定`x,y,w,h` 目标位置学习目标特征，然后调用`tack`函数从新的图像中追踪目标获取到目标的位置。

具体详细代码请看[MaixPy/examples/vision/ai_vision/nn_self_learn_tracker.py](https://github.com/sipeed/MaixPy/blob/main/examples/vision/ai_vision/nn_self_learn_tracker.py)

> 注意这里使用了内置的模型，在系统`/root/models`下已经内置了，你也可以在[MaixHub 模型库](https://maixhub.com/model/zoo/437)下载到模型。


### MixFormerV2

使用`maix.nn.MixFormerV2`类即可，初始化对象后，先调用`init`方法指定要检测的目标，然后调用`track`方法连续跟踪目标，以下为简化的代码：

```python
from maix import nn

model_path = "/root/models/nanotrack.mud"
tracker = nn.MixFormerV2(model_path, update_interval = 200, int lost_find_interval = 60)
tracker.init(img, x, y, w, h)
pos = tracker.track(img, threshold=0.5)
```

和`NanoTrack`类似，这里先从一张图中指定`x,y,w,h` 目标位置学习目标特征，然后调用`tack`函数从新的图像中追踪目标获取到目标的位置。
不同的是，这里多提供了两个参数：
* **update_interval**: 每隔`update_interval`帧图更新一次目标，同时初始目标也会保留，更新后的目标和初始目标一起输入得到结果。这样就算目标有变化也能及时学习到，比如角度变化。
* **lost_find_interval**: 这是内置的一个简单的丢失找回算法，即超过`lost_find_interval`帧没找到数据后，会自动改变搜索区域尝试搜索。

具体详细代码请看[MaixPy/examples/vision/ai_vision/nn_self_learn_tracker.py](https://github.com/sipeed/MaixPy/blob/main/examples/vision/ai_vision/nn_self_learn_tracker.py)

## 丢失找回

对于 `NanoTrack` `MixFormerV2`，两者都是基于搜索区域的识别，比如一张图 1920x1080，初始目标只有 100x50 像素，实际检测不会检测整张1920x1080的图，会从目标附近按照一定比例扩大后裁切一部分作为识别区域进行识别。在上面的视频中也可以看到目标外围画出了搜索区域框。

所以问题是，当目标被遮挡或者消失一段时间后再从搜索区域外出现，就无法检测到目标，目标虽然在画面中，但是算法找不到，这个时候就需要一个找回算法，对于 `NanoTrack` `MixFormerV2` 算法官方没有提供找回，MaixPy 中`MixFormerV2`的实现提供了一个简单的找回算法，只要设置`lost_find_interval`参数就能在丢失目标后自动尝试全局搜索。


## 其它自学习跟踪算法和算法优化

本文抛砖引玉，提供了几个算法，如果有更好的算法和优化，可以自行参考已有的 NanoTrack / MixFormerV2 实现方式进行实现，也欢迎讨论或者提交代码PR。


