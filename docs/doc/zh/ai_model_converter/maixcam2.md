---
title: 将 ONNX 模型转换为 MaixCAM2 MaixPy 可以使用的模型（MUD）
---

> MaixCAM / MaixCAM-Pro 模型转换请看[MaixCAM 模型转换文档](./maixcam.md)

## 简介

电脑上训练的模型不能直接给 MaixCAM2 使用，因为 MaixCAM2 的硬件性能有限，一般我们需要将模型进行`INT8`量化以减少计算量，并且转换为 MaixCAM2 支持的模型格式。

本文介绍如何将 ONNX 模型转换为 MaixCAM2 能使用的模型（MUD模型）。


## MaixCAM2 支持的模型文件格式

MUD（模型统一描述文件， model universal description file）是 MaixPy 支持的一种模型描述文件，用来统一不同平台的模型文件，方便 MaixPy 代码跨平台，本身是一个 `ini`格式的文本文件，可以使用文本编辑器编辑。
一般 MUD 文件会伴随一个或者多个实际的模型文件，比如对于 MaixCAM2， 实际的模型文件是`.axmodel`格式， MUD 文件则是对它做了一些描述说明。
下面请按照教程讲onnx文件逐步转换成MaixCAM2能运行的MUD模型文件。



## 准备 ONNX 模型

