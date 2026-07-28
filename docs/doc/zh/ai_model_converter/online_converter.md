---
title: 在线转换 YOLO 模型
---

## 简介

MaixCAM 模型转换工具是 Sipeed 部署好的网页模型转换服务。你不需要在本机安装 Docker、Pulsar2 或 TPU-MLIR 环境，只需要准备 ONNX 模型文件和量化图片数据集，在网页中创建转换任务，等待平台完成转换后下载结果即可。

在线平台适合快速转换常见 YOLO Detect 模型，并生成可以直接在 MaixCAM、MaixCAM Pro 或 MaixCAM2 上部署的模型文件。如果需要内网部署、自管转换环境，或不方便上传模型文件到在线服务，请参考[私有部署图形化模型转换平台](./web_converter.md)。

## 当前支持

目前平台支持的设备和模型如下：

| 项目 | 支持范围 |
| --- | --- |
| 目标设备 | MaixCAM、MaixCAM Pro、MaixCAM2 |
| 模型类型 | YOLO26、YOLO11、YOLOv8、YOLOv5u |
| 任务类型 | 目标检测（Detect） |
| 输入模型 | `.onnx` |
| 量化数据集 | 包含 20～100 张 `.jpg`、`.png` 或 `.bmp` 图片的 `.zip` 文件，不能大于 100MB |

> 当前暂不支持分类、分割、姿态检测和 OBB 等任务。其他模型或者需要自定义转换参数时，请使用前面介绍的手动转换方法，或自行私有部署转换平台后按需修改。
>
> YOLOv5u 属于 Ultralytics 新版 `ultralytics` 仓库中的模型，推理代码直接使用 `nn.YOLOv8` 即可，不要使用 `nn.YOLOv5`。

## 打开在线平台

在浏览器中打开在线模型转换平台：

