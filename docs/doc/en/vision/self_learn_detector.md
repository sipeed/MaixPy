---
title: MaixCAM MaixPy Self-learning Tracker
update:
  - date: 2024-04-03
    author: neucrack
    version: 1.0.0
    content: Initial version of the document
update:
  - date: 2025-09-03
    author: neucrack
    version: 1.1.0
    content: Added MixFormerV2 support
---

## MaixPy Self-learning Detection Tracker

Similar to the self-learning classifier, no training is required; simply select the target object with a bounding box to achieve detection and tracking. It is very useful in simple detection scenarios.
Unlike the self-learning classifier, since this is a detector, it provides the coordinates and size of the object.

There are also other names, such as SOT (Single Object Tracking) and MOT (Multiple Object Tracking). We classify all of them under the self-learning detection tracker. Currently, MaixPy supports two SOT algorithms, but of course, you can also port or create more algorithms yourself. Hopefully, this can serve as inspiration.

<video playsinline controls autoplay loop muted preload src="/static/video/self_learn_tracker.mp4" style="width: 100%; min-height: 20em;"></video>

## Using the Self-learning Detection Tracker in MaixPy

Currently, MaixPy provides a single-object learning detection tracking algorithm, meaning you start by selecting the target object, and it will continuously track that object.
The algorithms used here are [NanoTrack](https://github.com/HonglinChu/SiamTrackers/tree/master/NanoTrack) and [MixFormerV2](https://github.com/MCG-NJU/MixFormerV2). Those interested in the principles can study them further.

You can flash the latest system image and directly use the built-in self-learning tracking application to see the results.

Different devices support different models, and different algorithms have their own characteristics, as shown in the table below:

| Model                 | NanoTrack                 | MixFormerV2                                                                            |
| --------------------- | ------------------------- | -------------------------------------------------------------------------------------- |
| Features              | Lightweight, fast runtime | Slightly slower than NanoTrack, supports online update, better recognition performance |
| Sub-category          | SOT                       | SOT                                                                                    |
| MaixCAM / MaixCAM-Pro | ✅<br>                     | ❌                                                                                      |
| MaixCAM2              | ❌                         | ✅<br>Model runs at 38fps<br>Full pipeline 640x480 at 33fps                             |

### NanoTrack

Use the `maix.nn.NanoTrack` class. After initializing the object, first call the `init` method to specify the target, then call the `track` method to continuously track the target. Simplified code is as follows:

```python
from maix import nn

model_path = "/root/models/nanotrack.mud"
tracker = nn.NanoTrack(model_path)
tracker.init(img, x, y, w, h)
pos = tracker.track(img, threshold=0.9)
```

Here, the target features are learned from a specified `x,y,w,h` region in one image, and then the `track` function is called on a new image to get the target’s position.

For detailed code, see [MaixPy/examples/vision/ai\_vision/nn\_self\_learn\_tracker.py](https://github.com/sipeed/MaixPy/blob/main/examples/vision/ai_vision/nn_self_learn_tracker.py)

> Note: This uses a built-in model already included under `/root/models` in the system. You can also download models from [MaixHub Model Zoo](https://maixhub.com/model/zoo/437).

### MixFormerV2

Use the `maix.nn.MixFormerV2` class. After initializing the object, first call the `init` method to specify the target, then call the `track` method to continuously track the target. Simplified code is as follows:

```python
from maix import nn

model_path = "/root/models/nanotrack.mud"
tracker = nn.MixFormerV2(model_path, update_interval = 200, int lost_find_interval = 60)
tracker.init(img, x, y, w, h)
pos = tracker.track(img, threshold=0.5)
```

Similar to `NanoTrack`, the target features are learned from a specified `x,y,w,h` region in one image, and then the `track` function is called on a new image to get the target’s position.
The difference here is that two additional parameters are provided:

* **update\_interval**: Updates the target every `update_interval` frames while keeping the initial target. Both the updated and initial targets are input together to produce the result. This ensures adaptation if the target changes, such as angle variation.
* **lost\_find\_interval**: A simple built-in lost-target recovery algorithm. If the target is not found for more than `lost_find_interval` frames, it automatically expands the search area to try to find it.

For detailed code, see [MaixPy/examples/vision/ai\_vision/nn\_self\_learn\_tracker.py](https://github.com/sipeed/MaixPy/blob/main/examples/vision/ai_vision/nn_self_learn_tracker.py)

## Lost Target Recovery

For both `NanoTrack` and `MixFormerV2`, recognition is based on a search region. For example, in a 1920x1080 image, if the initial target is only 100x50 pixels, the detection is not done across the whole 1920x1080 image but rather within an expanded region cropped around the target. In the video above, you can see the search region box drawn around the target.

The problem is that if the target is occluded or disappears for some time and then reappears outside the search region, it cannot be detected. The target is still in the frame, but the algorithm cannot find it. In this case, a recovery algorithm is needed. The official `NanoTrack` and `MixFormerV2` do not provide recovery, but MaixPy’s implementation of `MixFormerV2` includes a simple recovery algorithm. By setting the `lost_find_interval` parameter, it will automatically attempt a global search after losing the target.

## Other Self-learning Tracking Algorithms and Optimizations

This article serves as inspiration by providing a few algorithms. If you have better algorithms and optimizations, you can refer to the existing NanoTrack / MixFormerV2 implementations to create your own. Contributions and discussions are also welcome.
