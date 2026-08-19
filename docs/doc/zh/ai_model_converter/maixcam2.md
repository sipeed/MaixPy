---
title: 将 ONNX 模型转换为 MaixCAM2 MaixPy 可以使用的模型（MUD）
---

> MaixCAM / MaixCAM-Pro 模型转换请看[MaixCAM 模型转换文档](./maixcam.md)

## 简介

电脑上训练的模型不能直接给 MaixCAM2 使用，一般需要将模型量化为 INT8，并转换为 MaixCAM2 支持的 `.axmodel` 格式。INT8 通常可以降低模型存储、内存带宽和运行开销，但最终速度与模型结构、输入尺寸和输出数据量也有关。

本文面向会使用 Python、Docker，并能通过 Netron 查看 ONNX 输入输出的读者；完整示例仅针对 **标准 Ultralytics YOLO11 Detect**。

注意：如果转换过程中遇到问题，需要在 QQ 群、论坛或 GitHub 提问，请不要只描述“为什么转换失败”并附一张报错截图。建议同时提供模型类型、输入尺寸、类别数量、ONNX 输入输出节点及 shape、完整转换命令或配置文件、转换工具和 MaixPy 版本，以及从开始转换到报错位置的完整日志，方便他人准确定位问题。

## MaixCAM2 支持的模型文件格式

MUD（模型统一描述文件， model universal description file）是 MaixPy 支持的一种模型描述文件，用来统一不同平台的模型文件，方便 MaixPy 代码跨平台，本身是一个 `ini`格式的文本文件，可以使用文本编辑器编辑。
一般 MUD 文件会伴随一个或者多个实际的模型文件，比如对于 MaixCAM2， 实际的模型文件是`.axmodel`格式， MUD 文件则是对它做了一些描述说明。本文最终会得到：

```text
yolo11n.mud
yolo11n_npu.axmodel
yolo11n_vnpu.axmodel
```

下面请按照步骤，将 ONNX 文件逐步转换成 MaixCAM2 能运行的 MUD 模型文件。

## 准备 ONNX 模型

本节的目标是先得到一个可以被 Pulsar2 读取的 `.onnx` 文件。ONNX 一般来自下面几种情况：

1. **自己训练后导出**：例如 YOLO11 / YOLOv8 训练得到 `.pt` 文件后，按 [离线训练 YOLO 模型](../vision/customize_model_yolov8.md) 中的“导出 ONNX 模型”步骤导出。MaixCAM2 建议先使用固定输入尺寸，例如 `640x480` 或 `320x240`，不要使用动态输入尺寸。
2. **其它训练框架导出**：例如 PyTorch、TensorFlow 等框架训练后导出 ONNX。导出后需要确认模型输入尺寸固定，并且输入、输出节点可以在 Netron 中正常查看。
3. **第三方提供的 ONNX**：可以直接从 ONNX 开始转换，但需要确认模型授权可用，并且模型结构适合在 MaixCAM2 上运行。

若已获取 `.mud` 和 `.axmodel` 文件，表示该模型已完成面向 MaixCAM2 的转换，可直接部署使用，无需执行本文转换流程。

