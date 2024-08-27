---
title: MaixCAM MaixPy 物体轨迹追踪和计数（如人流计数）
---

## 轨迹追踪简介

前面我们使用 YOLOv5 YOLOv8 甚至是 find_blobs 都可以检测到物体，但是如果画面中同时存在多个物体，当我们需要区分每一个物体，就需要物体追踪功能了。

比如画面中同时有 5 个人在移动，我们需要给每个人编号，知道他们的行动轨迹。

应用：
* 人流计数，比如通过某个地段的人数量。
* 工件计数，比如流水线对生产的产品进行计数。
* 物体移动轨迹记录和识别。

## MaixCAM/MaixPy 物体追踪和人流计数效果

效果如下视频，可以跟踪每个人，以及对从上往下跨越黄色区域的人进行计数（左下角）：

<video playsinline controls autoplay loop muted preload src="/static/video/tracker.mp4" style="width: 100%; min-height: 20em;"></video>


## MaixCAM / MaixPy 使用 物体追踪和人流计数

可以参考直接安装[应用](https://maixhub.com/app/61) 体验。
可以看[examples/vision/tracker 下的例程](https://github.com/sipeed/MaixPy/tree/main/examples/vision/tracker)。

其中`tracker_bytetrack.py` 例程是基本的物体跟踪例程，分为几个步骤：
* 使用 YOLOv5 或者 YOLOv8 检测物体，这样你就可以根据你自己要检测的物体更换模型即可检测不同物体。
* 使用`maix.tracker.ByteTracker` 这个算法进行物体追踪，只需要调用一个`update`函数即可得到结果（画面中的每个轨迹），十分简单。

其中有几个参数根据自己的实际场景进行调整，具体参数以例程代码和 API 参数说明为准：
```python
# configs
conf_threshold = 0.3       # detect threshold
iou_threshold = 0.45       # detect iou threshold
max_lost_buff_time = 120   # the frames for keep lost tracks.
track_thresh = 0.4         # tracking confidence threshold.
high_thresh = 0.6          # threshold to add to new track.
match_thresh = 0.8         # matching threshold for tracking, e.g. one object in two frame iou < match_thresh we think they are the same obj.
max_history_num = 5        # max tack's position history length.
show_detect = False        # show detect
valid_class_id = [0]       # we used classes index in detect model。
```

`tracker_bytetrack_count.py` 例程则增加了人流计数例程，这里为了让例程更加简单，只简单地写了一个判断人从上往下走的计数，即当人处在黄色区域以下，同时轨迹在黄色区域内就认为是从上往下跨越了黄色区域。
实际在你的应用场景可以自己编写相关逻辑。