准备好你的 onnx 模型， 然后在[https://netron.app/](https://netron.app/) 查看你的模型，确保你的模型使用的算子在转换工具的支持列表中，转换工具的支持列表可以在[Pulsar2 工具链文档](https://pulsar2-docs.readthedocs.io/)找到。
对于 `MaixCAM2`，对应了 Pulsar2 文档中 `AX620E` 平台。


## 找出合适的量化输出节点
[详细参考这里](./onnx_export.md)
假设你裁剪得到的onnx文件是`export.onnx`。

## 安装模型转换环境

参考 [Pulsar2 工具链文档](https://pulsar2-docs.readthedocs.io/) 进行安装，要安装它我们直接在 docker 环境中安装，防止我们电脑的环境不匹配。


### 拉取 docker 镜像

可以按照 [Pulsar2 工具链文档](https://pulsar2-docs.readthedocs.io/) 中的方法下载和加载，如果文档中不是最新的，也可以到[huggingface](https://huggingface.co/AXERA-TECH/Pulsar2/tree/main) / [modelscope](https://www.modelscope.cn/models/AXERA-TECH/Pulsar2/files) 下载。

即下载镜像文件后，使用命令加载：
```shell
docker load -i pulsar2_vxx.tar.gz
```

工具链会定期更新，下载新的加载即可。

### 运行容器
> 根据你的版本，docker镜像名不一定是`pulsar2:6.0`，具体请使用`docker images`查看具体的`pulsar2:xx`镜像名。
```shell
docker run -it --net host --rm -v ./:/data pulsar2:6.0
```

### 转换命令和配置文件解析

可以详细读一读 pulsar2 工具的文档。
主要核心就是一个命令：
```shell
pulsar2 build --target_hardware AX620E --input onnx_path --output_dir out_dir --config config_path
```

`config.json` 文件是一个 `json`配置文件，配置了预处理和输出节点，以及量化策略，具体可以看 pulsar2 文档，比如 yolo11:
```json
{
  "model_type": "ONNX",
  "npu_mode": "NPU2",
  "quant": {
    "input_configs": [
      {
        "tensor_name": "images",
        "calibration_dataset": "datasets/train.tar",
        "calibration_size": 64,
        "calibration_mean": [0, 0, 0],
        "calibration_std": [255, 255, 255]
      }
    ],
    "calibration_method": "MinMax",
    "precision_analysis": true
  },
  "input_processors": [
    {
      "tensor_name": "images",
      "tensor_format": "RGB",
      "tensor_layout": "NCHW",
      "src_format": "RGB",
      "src_dtype": "U8",
      "src_layout": "NHWC",
      "csc_mode": "NoCSC"
    }
  ],
  "output_processors": [
    {
      "tensor_name": "/model.23/Concat_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_1_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_2_output_0",
      "dst_perm": [0, 2, 3, 1]
    }
  ],
  "compiler": {
    "check": 3,
    "check_mode": "CheckOutput",
    "check_cosine_simularity": 0.9
  }
}
```

| 参数 | 说明 |
|------|------|
| `calibration_dataset` | 量化校准数据，tar文件里面存放训练集的图片即可。 |
| `output_processors` | 输出节点，根据你裁剪的onnx的终点节点。 dst_perm,必须和你的输出的维度对上，不然无法使用|
| `npu_mode` | 需要特别注意的参数。 |
| `NPU2` | 表示使用全部 NPU 算力。 |
| `NPU1` | 表示开启虚拟 NPU 功能，将 NPU 分成两个虚拟 NPU：一个用于 AI-ISP，另一个用于模型，因此模型只使用一半 NPU 算力。 |
| AI-ISP 使用建议 | 如果需要使用 AI-ISP 功能，应将 `npu_mode` 设置为 `NPU1`。 |
| MaixCAM2 模型转换建议 | 为方便用户自由选择是否启用 AI-ISP，建议在转换模型时同时生成两种模型。 |
| mud 文件对应模型 | 分别对应 `model_npu` 和 `model_vnpu` 两个模型。 |

### pulsar2导出`model_npu`和`model_vnpu`教程
`第一步,配置npu和vnpu分别所需要的config.json`
> 注意`output_processors`的节点配置是否和裁剪后的onnx的输出节点是**完全一致**的
`./config/yolo11n.npu.json`
```json
{
  "model_type": "ONNX",
  "npu_mode": "NPU1",
  "quant": {
    "input_configs": [
      {
        "tensor_name": "images",
        "calibration_dataset": "datasets/train.tar",
        "calibration_size": 4,
        "calibration_mean": [0, 0, 0],
        "calibration_std": [255, 255, 255]
      }
    ],
    "calibration_method": "MinMax",
    "precision_analysis": true
  },
  "input_processors": [
    {
      "tensor_name": "images",
      "tensor_format": "RGB",
      "tensor_layout": "NCHW",
      "src_format": "RGB",
      "src_dtype": "U8",
      "src_layout": "NHWC",
      "csc_mode": "NoCSC"
    }
  ],
  "output_processors": [
    {
      "tensor_name": "/model.23/Concat_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_1_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_2_output_0",
      "dst_perm": [0, 2, 3, 1]
    }
  ],
  "compiler": {
    "check": 3,
    "check_mode": "CheckOutput",
    "check_cosine_simularity": 0.9
  }
}

```

> 存放以上json字符串到`./config/yolo11n.npu.json`，你也可以存放到其他目录，但是需要注意后续命令的路径需要保证是完全一致的。
`./config/yolo11n.vnpu.json`
```json
{
  "model_type": "ONNX",
  "npu_mode": "NPU2",
  "quant": {
    "input_configs": [
      {
        "tensor_name": "images",
        "calibration_dataset": "datasets/train.tar",
        "calibration_size": 4,
        "calibration_mean": [0, 0, 0],
        "calibration_std": [255, 255, 255]
      }
    ],
    "calibration_method": "MinMax",
    "precision_analysis": true
  },
  "input_processors": [
    {
      "tensor_name": "images",
      "tensor_format": "RGB",
      "tensor_layout": "NCHW",
      "src_format": "RGB",
      "src_dtype": "U8",
      "src_layout": "NHWC",
      "csc_mode": "NoCSC"
    }
  ],
  "output_processors": [
    {
      "tensor_name": "/model.23/Concat_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_1_output_0",
      "dst_perm": [0, 2, 3, 1]
    },
    {
      "tensor_name": "/model.23/Concat_2_output_0",
      "dst_perm": [0, 2, 3, 1]
    }
  ],
  "compiler": {
    "check": 3,
    "check_mode": "CheckOutput",
    "check_cosine_simularity": 0.9
  }
}
```
> 存放以上json字符串到`./config/yolo11n.vnpu.json`。


`第二步,运行转换指令`
> 注意`--input`，`--config`的路径和前面存放的文件路径是否一致，注意输出的中间产出文件夹`./tmp`的路径，以免被覆盖或删除。
```bash
pulsar2 build --target_hardware AX620E --input ./export.onnx  --output_dir ./tmp --config ./config/yolo11n.npu.json
cp tmp/compiled.axmodel out/yolo11n_npu.axmodel

pulsar2 build --target_hardware AX620E --input ./export.onnx  --output_dir ./tmp --config ./config/yolo11n.vnpu.json
cp tmp/compiled.axmodel out/yolo11n_vnpu.axmodel
```

执行成功后就会在文件夹`out/`得到  `*_npu.axmodel`和`*_vnpu.axmodel`两个模型。

## 编写`mud`文件

这里以 `YOLO11` 模型文件举例，一共三个文件`yolo11n.mud`， `yolo11n_npu.axmodel`和`yolo11n_vnpu.axmodel`，前者内容：

```ini
[basic]
type = axmodel
model_npu  = yolo11n_npu.axmodel
model_vnpu = yolo11n_vnpu.axmodel

[extra]
model_type = yolo11
type=detector
input_type = rgb
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

input_cache = true
output_cache = true
input_cache_flush = false
output_cache_inval = true

mean = 0,0,0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
```

可以看到， 指定了模型类别为`axmodel`, 模型路径为相对`mud`文件的路径下的`*.axmodel`文件；

以及一些需要用到的信息:

| 参数 | 说明 |
|---|---|
| `labels` | 检测对象的 80 种分类。 |
| `input_cache` / `output_cache` | 代表输入输出是否使用缓存内存。使用缓存能在需要多次读取数据的情况下加快读取速度，比如后处理需要连续多次读取模型输出结果时，建议使用缓存。 |
| `input_cache_flush` | 表示运行模型前是否将内存 cache 刷新到 DDR 中。一般如果模型第一层是 NPU 算子，则必须设置为 `true`。对于 YOLO11，因为模型集成了预处理，也就是说第一层是 CPU 处理，所以设置为 `false`。如果不确定，则设置为 `true`。 |
| `output_cache_inval` | 表示模型运行完成后是否将输出内存缓冲区设置为无效，以保证读取模型输出数据时是直接从 DDR 读取。一般如果模型最后一层是 NPU 算子输出，则必须设置为 `true`；如果是 CPU 算子，则可以设置为 `false` 以减少耗时。如果不确定，可以设置为 `true` 以保证数据正确。 |
| `mean` / `scale` | 实际上在转模型时，预处理已经集成在模型中，这里写出来只是为了方便查看，需要与训练时对模型输入数据的预处理方法保持一致。 |

实际用这个模型的时候将三个文件放在同一个目录下即可。

根据你的模型情况修改，比如对于 YOLO11，修改成你训练的`axmodel`名字和`labels`就好了。

这里`basic`部分指定了模型文件类别和模型文件路径，是必要的参数，有了这个参数就能用`MaixPy`或者`MaixCDK`中的`maix.nn.NN`类来加载并运行模型了。

如果你需要移植 `MaixPy` 没有支持的模型，则可以根据模型的预处理和后处理情况定义 `extra`, 然后编写对应的解码类。如果你不想用C++修改 MaixPy 源码，你也可以用MaixPy 的`maix.nn.NN`类加载模型，然后用 `forward` 或者 `forward_image` 方法或者原始输出，在 Python 层面写后处理也可以，只是运行效率比较低不太推荐。


## 编写后处理代码

如上一步所说，如果是按照已经支持的模型的`mud`文件修改好，那直接调用`MaixPy`或者`MaixCDK`对应的代码加载即可。
如果是仍未支持的新模型，设计好 `mud` 文件后，你需要实际编写预处理和后处理，有两种方法：
* 一：**适合快速验证**。MaixPy 用 `maix.nn.NN`加载模型，然后`forward`或者`forward_image`函数运行模型，获得输出，然后用 Python 函数编写后处理得到最终结果。可以参考[移植新模型](../pro/customize_model.md)
* 二：**适合正式封装，让`MaixCDK`和`MaixPy`都可以调用而且运行效率更高**。在`MaixCDK`中，可以参考[YOLOv5 的源码](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp), 新增一个`hpp`文件，增加一个处理你的模型的类，并且修改所有函数和类的`@maixpy`注释，编写好了编译`MaixPy`项目，即可在`MaixPy`中调用新增的类来运行模型了。

支持了新模型后还可以将源码提交（Pull Request）到主`MaixPy`仓库中，成为`MaixPy`项目的一员，为社区做贡献，也可以到 [MaixHub 分享](https://maixhub.com/share) 分享你新支持的模型，根据质量可以获得最少 `30元` 最高 `2000元` 的打赏！




