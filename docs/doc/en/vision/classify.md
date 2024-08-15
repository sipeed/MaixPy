---
title: Using AI Models for Object Classification in MaixCAM MaixPy
---

## Object Classification Concept

For example, if there are two images in front of you, one with an apple and the other with an airplane, the task of object classification is to input these two images into an AI model one by one. The model will then output two results, one for apple and one for airplane.

## Using Object Classification in MaixPy

MaixPy provides a pre-trained `1000` classification model based on the `imagenet` dataset, which can be used directly:

```python
from maix import camera, display, image, nn

classifier = nn.Classifier(model="/root/models/mobilenetv2.mud", dual_buff = True)
cam = camera.Camera(classifier.input_width(), classifier.input_height(), classifier.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_string(10, 10, msg, image.COLOR_RED)
    dis.show(img)
```

Result video:

<video playsinline controls autoplay loop muted preload src="https://wiki.sipeed.com/maixpy/static/video/classifier.mp4" type="video/mp4">
Classifier Result video
</video>

Here, the camera captures an image, which is then passed to the `classifier` for recognition. The result is displayed on the screen.

For more API usage, refer to the documentation for the [maix.nn](/api/maix/nn.html) module.

## dual_buff Dual Buffer Acceleration

You may have noticed that the model initialization uses `dual_buff` (which defaults to `True`). Enabling the `dual_buff` parameter can improve running efficiency and increase the frame rate. For detailed principles and usage notes, see [dual_buff Introduction](./dual_buff.md).

## Training Your Own Classification Model

Please go to [MaixHub](https://maixhub.com) to learn and train classification models. When creating a project, select `Classification Model`.
