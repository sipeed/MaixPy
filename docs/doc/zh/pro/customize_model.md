---
title: 为 MaixCAM MaixPy 添加新的 AI 模型
update:
    - date: 2024-11-01
      author: neucrack
      version: 1.0.0
      content: 新增移植文档
---


## 简介

除了 MaixPy 自带的 AI 算法和模型外， MaixPy 有很大的扩展能力，你可以自己添加新的算法和模型。

因为视觉应用比较多，以下将分为视觉应用和其它应用进行讲解。


## 如果 MaixPy 已经支持的框架，只是数据集不同

比如 MaixPy 已经支持了 YOLO11 检测，但是你的数据集不同，这种情况下，你只需要准备好数据集，然后训练模型，导出模型即可。

还有一个偷懒的最快的方式，就是先去网上找找有没有人已经训练好了模型或者开源了模型，下载转一下格式就能用了，或者基于其继续训练。
举个例子:
比如要识别火焰，在网上一搜，找到[Abonia1/YOLOv8-Fire-and-Smoke-Detection](https://github.com/Abonia1/YOLOv8-Fire-and-Smoke-Detection) 这个项目分享了基于 YOLOv8 的火焰和烟雾检测模型，下载下来，导出成 ONNX 格式再转换为 MaixPy 支持的格式即可。

可以上传到[MaixHub 模型库](https://maixhub.com/model/zoo)分享给更多人使用，也可以找其他人分享的模型。

## 在 Python 层面添加视觉 AI 模型和算法

对于视觉，一般来说是对图像进行时别，即：
* 输入：图像
* 输出：任何数据，比如分类、概率、图像、坐标等

在`MaixPy`中我们以常用的算法比如`YOLO11`检测为例：

```python
from maix import nn, image

detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff = True)

img = image.Image(detector.input_width(), detector.input_height(), detector.input_format())
objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
```

可以看到先构建`YOLO11`对象读取模型，然后将图片传给`detect`方法时别，每一步内部分别做了：
* nn.YOLO11()： 构造对象，读取加载模型到内存，解析模型。
* detector.detect(): 
  * 预处理图像，一般是标准化图像即 `(值 - mean) * scale` 将像素值调整到一个合适的范围比如[0,1]，这个由训练模型时决定，运行时要和训练时用的方法一致。
  * 运行模型，将预处理好的数据发给 NPU，让 NPU 按照模型的网络进行计算，得到 AI 模型网络的最后 N 层输出，一般是 浮点 型数据。
  * 后处理，一般模型的输出不是最后的结果，还要对模型的输出进行一定的处理才能得到结果。

所以，我们要添加一个新的模型和算法，也就是要自己实现一个类似 `YOLO11` 这样的类，伪代码：
```python
class My_Model:
    def __init__(self, model : str):
      pass
      # 解析模型，可以自定义一个 MUD 文件从里面解析，比如解析出 mean scale 的值

    def recognize(self, img : image.Image):
      pass
      # 预处理图像
      # 运行模型
      # 后处理
      # 返回结果
```

我们借助 `nn.NN` 类可以实现模型解析和运行，具体方法可以看 [API](http://127.0.0.1:2333/maixpy/api/maix/nn.html#NN) 文档。

通过`nn.NN`我们可以解析我们写的`mud`模型描述文件，比如得到预处理的`mean`和`scale`的值，然后用`nn.NN.forward_image()`方法运行模型，这个方法集成了预处理和运行模型两个步骤可以减少内存拷贝会更快，如果你的预处理更复杂，可以自己写预处理然后调用`forward`方法运行模型得到模型的输出结果。

比如我们以分类模型为例，不使用内置的`nn.Classifier` 类，而是自己实现一个试试：

```python
from maix import nn, image, tensor
import os
import numpy as np

def parse_str_values(value : str) -> list[float]:
    if "," in value:
      final = []
      values = value.split(",")
      for v in values:
        final.append(float(v))
      return final
    else:
      return [float(value)]

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
        return self.labels[max_idx], out[max_idx]

classifier = My_Classifier("/root/models/mobilenetv2.mud")
file_path = "/root/cat_224.jpg"
img = image.load(file_path, image.Format.FMT_RGB888)
if img is None:
    raise Exception(f"load image {file_path} failed")
label, score = classifier.classify(img)

print("max score:", label, score)
```

可以看到这里我们：
* 加载模型，从模型的`mud`文件中获取到`mean` `scale`参数并解析成`float`类型
* 识别图片，直接调用`forward_image` 函数得到模型输出。
* 这里我们的模型最后的输出是没有经过`softmax`计算的（取决于模型本身以及导出模型时选择的节点），所以我们需要进行 softmax 后处理。
* 然后我们只取了一个最大概率的类别进行了显示作为例子。


注意到这里的后处理比较简单，只是一个 softmax 计算，对于更复杂的模型，可能有更复杂的后处理，比如 YOLO 的后处理就相对复杂，我们把 YOLO 模型后面的 CPU 计算的不适合量化的部分节点从模型中去掉并手动编写后处理完成。


## 添加其它类型数据的 AI 模型和算法

对于其它类型的数据，比如音频数据，运动传感器数据等：
* 输入：任何数据，比如音频数据，IMU 数据，压力数据等。
* 输出：任何数据，比如分类、概率、控制值等。

可以看到这里和视觉模型不同的就是输入数据类型，对于图片输入，我们用`forward_image`函数能高效地预处理图像并运行模型，对于非图像，我们可以用`forward`函数来运行裸`float32`数据。

按照`forward`函数的要求准备参数即可，这里比较麻烦就是准备`tensor.Tensors`类型的输入数据，可以通过 `numpy`数据转过来：
```python
from maix import nn, tensor, time
import numpy as np

input_tensors = tensor.Tensors()
for layer in model.inputs_info():
    print(layer)
    data = np.zeros(layer.shape, dtype=np.float32)
    t = tensor.tensor_from_numpy_float32(data)
    input_tensors.add_tensor(layer.name, t, True, True)
outputs = model.forward(input_tensors, copy_result = False, dual_buff_wait=True)
del input_tensors_li
```
这样就实现了传裸数据给模型了。

另外这个代码还可以减少拷贝来加速运行，只不过写不好程序容易出错，可以参考：
```python
from maix import nn, tensor, time
import numpy as np

input_tensors = tensor.Tensors()
input_tensors_li = []
for layer in model.inputs_info():
    print(layer)
    data = np.zeros(layer.shape, dtype=np.float32)
    t = tensor.tensor_from_numpy_float32(data, copy = False)
    input_tensors.add_tensor(layer.name, t, False, False)
    # we use `copy = False` for add_tensor, so input_tensors' data is borrowed from t,
    # so we add to global var to prevent t to be collected until we don't use input_tensors anymore.
    input_tensors_li.append(t)
outputs = model.forward(input_tensors, copy_result = False, dual_buff_wait=True)
del input_tensors_li
```



## C++ 层面添加 AI 模型和算法

在 Python 层面写程序会比较快速地就能验证模型，不过如果后处理或预处理太复杂会导致程序运行比较慢，这种情况下可以考虑使用 C++ 进行封装。

可以参考 [YOLO11](https://github.com/sipeed/MaixCDK/blob/main/components/nn/include/maix_nn_yolo11.hpp) 的源码写即可。

另外， 用 C++ 写的好处是不光可以给 C++ 使用，也可以给 MaixPy 使用，只需要给类添加`@maixpy maix.nn.YOLO11` 这样的注释，编译后就能用在`MaixPy`通过`maix.nn.YOLO11`调用了，是不是非常方便。




