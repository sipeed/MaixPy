---
title: 手动转换给 MaixCAM 用
---

> MaixCAM2 模型转换请看 [MaixCAM2 模型转换文档](./maixcam2.md)

> 这是进阶文档。普通 YOLO 检测模型请先使用[网页转换](./online_converter.md)，不需要安装 Docker。只有网页不支持模型或需要自定义参数时，才继续阅读本文。

## 简介

电脑上训练的模型不能直接给 MaixCAM / MaixCAM-Pro 使用，需要先将模型转换为设备支持的 `.cvimodel` 格式，并配套编写 `.mud` 模型描述文件。本文以 YOLOv8 检测模型为例，说明从 ONNX 到 MaixCAM 可运行模型的完整流程。

## MaixCAM 支持的模型文件格式

MUD（Model Universal Description，模型统一描述文件）是 MaixPy 支持的模型描述文件，用来统一不同平台的模型加载方式。它本质上是一个 `ini` 格式的文本文件，可以使用文本编辑器编辑。

对于 MaixCAM / MaixCAM-Pro，实际模型文件是 `.cvimodel`，`.mud` 文件负责描述模型文件路径、模型类型、预处理参数和类别列表。常见文件组合如下：

```text
yolov8n.mud
yolov8n_int8.cvimodel
```

使用时建议把 `.mud` 和 `.cvimodel` 放在同一个目录，避免路径写错。

## 准备 ONNX 模型

本节的目标是先得到一个可以被 `tpu-mlir` 读取的 `.onnx` 文件。ONNX 一般来自下面几种情况：

1. **自己训练后导出**：例如 YOLOv8 / YOLO11 训练得到 `.pt` 文件后，按[在电脑训练 YOLO 检测模型](../vision/customize_model_yolo.md)导出。MaixCAM 常用输入尺寸为 `320x224`，建议使用固定输入尺寸，不要使用动态输入尺寸。
2. **其它训练框架导出**：例如 PyTorch、TensorFlow 等框架训练后导出 ONNX。导出后需要确认模型输入尺寸固定，并且输入、输出节点可以在 Netron 中正常查看。
3. **第三方提供的 ONNX**：可以直接从 ONNX 开始转换，但需要确认模型授权可用，并且模型结构适合在 MaixCAM 上运行。

若已获取 `.mud` 和 `.cvimodel` 文件，表示该模型已完成面向 MaixCAM 的转换，可直接部署使用，无需执行本文转换流程。