获取 ONNX 文件后，建议将其放置在独立工作目录，并统一命名为 `model.onnx`。随后使用 [Netron](https://netron.app/) 打开模型，核对并记录以下信息：

| 信息项 | 获取方式 | 后续用途 |
| --- | --- | --- |
| 输入节点名称 | 在 Netron 的输入节点区域查看，常见名称为 `images` | 用于 ONNX 裁剪命令的输入参数、`config.json` 中的 `tensor_name` |
| 输入尺寸 | 在 Netron 的输入节点形状中查看，例如 `1x3x480x640` | 用于确认导出尺寸与 MaixPy 运行时输入尺寸一致 |
| 候选输出节点 | 查看模型末端用于后处理前的输出节点 | 用于 ONNX 裁剪命令的输出参数、`config.json` 中的 `output_processors` |

同时需要确认模型算子位于 Pulsar2 支持范围内。MaixCAM2 对应 Pulsar2 文档中的 `AX620E` 平台；若转换过程中提示某个算子不受支持，应回到训练 / 导出阶段调整模型结构，或选用 MaixPy 已支持的模型结构。


## 找出合适的量化输出节点

本节的目标是得到裁剪后的 `export.onnx`，后面的转换命令会直接使用它。

很多检测模型在 ONNX 末尾带有后处理节点，这些节点通常更适合由 CPU 处理。直接把完整 ONNX 拿去量化，可能会导致量化误差变大或转换失败。因此需要先选择合适的输出节点，再裁剪 ONNX。

可按下表选择常见模型的输出节点。节点选择依据可参考 [离线训练 YOLO 模型 - 输出节点选择](../vision/customize_model_yolov8.md)；分类模型的裁剪原则可参考 [裁剪 ONNX 模型节点教程](./onnx_export.md)。

| 模型类型 | 推荐输出节点选择 | 下一步 |
| --- | --- | --- |
| YOLO11 / YOLOv8 检测模型 | MaixCAM2 推荐使用 `/model.xx/Concat...` 这组输出节点，即把解码和 NMS 留给 MaixPy 后处理 | 参考下方常用节点表 |
| YOLO11 / YOLOv8 pose / seg / obb | 输出节点数量更多，按 [离线训练 YOLO 模型](../vision/customize_model_yolov8.md) 的“输出节点选择”表选择 MaixCAM2 方案 | 复制对应节点名后再裁剪 |
| 分类模型 | 一般取最后一层分类输出；如果末尾有 `softmax`，建议取 `softmax` 前一层输出 | 记录该输出节点名 |

常见 YOLO 检测模型在 MaixCAM2 上可以先使用下面节点：

| 模型 | MaixCAM2 推荐输出节点 |
| --- | --- |
| YOLOv8 检测 | `/model.22/Concat_1_output_0`<br>`/model.22/Concat_2_output_0`<br>`/model.22/Concat_3_output_0` |
| YOLO11 检测 | `/model.23/Concat_output_0`<br>`/model.23/Concat_1_output_0`<br>`/model.23/Concat_2_output_0` |

如果你的节点名称和表格不完全一致，请用 Netron 找到位置相同、含义相同的输出节点，而不是机械复制。

对于标准 YOLO11 / YOLOv8 Detect，MaixPy 的三输出模式要求每层通道数为：

```text
64 + C
```

其中 64 是默认 DFL 回归通道数，`C` 是类别数。输入为 `H×W` 时，应选择三个四维 NCHW 输出：

```text
[1, 64+C, H/8,  W/8]
[1, 64+C, H/16, W/16]
[1, 64+C, H/32, W/32]
```

例如本文使用 `640×480`、80 类模型，三个输出必须为：

```text
[1, 144, 60, 80]
[1, 144, 30, 40]
[1, 144, 15, 20]
```

常见导出版本中的节点名可能包含 `/model.23/Concat...`，但 Ultralytics 版本或导出方式变化后，相同名称可能代表完全不同的张量。因此不能机械复制节点名，必须同时满足上面的输出数量、rank 和 shape。

例如下面这组聚合后的三维输出：

```text
[1, 64, N]
[1, C, N]
[1, 4, N]
```

很明显，不是本文需要的三层特征图，给这类三维输出使用四维 `dst_perm = [0,2,3,1]` 会造成维度错误；即使改成三维 permutation 让编译继续，MaixPy YOLO11 的三输出模式仍会因 shape 不符而失败。

确定输入节点名和输出节点名后，先安装裁剪和简化 ONNX 需要的工具：

```bash
pip install onnx onnxsim
```

然后执行下面命令裁剪 ONNX：

```bash
python -c "import onnx,sys; onnx.utils.extract_model(sys.argv[1], sys.argv[2], [s.strip() for s in sys.argv[3].split(',')], [s.strip() for s in sys.argv[4].split(',')])" model.onnx tmp_extract.onnx "images" "/model.23/Concat_output_0,/model.23/Concat_1_output_0,/model.23/Concat_2_output_0"
onnxsim tmp_extract.onnx export.onnx
```

请把命令中的：

* `model.onnx` 替换为你的原始 ONNX 文件名。
* `"images"` 替换为 Netron 中看到的输入节点名。
* `"/model.23/Concat_output_0,...` 替换为你选择的输出节点名，多个节点用英文逗号分隔。

命令执行成功后，当前目录会得到 `export.onnx`。后文所有 `--input ./export.onnx` 都指这个裁剪并简化后的文件。更完整的裁剪说明可看 [裁剪 ONNX 模型节点教程](./onnx_export.md)。

## 安装模型转换环境

本节的目标是让电脑能够运行 `pulsar2 build` 命令。Pulsar2 建议放在 Docker 容器里运行，这样可以减少本机 Python、系统库版本不一致带来的问题。

如果电脑还没有安装 Docker，请先按 [Docker 官方文档](https://docs.docker.com/engine/install/ubuntu/) 安装。安装完成后执行下面命令，能看到版本号就表示 Docker 可用：

```shell
docker --version
```

然后下载 Pulsar2 Docker 镜像。下载入口可参考 [Pulsar2 工具链文档](https://pulsar2-docs.readthedocs.io/)，也可以到 [Hugging Face](https://huggingface.co/AXERA-TECH/Pulsar2/tree/main) 或 [ModelScope](https://www.modelscope.cn/models/AXERA-TECH/Pulsar2/files) 下载镜像文件。下载到 `pulsar2_vxx.tar.gz` 这类文件后，先加载镜像：

```shell
docker load -i pulsar2_vxx.tar.gz
```

加载完成后查看镜像名，后面的 `docker run` 需要使用这个名字：

```shell
docker images | grep pulsar2
```

例如看到的镜像名是 `pulsar2:6.0`，就进入你的模型转换工作目录并运行容器：

```shell
mkdir -p ~/maixcam2_convert
cd ~/maixcam2_convert
docker run -it --net host --rm -v "$PWD":/data -w /data pulsar2:6.0
```

如果你的镜像名不是 `pulsar2:6.0`，请把命令最后的 `pulsar2:6.0` 换成 `docker images` 看到的实际名称。进入容器后，当前目录就是 `/data`，后面的 `export.onnx`、`datasets/train.tar`、`config/*.json` 都放在这个目录里。

## 转换模型

运行转换前，工作目录中至少应准备好这些文件：

```text
.
├── export.onnx
├── datasets/
│   └── train.tar
└── config/
    ├── yolo11n.npu.json
    └── yolo11n.vnpu.json
```

这些文件分别来自下面步骤：

| 文件 | 如何得到 | 作用 |
| --- | --- | --- |
| `export.onnx` | 上一步裁剪并简化 ONNX 后得到 | 作为 Pulsar2 的输入模型 |
| `datasets/train.tar` | 用真实场景图片打包生成 | 给 INT8 量化做校准 |
| `config/yolo11n.npu.json` | 按下方示例新建 | 生成完整 NPU 算力模型 |
| `config/yolo11n.vnpu.json` | 复制 npu 配置后只修改 `npu_mode` | 生成给 AI-ISP 预留算力的虚拟 NPU 模型 |

校准图片包可以这样准备：新建 `datasets/train_images` 文件夹，放入 20 到 100 张真实场景图片，然后打包成 `datasets/train.tar`：

```shell
mkdir -p datasets/train_images
# 先把校准图片放到 datasets/train_images 目录，再执行下面命令
tar -cf datasets/train.tar -C datasets/train_images .
```

图片越接近实际使用场景，量化后的模型效果越稳定。例如要识别桌面物体，就放桌面环境下拍摄的图片；要识别产线物料，就放产线相机拍到的图片。

Pulsar2 的核心转换命令是：

```shell
pulsar2 build --target_hardware AX620E --input onnx_path --output_dir out_dir --config config_path
```

其中：

| 参数 | 填写内容 |
| --- | --- |
| `--target_hardware AX620E` | MaixCAM2 对应的平台，固定写 `AX620E` |
| `--input onnx_path` | 填写裁剪后的 ONNX，例如 `./export.onnx` |
| `--output_dir out_dir` | 填写临时输出目录，例如 `./tmp` |
| `--config config_path` | 填写配置文件路径，例如 `./config/yolo11n.npu.json` |

以 YOLO11 检测模型为例，先创建 `config/yolo11n.npu.json`：

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

这个配置里最容易出错的是下面几项：

| 参数 | 说明 |
|------|------|
| `tensor_name` | 必须和 Netron 中看到的输入节点名一致，常见是 `images`。 |
| `calibration_dataset` | 指向上面准备的 `datasets/train.tar`。 |
| `calibration_size` | 使用多少张校准图片参与量化，不能大于 `train.tar` 里的图片数量。 |
| `output_processors` | 输出节点必须和裁剪后的 `export.onnx` 输出节点完全一致。`dst_perm` 也要和输出维度对应，否则后处理无法正确解析输出。 |
| `npu_mode` | `NPU2` 表示完整 NPU 算力；`NPU1` 表示给 AI-ISP 预留算力的虚拟 NPU。 |

为了让用户运行时可以自由选择是否启用 AI-ISP，建议同时生成两种模型：

| 生成文件 | 配置文件 | `npu_mode` | 写入 `.mud` 的字段 |
| --- | --- | --- | --- |
| `yolo11n_npu.axmodel` | `config/yolo11n.npu.json` | `NPU2` | `model_npu` |
| `yolo11n_vnpu.axmodel` | `config/yolo11n.vnpu.json` | `NPU1` | `model_vnpu` |

创建 `config/yolo11n.vnpu.json` 时，可以先复制 `config/yolo11n.npu.json`，然后只把 `"npu_mode": "NPU2"` 改成 `"npu_mode": "NPU1"`：

```shell
cp config/yolo11n.npu.json config/yolo11n.vnpu.json
```

确认 `export.onnx`、`datasets/train.tar`、两个配置文件都准备好后，运行转换命令：

```bash
pulsar2 build --target_hardware AX620E --input ./export.onnx --output_dir ./tmp --config ./config/yolo11n.npu.json
mkdir -p out
cp tmp/compiled.axmodel out/yolo11n_npu.axmodel

rm -rf tmp
pulsar2 build --target_hardware AX620E --input ./export.onnx --output_dir ./tmp --config ./config/yolo11n.vnpu.json
cp tmp/compiled.axmodel out/yolo11n_vnpu.axmodel
```

执行成功后，`out/` 目录中会得到 `yolo11n_npu.axmodel` 和 `yolo11n_vnpu.axmodel` 两个模型文件。

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

这里需要根据自己的模型修改下面几项：

| 参数 | 说明 |
|---|---|
| `model_npu` | 完整 NPU 算力模型文件名，例如 `yolo11n_npu.axmodel`。 |
| `model_vnpu` | 给 AI-ISP 预留算力的虚拟 NPU 模型文件名，例如 `yolo11n_vnpu.axmodel`。 |
| `model_type` | MaixPy 已支持的模型类型，例如 `yolo11`、`yolov8`、`classifier`。 |
| `labels` | 模型类别列表，必须和训练数据集的类别数量、顺序完全一致。 |
| `input_cache` / `output_cache` | 代表输入输出是否使用缓存内存。使用缓存能在需要多次读取数据的情况下加快读取速度，比如后处理需要连续多次读取模型输出结果时，建议使用缓存。 |
| `input_cache_flush` | 表示运行模型前是否将内存 cache 刷新到 DDR 中。一般如果模型第一层是 NPU 算子，则必须设置为 `true`。对于 YOLO11，因为模型集成了预处理，也就是说第一层是 CPU 处理，所以设置为 `false`。如果不确定，则设置为 `true`。 |
| `output_cache_inval` | 表示模型运行完成后是否将输出内存缓冲区设置为无效，以保证读取模型输出数据时是直接从 DDR 读取。一般如果模型最后一层是 NPU 算子输出，则必须设置为 `true`；如果是 CPU 算子，则可以设置为 `false` 以减少耗时。如果不确定，可以设置为 `true` 以保证数据正确。 |
| `mean` / `scale` | 实际上在转模型时，预处理已经集成在模型中，这里写出来只是为了方便查看，需要与训练时对模型输入数据的预处理方法保持一致。 |

使用时把 `.mud` 和两个 `.axmodel` 放在同一个目录下。只要 `.mud` 中的文件名和真实文件名一致，MaixPy 就可以通过 `.mud` 找到对应模型。

## 部署到设备和快速验证

MaixPy 加载模型时通常只需要指定 `.mud` 文件路径，`.mud` 中会再指向实际的 `.axmodel` 文件。最省心的做法是把它们放在同一个目录，例如：

```text
/root/models/my_model.mud
/root/models/my_model_npu.axmodel
/root/models/my_model_vnpu.axmodel
```

然后在代码中先确认模型能被加载：

```python
from maix import nn

model = nn.NN("/root/models/my_model.mud")
print(model)
```

如果是 MaixPy 已经支持的模型类型，优先使用对应封装好的 API，例如 YOLO 可以参考 [YOLO 目标检测文档](../vision/yolov5.md)：

```python
from maix import nn

detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)
```

## 调试时先检查这些问题

模型无法加载或运行结果不对时，先按这个顺序排查：

1. `.mud` 和 `.axmodel` 是否在同一个目录，`.mud` 里面的 `model_npu`、`model_vnpu` 文件名是否写对。
2. 设备上填写的路径是否真实存在，比如 `/root/models/xxx.mud`。
3. `labels` 是否和训练时的类别数量、顺序完全一致。
4. `model_type` 是否是 MaixPy 已经支持的类型，比如 `yolo11`、`yolov8`、`classifier` 等。
5. 输入分辨率、`mean`、`scale`、RGB/BGR 顺序是否和训练、导出、转换时保持一致。
6. ONNX 输出节点和 `config.json` 里的 `output_processors` 是否完全一致。
7. 如果不确定是模型问题还是代码问题，先换 MaixHub 或系统内置模型测试；官方模型能跑通后，再调试自己的模型。

提交问题时请提供 ONNX 导出命令、模型任务和类别数、输入输出名称及 shape、完整转换命令、工具版本、MUD、MaixPy / 系统版本和完整错误日志。

确认这些基础项没有问题后，再继续查看对应模型文档或转换流程。如果是 MaixPy 尚未封装的新模型，继续阅读下一节。


## 编写后处理代码

如果模型类型已经被 MaixPy 支持，例如 YOLO 或分类模型，通常不需要自己写后处理，直接调用对应 API 即可。

如果是 MaixPy 尚未封装的新模型，需要根据模型输出自己实现后处理，可以按目标选择下面方式：

* **快速验证**：使用 `maix.nn.NN` 加载 `.mud`，通过 `forward` 或 `forward_image` 得到原始输出，然后在 Python 中写后处理逻辑。完整流程可参考[移植新模型](../pro/customize_model.md)。
* **正式封装**：在 `MaixCDK` 中新增模型解码类，让 `MaixCDK` 和 `MaixPy` 都可以调用，运行效率也更高。可以参考 [YOLOv5 源码](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp)，新增对应 `hpp` 文件，补齐 `@maixpy` 注释后重新编译 MaixPy。

支持了新模型后还可以将源码提交（Pull Request）到主`MaixPy`仓库中，成为`MaixPy`项目的一员，为社区做贡献，也可以到 [MaixHub 分享](https://maixhub.com/share) 分享你新支持的模型，根据质量可以获得最少 `30元` 最高 `2000元` 的打赏！