[MaixHub Converter tool](https://maixhub.com/toolbox)

## 将 PT 模型导出为 ONNX

在线平台只支持上传 `.onnx` 模型。如果你训练得到的是 `.pt` 权重文件，需要先在电脑上导出为 ONNX，再上传到平台转换。

对于使用 Ultralytics 训练得到的 YOLO26、YOLO11、YOLOv8 或 YOLOv5u 模型，训练和导出 ONNX 都建议固定使用 `ultralytics==8.4.104`，避免不同版本导出的模型结构或输出节点不一致，导致后续转换失败。

先安装指定版本的导出工具：

```shell
pip install ultralytics==8.4.104 ultralytics-thop onnx onnxslim onnxruntime -i https://pypi.tuna.tsinghua.edu.cn/simple
```

然后根据目标设备选择合适的输入分辨率。前面模型转换文档中推荐 MaixCAM 使用 `320x224`，MaixCAM2 使用 `640x480` 或 `320x240`。这里的分辨率按“宽 x 高”描述，而 Ultralytics 导出命令中的 `imgsz` 按“高,宽”填写。

以 MaixCAM 为例，导出 `320x224` 输入的 ONNX：

```shell
yolo export model=best.pt format=onnx imgsz=224,320 opset=17 simplify=True
```

以 MaixCAM2 为例，导出 `640x480` 输入的 ONNX：

```shell
yolo export model=best.pt format=onnx imgsz=480,640 opset=17 simplify=True
```

如果希望 MaixCAM2 使用更小分辨率提高运行速度，也可以导出 `320x240` 输入的 ONNX：

```shell
yolo export model=best.pt format=onnx imgsz=240,320 opset=17 simplify=True
```

其中 `model` 替换为你的 `.pt` 文件路径，`imgsz` 设置为模型部署时使用的输入分辨率。导出完成后通常会在同目录生成 `best.onnx`。

导出后建议用 Netron 或其它 ONNX 查看工具确认模型输入尺寸是固定尺寸，并且与后续在平台中填写的宽度、高度一致。

## 准备模型和量化数据集

模型文件只支持 `.onnx` 格式。平台会使用 ONNX 模型自身的静态输入尺寸进行后续处理和转换，不会在上传后重新调整模型尺寸。建议在导出 ONNX 时就确定好最终部署使用的输入分辨率。

量化数据集需要打包为 `.zip` 文件，压缩包中只需要图片，不需要标注文件。图片数量需要在 20～100 张之间，支持 `.jpg`、`.png` 和 `.bmp` 格式，上传的 ZIP 文件不能大于 100MB。

压缩包中可以直接放置图片：

```text
dataset.zip
  000001.jpg
  000002.jpg
  000003.jpg
```

量化图片应该尽量接近模型部署后的真实使用场景。例如模型将用于摄像头拍摄，就优先使用同类摄像头在实际环境中采集的图片。建议先准备 20～50 张图片快速验证流程，正式转换时再根据数据集情况增加到接近 100 张。

## 创建转换任务

打开网页后，按照页面从上到下填写转换参数：

![MaixHub 创建转换任务](../../assets/maixhub_converter_create_job.jpg)

平台一般会自己识别出模型里面的标签，如果没有的话就手动填上去。

![MaixHub 模型标签设置](../../assets/maixhub_converter_labels.jpg)

填写完成后点击“开始转换”。页面会显示文件上传进度、当前任务状态和实时转换日志。转换时间与模型大小、量化图片数量以及服务器任务排队情况有关，请耐心等待。

等待转换完成

![MaixHub 转换任务完成](../../assets/maixhub_converter_job_done.jpg)

## 下载转换结果

![MaixHub 下载转换结果](../../assets/maixhub_converter_download_result.jpg)

MaixCAM2 的结果通常包含：

```text
model_name.mud
model_name_npu.axmodel
model_name_vnpu.axmodel
```

MaixCAM 和 MaixCAM Pro 的结果通常包含：

```text
model_name.mud
model_name.cvimodel
```

## 把模型文件传送到 MaixCAM / MaixCAM Pro / MaixCAM2

1. 打开 MaixVision，连接上设备。

2. 点击设备文件管理器。

![MaixVision 设备文件管理器](../../assets/maixvision_file_manager.jpg)

3. 在 `root` 目录新建一个 `my_models` 文件夹，用来保存刚刚转换的模型。

![MaixVision 新建 my_models 文件夹](../../assets/maixvision_create_my_models.jpg)

4. 单击 `my_models` 文件夹，进入到 `my_models` 文件夹。

![MaixVision 进入 my_models 文件夹](../../assets/maixvision_enter_my_models.jpg)

5. 把转换出来的文件上传到 `my_models` 目录。如果是 MaixCAM / MaixCAM Pro，上传 `.mud` 和 `.cvimodel` 文件；如果是 MaixCAM2，上传 `.mud` 和 `.axmodel` 文件。

![MaixVision 上传模型文件](../../assets/maixvision_upload_model_files.jpg)

6. 编写推理代码。

下面以 YOLOv8 为例：

假设你刚刚得到的 `.mud` 文件是 `model_4090.mud`。

```python
from maix import app, camera, display, image, nn

detector = nn.YOLOv8(model="/root/my_models/model_4090.mud", dual_buff=True)
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        msg = f"{detector.labels[obj.class_id]}: {obj.score:.2f}"
        img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
    disp.show(img)
```

如果转换的是 YOLO26 或 YOLO11，请将示例中的 `nn.YOLOv8` 换成对应的 MaixPy 模型接口。

## 注意事项

- 上传模型前请确认模型来源和授权，避免上传没有使用权限的模型文件。
- 在线平台只接受 ONNX 模型；如果手上是 `.pt` 权重，请先导出 ONNX。
- 量化数据集需要包含 20～100 张 `.jpg`、`.png` 或 `.bmp` 图片，ZIP 文件大小不能超过 100MB。
- 如果模型或数据集包含敏感信息，建议使用[私有部署图形化模型转换平台](./web_converter.md)在自有服务器中转换。
- 转换任务可能需要排队，耗时与模型大小、量化图片数量和服务器负载有关。
- 转换成功后请及时下载结果，避免任务过期或被清理。
- 在线平台主要面向通用 YOLO Detect 转换；需要修改 Docker 镜像、工具链参数或生成逻辑时，请使用私有部署方式。

## 常见问题

### 量化图片数量不足

页面中的“图片数量”需要在 20～100 之间，并且不能大于 ZIP 文件中实际包含的有效图片数量。如果只准备了 50 张图片，就不要将图片数量设置为 100。

### 自训练模型的类别不正确

平台会尝试从 ONNX metadata 中读取类别名称。如果模型运行后类别数量或名称不正确，请检查生成的 `.mud` 文件中 `labels` 的内容是否与训练模型一致。

### 转换任务失败

先查看页面中的实时日志，确认模型格式、YOLO 版本、输入分辨率、量化图片数量是否正确。如果日志中提示模型算子不支持、输出节点异常或量化失败，需要回到训练、导出 ONNX 或手动转换流程中排查。
