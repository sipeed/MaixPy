---
title: 将 ONNX 模型转换为 MaixCAM MaixPy 可以使用的模型（MUD）
---

> MaixCAM2 模型转换请看[MaixCAM2 模型转换文档](./maixcam2.md)

## 简介

电脑上训练的模型不能直接给 MaixCAM 使用，因为 MaixCAM 的硬件性能有限，一般我们需要将模型进行`INT8`量化以减少计算量，并且转换为 MaixCAM 支持的模型格式。

本文介绍如何将 ONNX 模型转换为 MaixCAM 能使用的模型（MUD模型）。


## MaixCAM 支持的模型文件格式

MUD（模型统一描述文件， model universal description file）是 MaixPy 支持的一种模型描述文件，用来统一不同平台的模型文件，方便 MaixPy 代码跨平台，本身是一个 `ini`格式的文本文件，可以使用文本编辑器编辑。
一般 MUD 文件会伴随一个或者多个实际的模型文件，比如对于 MaixCAM， 实际的模型文件是`.cvimodel`格式， MUD 文件则是对它做了一些描述说明。


## 准备 ONNX 模型

准备好你的 onnx 模型， 然后在[https://netron.app/](https://netron.app/) 查看你的模型，确保你的模型使用的算子在转换工具的支持列表中，转换工具的支持列表可以在[算能 TPU SDK](https://developer.sophgo.com/thread/473.html)的 **CVITEK_TPU_SDK开发指南.pdf** 中看到列表。


## 找出合适的量化输出节点
[详细参考这里](./onnx_export.md)
假设你裁剪得到的onnx文件是`export.onnx`。

## 安装模型转换环境

模型转换使用算能的[https://github.com/sophgo/tpu-mlir](https://github.com/sophgo/tpu-mlir)，要安装它我们直接在 docker 环境中安装，防止我们电脑的环境不匹配，如果你没用过 docker，可以简单理解成它类似虚拟机。

### 拉取 docker 镜像

```shell
docker pull sophgo/tpuc_dev:latest
```

如果docker拉取失败，可以通过以下方式进行下载：
```shell
wget https://sophon-file.sophon.cn/sophon-prod-s3/drive/24/06/14/12/sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
docker load -i sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
```
这个方法参考[tpu-mlir官方docker环境配置](https://github.com/sophgo/tpu-mlir/blob/master/README_cn.md)。

此外你也可以设置国内的镜像，可自行搜索或者参考[docker 设置代理，以及国内加速镜像设置](https://neucrack.com/p/286)。


### 运行容器

```shell
docker run --privileged --name tpu-env -v ./:/workspace -it sophgo/tpuc_dev:v3.2
```

首先创建一个容器，名叫`tpu-env`，并且把当前目录挂载到了容器的`/workspace`，这样就实现了文件共享，请把`export.onnx`放在当前目录。

下次启动容器用`docker start tpu-env && docker attach tpu-env`即可。


### 安装 tpu-mlir

```shell
pip install tpu_mlir
```

之后在容器内**直接输入**`model_transform.py`回车执行会有打印帮助信息就算是安装成功了。

## 转换onnx模型到cvimodel

转换模型主要就两个命令，`model_transform.py` 和 `model_deploy.py`，下面请根据教程在终端里面调整参数，以yolov5s为例,其他模型请自行修改文件路径，**注意运行的前后顺序**。

`第一步`
> 注意`--model_def`，`--test_result`，`--mlir`，`--test_input`的路径和后续的文件路径是否一致，其他的参数请参考下面的表格调整。
```bash
model_transform.py \
--model_name yolov5s \
--model_def ./export.onnx \
--input_shapes [[1,3,224,320]] \
--mean "0,0,0" \
--scale "0.00392156862745098,0.00392156862745098,0.00392156862745098" \
--keep_aspect_ratio \
--pixel_format rgb \
--channel_format nchw \
--output_names "/model.24/m.0/Conv_output_0,/model.24/m.1/Conv_output_0,/model.24/m.2/Conv_output_0" \
--test_input ./zidane.jpg \
--test_result yolov5s_top_outputs.npz \
--tolerance 0.99,0.99 \
--mlir yolov5s.mlir
```


| 关键参数 | 含义 | 说明/建议 | 示例 |
|---|---|---|---|
| `output_names` | 输出节点的输出名 | 就是前面提到的模型输出节点名称，需要与实际模型导出后的输出名一致。 | `--output_names "output0"` |
| `mean, scale` | 训练时使用的预处理方法 | 例如 YOLOv5 官方预处理通常是对 RGB 3 个通道做归一化。默认可理解为 `mean=0`、`std=255`，即把图像像素值归一化到较小范围，因此 `scale=1/std`。这里需要根据你自己的模型实际预处理方式进行修改。 | `--mean "0,0,0"`，`--scale "0.00392156862745098,0.00392156862745098,0.00392156862745098"` |
| `test_input` | 转换时用来测试的图像 | 例如这里使用 `../dog.jpg`，所以实际转换模型时，需要在此脚本所在目录附近放置对应测试图片。你的模型应根据实际情况替换为自己的测试图像。 | `--test_input ./zidane.jpg` |
| `tolerance` | 量化前后允许的误差 | 如果转换时报错，提示误差值大于该设置，说明转换后的模型相比 ONNX 模型误差可能较大。如果可以容忍，可适当调整该阈值让转换通过；但大多数情况下，误差大往往是模型结构或后处理导致的，需要优化模型，并尽量移除可去除的后处理。 | `--tolerance 0.99,0.99` |
| `model_def` | 裁剪节点后的onnx文件 | | `--model_def ./export.onnx` |
| `mlir` | 转换后的mlir中间产物文件 | | `--mlir yolov5s.mlir` |
| `test_result` | `test_input`输入图像转换得到的中间文件，用于后续处理 | | `--test_result yolov5s_top_outputs.npz ` |
| `input_shapes` | 待转换模型的输入尺寸 |由于模型输入图像的尺寸是固定的，请根据你MaixCAM输入的图像灵活调整，需要在onnx的导出阶段就确定好你的图像尺寸 | `--input_shapes [[1,3,224,320]]` |



`第二步`

> 注意`--model_def`，`--test_result`，`--mlir`，`--test_input`，的路径和前面的文件路径是否一致，其他的参数请参考下面的表格调整。
> 第一个是bf16的转化过程，第二个是int8的转化过程，int8模型需要多经过一层校准，请注意区分。
`bf16`
```bash
# export bf16 model
#   not use --quant_input, use float32 for easy coding
model_deploy.py \
--mlir yolov5s.mlir \
--quantize BF16 \
--processor cv181x \
--test_input yolov5s_in_f32.npz \
--test_reference yolov5s_top_outputs.npz \
--model yolov5s_bf16.cvimodel
```


`int8`
```bash
#  "calibrate for int8 model"
# export int8 model
run_calibration.py yolov5s.mlir \
--dataset ./images \
--input_num 1 \
-o yolov5s_cali_table

#  "convert to int8 model"
# export int8 model
#    add --quant_input, use int8 for faster processing in maix.nn.NN.forward_image
model_deploy.py \
--mlir yolov5s.mlir \
--quantize INT8 \
--quant_input \
--calibration_table yolov5s_cali_table \
--processor cv181x \
--test_input yolov5s_in_f32.npz \
--test_reference yolov5s_top_outputs.npz \
--tolerance 0.9,0.6 \
--model yolov5s_int8.cvimodel
```

| 关键参数 | 含义 | 说明/建议 | 示例 |
|----------|------|-----------|------|
| `quantize` | 量化的数据类型 | 在 MaixCAM 上一般优先使用 `INT8` 模型。`BF16` 模型精度较高，但运行速度通常较慢。因此，推荐优先尝试转换为 `INT8`；如果无法转换，或对精度要求更高且对速度要求不高，再考虑 `BF16`。 | `--quantize INT8` / `--quantize BF16` |
| `dataset`  | 用于量化的数据集 | 数据集通常放在转换脚本同目录下，例如这里的 `images` 文件夹。对于 YOLOv5，一般放图片即可，可以从 COCO 数据集中挑选一部分典型场景图片。`--input_num` 可指定实际使用的图片数量，且应小于等于 `images` 目录中的实际图片数。 | `--dataset ./images` |
| `mlir`  | 转换前的mlir文件 | 需要和`model_transform.py`转换得到的mlir文件一致 | `--mlir yolov5s.mlir` |
| `test_input`  | 测试用的npz文件 | 需要和`model_transform.py`中使用的参数`test_result`得到的npz文件一致 | `--test_input yolov5s_in_f32.npz ` |
| `model`  | 最终得到的cvimodel | 将得到的cvimodel放入MaixCAM中并在该目录下配置mud文件即可经过MaixPy调用 | `--model yolov5s_int8.cvimodel` |



## 编写`mud`文件


> 注：mud和cvimodel必须在同一文件目录。

这里以 `YOLOv8` 模型文件举例，一共两个文件`yolov8n.mud`和`yolov8n.cvimodel`，前者内容：

```ini
[basic]
type = cvimodel
model = yolov8n.cvimodel

[extra]
model_type = yolov8
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```

| 项目 | 说明 |
|------|------|
| 模型类别 |  `cvimodel`，MaixCAM2是`axmodel`。 |
| 模型路径 | 相对 `mud` 文件路径下的 `yolov8n.cvimodel` 文件。 |
| `mean` / `scale` | 预处理参数，需要与训练时模型输入数据的预处理方法保持一致。 |
| `labels` | 检测对象的类别列表，这里对应 80 种分类。 |
| 文件放置方式 | 实际使用时，将模型文件和 `mud` 文件放在同一目录下即可。 |
| 自定义模型修改项 | 根据你的模型情况，在 `mud` 文件中修改你训练得到的 `labels` 即可。 |

实际用这个模型的时候将两个文件放在同一个目录下即可。

根据你的模型情况，在`mud`文件修改你训练的`labels`就好了。

这里`basic`部分指定了模型文件类别和模型文件路径，是必要的参数，有了这个参数就能用`MaixPy`或者`MaixCDK`中的`maix.nn.NN`类来加载并运行模型了。


`extra`则根据不同模型的需求设计不同参数。
比如这里对`YOLOv5`设计了这些参数，主要是 预处理、后处理、标签等参数。
对于 `MaixPy` 已经支持了的模型可以直接下载其模型复制修改。
也可以看具体的代码，比如[YOLOv5 的源码](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp#L73-L223)，可以看到源码使用了哪些参数。

比如你用`YOLOv5`训练了检测数字`0~9`的模型，那么需要将`labels`改成`0,1,2,3,4,5,6,7,8,9`，其它参数如果你没改训练代码保持即可。

如果你需要移植 `MaixPy` 没有支持的模型，则可以根据模型的预处理和后处理情况定义 `extra`, 然后编写对应的解码类。如果你不想用C++修改 MaixPy 源码，你也可以用MaixPy 的`maix.nn.NN`类加载模型，然后用 `forward` 或者 `forward_image` 方法或者原始输出，在 Python 层面写后处理也可以，只是运行效率比较低不太推荐。


## 编写后处理代码

如上一步所说，如果是按照已经支持的模型的`mud`文件修改好，那直接调用`MaixPy`或者`MaixCDK`对应的代码加载即可。
如果支持新模型，设计好 `mud` 文件后，你需要实际编写预处理和后处理，有两种方法：
* 一：MaixPy 用 `maix.nn.NN`加载模型，然后`forward`或者`forward_image`函数运行模型，获得输出，然后用 Python 函数编写后处理得到最终结果。
* 二：在`MaixCDK`中，可以参考[YOLOv5 的源码](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp), 新增一个`hpp`文件，增加一个处理你的模型的类，并且修改所有函数和类的`@maixpy`注释，编写好了编译`MaixPy`项目，即可在`MaixPy`中调用新增的类来运行模型了。

支持了新模型后还可以将源码提交（Pull Request）到主`MaixPy`仓库中，成为`MaixPy`项目的一员，为社区做贡献，也可以到 [MaixHub 分享](https://maixhub.com/share) 分享你新支持的模型，根据质量可以获得最少 `30元` 最高 `2000元` 的打赏！




