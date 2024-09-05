---
title: MaixCAM MaixPy Self-Learning Detection Tracker
---

## MaixPy Self-Learning Detection Tracker

Similar to the self-learning classifier, this tracker doesn't require training. You can simply select the target object by drawing a box around it, and the system will detect and track the object, making it quite useful in simple detection scenarios. Unlike the self-learning classifier, the detection tracker provides the coordinates and size of the object.

<video playsinline controls autoplay loop muted preload src="/static/video/self_learn_tracker.mp4" style="width: 100%; min-height: 20em;"></video>

## Using the Self-Learning Detection Tracker in MaixPy

MaixPy currently offers a single-target learning detection tracking algorithm. Once you select the target object, the tracker will continuously follow it. The algorithm used here is [NanoTrack](https://github.com/HonglinChu/SiamTrackers/tree/master/NanoTrack), which you can explore if you're interested in learning more about the underlying principles.

You can directly use the built-in self-learning tracking application after flashing the latest system image (>=2024.9.5_v4.5.0) to see the results.

To use it, call the `maix.nn.NanoTrack` class. After initializing the object, call the `init` method to specify the target to be detected, then call the `track` method to continuously track the target. Below is a simplified code example:
```python
from maix import nn

model_path = "/root/models/nanotrack.mud"
tracker = nn.NanoTrack(model_path)
tracker.init(img, x, y, w, h)
pos = tracker.track(img)
```
Note that this uses a built-in model located in the system at `/root/models`. You can also download the model from the [MaixHub model library](https://maixhub.com/model/zoo/437).

For more detailed code, refer to [MaixPy/examples/vision/self_learn_tracker.py](https://github.com/sipeed/MaixPy/tree/main/examples/vision/self_learn_tracker.py).

## Other Self-Learning Tracking Algorithms

Currently, the NanoTrack algorithm is implemented, which is highly stable and reliable in simple scenarios and provides a sufficient frame rate. However, its limitations include the need for the object to return near the last disappearance point to be detected again if it goes out of view, and the fact that it can only detect one target at a time.

If you have better algorithms, you can refer to the existing NanoTrack implementation for guidance. Feel free to discuss or submit code PRs.


