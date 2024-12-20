---
title: Adding a New AI Model to MaixCAM MaixPy
update:
  - date: 2024-11-01
    author: neucrack
    version: 1.0.0
    content: Added migration documentation
---

## Introduction

Besides the built-in AI algorithms and models, MaixPy is highly extensible, allowing you to add your own algorithms and models.

Due to the prevalence of visual applications, this guide will be divided into sections for visual applications and other applications.


## If MaixPy Already Supports the Framework but the Dataset is Different

For instance, if MaixPy already supports YOLO11 detection, but your dataset is different, you only need to prepare your dataset, train the model, and export it.

Another quick and lazy method is to first search online to see if someone has already trained or open-sourced a model. If you find one, simply download it and convert the format for use, or continue training based on it. 

For example:
If you want to detect fire, a quick search online might lead you to the project [Abonia1/YOLOv8-Fire-and-Smoke-Detection](https://github.com/Abonia1/YOLOv8-Fire-and-Smoke-Detection), which shares a fire and smoke detection model based on YOLOv8. You can download it, export it to the ONNX format, and then convert it to a format supported by MaixPy.

You can also upload your model to the [MaixHub Model Library](https://maixhub.com/model/zoo) to share it with more people, or find models shared by others there.

## Adding Visual AI Models and Algorithms in Python

For visual applications, the usual task is image recognition, specifically:
* Input: Image
* Output: Any data, such as classification, probability, image, coordinates, etc.

In `MaixPy`, let’s use the common `YOLO11` detection algorithm as an example:

```python
from maix import nn, image

detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)

img = image.Image(detector.input_width(), detector.input_height(), detector.input_format())
objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
for obj in objs:
    img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
    msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
    img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
```

In this code, we first construct the `YOLO11` object to load the model, then pass an image to the `detect` method for recognition. The steps include:
* `nn.YOLO11()`: Initializes the object, loads the model into memory, and parses it.
* `detector.detect()`:
  * Preprocesses the image, usually standardizing it, such as `(value - mean) * scale`, adjusting pixel values to a suitable range like [0,1], which should match the preprocessing used during model training.
  * Runs the model, sending preprocessed data to the NPU for calculation following the model's network, producing output, typically floating-point data.
  * Postprocesses the output, transforming the model’s output into the final result.

To add a new model and algorithm, implement a similar class as `YOLO11`. Pseudocode example:

```python
class My_Model:
    def __init__(self, model: str):
      pass
      # Parses the model, potentially custom parsing from a MUD file

    def recognize(self, img: image.Image):
      pass
      # Preprocesses image
      # Runs model
      # Postprocesses output
      # Returns result
```

Using the `nn.NN` class, we can parse and run models; see the [API](http://127.0.0.1:2333/maixpy/api/maix/nn.html#NN) documentation for details.

Using `nn.NN`, we can parse our custom `mud` model description file, retrieve preprocessing values like `mean` and `scale`, and run the model with `nn.NN.forward_image()`. This method integrates preprocessing and running steps, reducing memory copy overhead for faster execution. For complex preprocessing, implement custom preprocessing, then run the model using `forward()` to get the output.

Here’s an example of implementing a classification model without the built-in `nn.Classifier`:

```python
from maix import nn, image, tensor
import os
import numpy as np

def parse_str_values(value: str) -> list[float]:
    return [float(v) for v in value.split(",")]

def load_labels(model_path, path_or_labels : str):
    path = ""
    if not ("," in path_or_labels or " " in path_or_labels or "\n" in path_or_labels):
      path = os.path.join(os.path.dirname(model_path), path_or_labels)
    if path and os.path.exists(path):
      with open(path, encoding = "utf-8") as f:
        labels0 = f.readlines()
    else:
      labels0 = path_or_labels.split(",")
    labels = []
    for label in labels0:
        labels.append(label.strip())
    return labels

class My_Classifier:
    def __init__(self, model : str):
      self.model = nn.NN(model, dual_buff = False)
      self.extra_info = self.model.extra_info()
      self.mean = parse_str_values(self.extra_info["mean"])
      self.scale = parse_str_values(self.extra_info["scale"])
      self.labels = self.model.extra_info_labels()
      # self.labels = load_labels(model, self.extra_info["labels"]) # same as self.model.extra_info_labels()

    def classify(self, img : image.Image):
      outs = self.model.forward_image(img, self.mean, self.scale, copy_result = False)
      # 后处理， 以分类模型为例
      for k in outs.keys():
        out = nn.F.softmax(outs[k], replace=True)
        out = tensor.tensor_to_numpy_float32(out, copy = False).flatten()
        max_idx = out.argmax()
        return self.labels[max_idx], out[max_idx]def load_labels(model_path, path_or_labels : str):
    path = ""
    if not ("," in path_or_labels or " " in path_or_labels or "\n" in path_or_labels):
      path = os.path.join(os.path.dirname(model_path), path_or_labels)
    if path and os.path.exists(path):
      with open(path, encoding = "utf-8") as f:
        labels0 = f.readlines()
    else:
      labels0 = path_or_labels.split(",")
    labels = []
    for label in labels0:
        labels.append(label.strip())
    return labels

class My_Classifier:
    def __init__(self, model : str):
      self.model = nn.NN(model, dual_buff = False)
      self.extra_info = self.model.extra_info()
      self.mean = parse_str_values(self.extra_info["mean"])
      self.scale = parse_str_values(self.extra_info["scale"])
      self.labels = self.model.extra_info_labels()
      # self.labels = load_labels(model, self.extra_info["labels"]) # same as self.model.extra_info_labels()

    def classify(self, img : image.Image):
      outs = self.model.forward_image(img, self.mean, self.scale, copy_result = False)
      # 后处理， 以分类模型为例
      for k in outs.keys():
        out = nn.F.softmax(outs[k], replace=True)
        out = tensor.tensor_to_numpy_float32(out, copy = False).flatten()
        max_idx = out.argmax()
        return self.labels[max_idx], out[max_idx]

classifier = My_Classifier("/root/models/mobilenetv2.mud")
file_path = "/root/cat_224.jpg"
img = image.load(file_path, image.Format.FMT_RGB888)
label, score = classifier.classify(img)

print("max score:", label, score)
```

This code:
* Loads the model and retrieves `mean` and `scale` parameters from the `mud` file.
* Recognizes an image by directly calling `forward_image` for model output.
* Applies `softmax` as a postprocessing step and displays the class with the highest probability as an example.

More complex models may have elaborate postprocessing, like YOLO, which requires custom CPU processing for certain model parts.

## Adding AI Models and Algorithms for Other Data Types

For other data types, like audio or motion sensor data:
* Input: Any data, like audio, IMU, or pressure data.
* Output: Any data, like classifications, probabilities, or control values.

For non-image inputs, use `forward` to process raw `float32` data. To prepare data for `forward`, convert it to `tensor.Tensors` from `numpy`:

```python
from maix import nn, tensor, time
import numpy as np

input_tensors = tensor.Tensors()
for layer in model.inputs_info():
    data = np.zeros(layer.shape, dtype=np.float32)
    t = tensor.tensor_from_numpy_float32(data)
    input_tensors.add_tensor(layer.name, t, True, True)
outputs = model.forward(input_tensors, copy_result=False, dual_buff_wait=True)
del input_tensors_li
```

This enables you to send raw data to the model.

Alternatively, to reduce memory copy and speed up execution, use:

```python
from maix import nn, tensor, time
import numpy as np

input_tensors = tensor.Tensors()
input_tensors_li = []
for layer in model.inputs_info():
    data = np.zeros(layer.shape, dtype=np.float32)
    t = tensor.tensor_from_numpy_float32(data, copy=False)
    input_tensors.add_tensor(layer.name, t, False, False)
    input_tensors_li.append(t)
outputs = model.forward(input_tensors, copy_result=False, dual_buff_wait=True)
del input_tensors_li
```

## Adding AI Models and Algorithms in C++

Writing Python code allows rapid model validation, but complex preprocessing or postprocessing can slow down performance. In such cases, consider C++ for efficiency.

Refer to the [YOLO11 source code](https://github.com/sipeed/MaixCDK/blob/main/components/nn/include/maix_nn_yolo11.hpp) for guidance.

Additionally, C++ code can be used in both C++ and MaixPy. By adding comments like `@maixpy maix.nn.YOLO11` to your C++ class, it can be used in MaixPy via `maix.nn.YOLO11`, providing seamless integration.