获取 ONNX 文件后，建议将其放置在独立工作目录，并统一命名为 `model.onnx`。随后使用 [Netron](https://netron.app/) 打开模型，核对并记录以下信息：

| 信息项 | 获取方式 | 后续用途 |
| --- | --- | --- |
| 输入节点名称 | 在 Netron 的输入节点区域查看，常见名称为 `images` | 用于 ONNX 裁剪命令的输入参数 |
| 输入尺寸 | 在 Netron 的输入节点形状中查看，例如 `1x3x224x320` | 用于 `model_transform.py` 的 `--input_shapes` 参数 |
| 候选输出节点 | 查看模型末端用于后处理前的输出节点 | 用于 ONNX 裁剪命令和 `model_transform.py` 的 `--output_names` 参数 |

同时需要确认模型算子位于 `tpu-mlir` 支持范围内。MaixCAM 对应 `cv181x` 处理器；若转换过程中提示某个算子不受支持，应回到训练 / 导出阶段调整模型结构，或选用 MaixPy 已支持的模型结构。

## 找出合适的量化输出节点

本节的目标是得到裁剪后的 `export.onnx`，后面的转换命令会直接使用它。

很多检测模型在 ONNX 末尾带有后处理节点，这些节点通常更适合由 CPU 处理。直接把完整 ONNX 拿去量化，可能会导致量化误差变大或转换失败。因此需要先选择合适的输出节点，再裁剪 ONNX。

可按下表选择常见模型的输出节点。YOLOv5、分类模型和其他模型的裁剪方法可参考[裁剪 ONNX 模型节点教程](./onnx_export.md)。

| 模型类型 | 推荐输出节点选择 | 下一步 |
| --- | --- | --- |
| YOLOv8 检测模型 | MaixCAM 推荐使用 `/model.22/dfl/conv/Conv_output_0` 和 `/model.22/Sigmoid_output_0` | 复制节点名后裁剪 ONNX |
| YOLO11 检测模型 | MaixCAM 推荐使用 `/model.23/dfl/conv/Conv_output_0` 和 `/model.23/Sigmoid_output_0` | 复制节点名后裁剪 ONNX |
| YOLOv5 检测模型 | 常见为三个检测头输出，例如 `/model.24/m.0/Conv_output_0`、`/model.24/m.1/Conv_output_0`、`/model.24/m.2/Conv_output_0` | 复制节点名后裁剪 ONNX |
| pose / seg / obb 模型 | 输出节点数量更多，需要按对应任务文档确认 | 复制对应节点名后再按裁剪教程操作 |
| 分类模型 | 一般取最后一层分类输出；如果末尾有 `softmax`，建议取 `softmax` 前一层输出 | 记录该输出节点名 |

如果你的节点名称和表格不完全一致，请用 Netron 找到位置相同、含义相同的输出节点，而不是机械复制。确定输入节点名和输出节点名后，先安装裁剪和简化 ONNX 需要的工具：

```bash
pip install onnx onnxsim
```

以 YOLOv8 检测模型为例，执行下面命令裁剪 ONNX：

```bash
python -c "import onnx,sys; onnx.utils.extract_model(sys.argv[1], sys.argv[2], [s.strip() for s in sys.argv[3].split(',')], [s.strip() for s in sys.argv[4].split(',')])" model.onnx tmp_extract.onnx "images" "/model.22/dfl/conv/Conv_output_0,/model.22/Sigmoid_output_0"
onnxsim tmp_extract.onnx export.onnx
```

请把命令中的：

* `model.onnx` 替换为你的原始 ONNX 文件名。
* `"images"` 替换为 Netron 中看到的输入节点名。
* `"/model.22/dfl/conv/Conv_output_0,...` 替换为你选择的输出节点名，多个节点用英文逗号分隔。

命令执行成功后，当前目录会得到 `export.onnx`。后文所有 `--model_def ./export.onnx` 都指这个裁剪并简化后的文件。更完整的裁剪说明可看 [裁剪 ONNX 模型节点教程](./onnx_export.md)。

## 安装模型转换环境

MaixCAM 模型转换使用算能的 [tpu-mlir](https://github.com/sophgo/tpu-mlir)。建议放在 Docker 容器中运行，避免本机 Python、系统库版本不一致导致转换失败。

如果电脑还没有安装 Docker，请先按 [Docker 官方文档](https://docs.docker.com/engine/install/ubuntu/) 安装。安装完成后执行下面命令，能看到版本号就表示 Docker 可用：

```shell
docker --version
```

然后拉取转换环境镜像：

```shell
docker pull sophgo/tpuc_dev:latest
```

如果拉取失败，可以按 tpu-mlir 官方说明下载镜像压缩包并加载：

```shell
wget https://sophon-file.sophon.cn/sophon-prod-s3/drive/24/06/14/12/sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
docker load -i sophgo-tpuc_dev-v3.2_191a433358ad.tar.gz
```

加载完成后查看实际镜像名：

```shell
docker images | grep tpuc
```

进入模型转换工作目录并启动容器：

```shell
mkdir -p ~/maixcam_convert
cd ~/maixcam_convert
docker run --privileged --rm -it -v "$PWD":/workspace -w /workspace sophgo/tpuc_dev:latest
```

如果你的镜像名不是 `sophgo/tpuc_dev:latest`，请把命令最后的镜像名替换为 `docker images` 看到的实际名称。进入容器后，当前目录就是 `/workspace`，后面的 `export.onnx`、测试图片和校准图片都放在这个目录里。

在容器内安装并检查 `tpu-mlir`：

```shell
pip install tpu_mlir
model_transform.py --help
```

如果 `model_transform.py --help` 能输出帮助信息，说明环境可用。

## 转换 ONNX 模型到 cvimodel

运行转换前，工作目录中至少应准备好这些文件：

```text
.
├── export.onnx
├── test.jpg
└── images/
    ├── 0001.jpg
    ├── 0002.jpg
    └── ...
```

| 文件 | 如何得到 | 作用 |
| --- | --- | --- |
| `export.onnx` | 上一步裁剪并简化 ONNX 后得到 | 作为 `model_transform.py` 的输入模型 |
| `test.jpg` | 任意一张符合模型输入场景的测试图片 | 用于转换时对比 ONNX 和 MLIR 输出 |
| `images/` | 放 20 到 200 张真实场景图片 | 用于 INT8 量化校准 |

图片越接近实际使用场景，量化后的模型效果越稳定。例如要识别桌面物体，就放桌面环境下拍摄的图片；要识别产线物料，就放产线相机拍到的图片。

### 生成 MLIR 中间文件

以 YOLOv8 检测模型为例，先执行 `model_transform.py`：

```bash
model_transform.py \
--model_name yolov8n \
--model_def ./export.onnx \
--input_shapes [[1,3,224,320]] \
--mean "0,0,0" \
--scale "0.00392156862745098,0.00392156862745098,0.00392156862745098" \
--keep_aspect_ratio \
--pixel_format rgb \
--channel_format nchw \
--output_names "/model.22/dfl/conv/Conv_output_0,/model.22/Sigmoid_output_0" \
--test_input ./test.jpg \
--test_result yolov8n_top_outputs.npz \
--tolerance 0.99,0.99 \
--mlir yolov8n.mlir
```

这个命令成功后，会得到 `yolov8n.mlir`、`yolov8n_in_f32.npz` 和 `yolov8n_top_outputs.npz`。后面的部署命令会继续使用这些文件。

关键参数说明：

| 参数 | 填写内容 |
| --- | --- |
| `--model_name` | 模型名称，用于生成中间文件名，例如 `yolov8n` |
| `--model_def` | 裁剪后的 ONNX，例如 `./export.onnx` |
| `--input_shapes` | 模型输入尺寸，顺序是 `[N,C,H,W]`，例如 `[[1,3,224,320]]` |
| `--mean` / `--scale` | 训练时使用的预处理参数，需要和训练、导出时保持一致 |
| `--output_names` | ONNX 输出节点名，必须和裁剪 `export.onnx` 时选择的输出节点一致 |
| `--test_input` | 测试图片路径，例如 `./test.jpg` |
| `--test_result` | 输出对比结果文件，下一步会作为参考 |
| `--mlir` | 生成的 MLIR 中间文件 |

### 生成 INT8 cvimodel

MaixCAM 上一般优先使用 INT8 模型，速度更快、内存占用更低。先用校准图片生成量化表：

```bash
run_calibration.py yolov8n.mlir \
--dataset ./images \
--input_num 50 \
-o yolov8n_cali_table
```

`--input_num` 表示实际参与校准的图片数量，不能大于 `images/` 目录中的图片数量。新手可以先准备 50 张左右真实场景图片，后续根据效果再增加。

然后生成 `.cvimodel`：

```bash
model_deploy.py \
--mlir yolov8n.mlir \
--quantize INT8 \
--quant_input \
--calibration_table yolov8n_cali_table \
--processor cv181x \
--test_input yolov8n_in_f32.npz \
--test_reference yolov8n_top_outputs.npz \
--tolerance 0.9,0.6 \
--model yolov8n_int8.cvimodel
```

执行成功后，当前目录会得到 `yolov8n_int8.cvimodel`。

如果 INT8 转换失败，可以先检查输出节点、输入尺寸、预处理参数和校准图片是否正确。确实无法通过时，再尝试 BF16：

```bash
model_deploy.py \
--mlir yolov8n.mlir \
--quantize BF16 \
--processor cv181x \
--test_input yolov8n_in_f32.npz \
--test_reference yolov8n_top_outputs.npz \
--model yolov8n_bf16.cvimodel
```

BF16 模型通常精度更容易保持，但速度和内存占用一般不如 INT8，建议只作为排查或特殊精度需求时使用。

## 编写 mud 文件

`.mud` 和 `.cvimodel` 必须放在同一个目录。以 `yolov8n_int8.cvimodel` 为例，新建 `yolov8n.mud`：

```ini
[basic]
type = cvimodel
model = yolov8n_int8.cvimodel

[extra]
model_type = yolov8
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```

这里需要根据自己的模型修改下面几项：

| 参数 | 说明 |
| --- | --- |
| `model` | `.cvimodel` 文件名，例如 `yolov8n_int8.cvimodel` |
| `model_type` | MaixPy 已支持的模型类型，例如 `yolov5`、`yolov8`、`yolo11`、`classifier` |
| `mean` / `scale` | 预处理参数，需要与训练、导出、转换时保持一致 |
| `labels` | 模型类别列表，必须和训练数据集的类别数量、顺序完全一致 |

例如训练的是数字检测模型，类别顺序为 `0` 到 `9`，则 `labels` 应写为：

```ini
labels = 0,1,2,3,4,5,6,7,8,9
```

## 部署到设备和快速验证

MaixPy 加载模型时通常只需要指定 `.mud` 文件路径，`.mud` 中会再指向实际的 `.cvimodel` 文件。最省心的做法是把它们放在同一个目录，例如：

```text
/root/models/yolov8n.mud
/root/models/yolov8n_int8.cvimodel
```

然后在代码中先确认模型能被加载：

```python
from maix import nn

model = nn.NN("/root/models/yolov8n.mud")
print(model)
```

如果是 MaixPy 已经支持的模型类型，优先使用对应封装好的 API，例如 YOLO 可以参考 [YOLO 目标检测文档](../vision/yolov5.md)：

```python
from maix import nn

detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff=True)
```

## 调试时先检查这些问题

模型无法加载或运行结果不对时，先按这个顺序排查：

1. `.mud` 和 `.cvimodel` 是否在同一个目录，`.mud` 里的 `model` 文件名是否写对。
2. 设备上填写的路径是否真实存在，比如 `/root/models/yolov8n.mud`。
3. `labels` 是否和训练时的类别数量、顺序完全一致。
4. `model_type` 是否是 MaixPy 已经支持的类型，比如 `yolov5`、`yolov8`、`yolo11`、`classifier` 等。
5. 输入分辨率、`mean`、`scale`、RGB/BGR 顺序是否和训练、导出、转换时保持一致。
6. ONNX 输出节点、裁剪命令和 `model_transform.py` 的 `--output_names` 是否完全一致。
7. 如果不确定是模型问题还是代码问题，先换 MaixHub 或系统内置模型测试；官方模型能跑通后，再调试自己的模型。

确认这些基础项没有问题后，再继续查看对应模型文档或转换流程。如果是 MaixPy 尚未封装的新模型，继续阅读下一节。

## 编写后处理代码

如果模型类型已经被 MaixPy 支持，例如 YOLO 或分类模型，通常不需要自己写后处理，直接调用对应 API 即可。

如果是 MaixPy 尚未封装的新模型，需要根据模型输出自己实现后处理，可以按目标选择下面方式：

* **快速验证**：使用 `maix.nn.NN` 加载 `.mud`，通过 `forward` 或 `forward_image` 得到原始输出，然后在 Python 中写后处理逻辑。完整流程可参考[移植新模型](../pro/customize_model.md)。
* **正式封装**：在 `MaixCDK` 中新增模型解码类，让 `MaixCDK` 和 `MaixPy` 都可以调用，运行效率也更高。可以参考 [YOLOv5 源码](https://github.com/sipeed/MaixCDK/blob/71d5b3980788e6b35514434bd84cd6eeee80d085/components/nn/include/maix_nn_yolov5.hpp)，新增对应 `hpp` 文件，补齐 `@maixpy` 注释后重新编译 MaixPy。

支持了新模型后还可以将源码提交（Pull Request）到主 `MaixPy` 仓库中，成为 `MaixPy` 项目的一员，为社区做贡献，也可以到 [MaixHub 分享](https://maixhub.com/share) 分享你新支持的模型，根据质量获得打赏。
