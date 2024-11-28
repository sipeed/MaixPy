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
disp = display.Display()

while 1:
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_string(10, 10, msg, image.COLOR_RED)
    disp.show(img)
```

Result video:

<video playsinline controls autoplay loop muted preload src="/static/video/classifier.mp4" type="video/mp4">
Classifier Result video
</video>

Here, the camera captures an image, which is then passed to the `classifier` for recognition. The result is displayed on the screen.

For more API usage, refer to the documentation for the [maix.nn](/api/maix/nn.html) module.

## dual_buff Dual Buffer Acceleration

You may have noticed that the model initialization uses `dual_buff` (which defaults to `True`). Enabling the `dual_buff` parameter can improve running efficiency and increase the frame rate. For detailed principles and usage notes, see [dual_buff Introduction](./dual_buff.md).

## Training Your Own Classification Model on MaixHub

If you want to train a classification model for specific images, visit [MaixHub](https://maixhub.com) to learn and train the model. When creating a project, select "Classification Model", then simply upload your images to train. There's no need to set up a training environment or spend money on expensive GPUs—training can be done quickly with one click.

## Offline Training for Your Own Classification Model

For offline training, you need to set up your environment. Search for keywords such as `PyTorch classification model training` or `Mobilenet` for guidance.
After training the model, export it in ONNX format, then refer to the [MaixCAM Model Conversion Documentation](../ai_model_converter/maixcam.md) to convert it into a model format supported by MaixCAM. Finally, use the `nn.Classifier` class mentioned above to load the model.

The classification model can be Mobilenet or another model like ResNet. During model conversion, it's best to extract the layer just before `softmax` as the final output layer because the `classifier.classify(img, softmax=True)` function has `softmax` enabled by default—this means the function will perform a `softmax` calculation on the results. Therefore, the model itself doesn't need a `softmax` layer. However, if the model does include a `softmax` layer, you can specify not to execute it again by using: `classifier.classify(img, softmax=False)`.

