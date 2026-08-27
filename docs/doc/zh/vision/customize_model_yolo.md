---
title: 在电脑训练 YOLO 检测模型
---

这篇继续用苹果检测做例子。你会在电脑上训练 YOLO11，得到 `best.pt`，再导出板子转换工具需要的 `best.onnx`。

如果是第一次训练，建议先用 [MaixHub 在线训练](./maixhub_train.md)。电脑训练需要安装 Python，适合想保留全部数据或自己控制训练过程的用户。

## 开始前准备好数据集

先按[准备模型和数据集](../pro/datasets.md)整理好图片、标注和 `data.yaml`。数据集的标准目录只在那一页说明，本页直接从安装训练工具开始。

## 安装训练工具

YOLO 是一组常用的目标检测模型。本文使用 Ultralytics 提供的训练工具。

先从 [Python 官网](https://www.python.org/downloads/)安装 Python 3，建议使用 3.11。Windows 安装界面要勾选 `Add Python to PATH`，这样终端才能找到 Python。

打开终端。Windows 可以使用 PowerShell，macOS 和 Linux 可以使用系统自带的“终端”。先检查 Python：

```shell
python --version
```

看到 `Python 3...` 后，安装训练工具。如果系统提示找不到 `python`，把本页命令中的 `python` 换成 `python3`。

```shell
python -m pip install ultralytics==8.4.104
```

安装完成后检查：

```shell
yolo checks
```

终端能打印 Python 和运行环境信息，就可以开始训练。如果提示找不到 `yolo`，关闭终端重新打开，再执行检查命令。

## 先跑 3 轮检查数据

下面的命令只训练 3 轮，目的是尽快发现路径、图片或标注格式问题：

```shell
yolo detect train model=yolo11n.pt data=/你的完整路径/apple_dataset/data.yaml epochs=3 imgsz=640 project=runs/apple name=check exist_ok=True
```

`yolo11n.pt` 是一个体积较小的基础模型，适合先跑通流程。`epochs=3` 表示把训练集学习 3 遍，`imgsz=640` 表示训练时把图片处理为 640 像素大小。第一次使用时保持这些值即可。

命令正常结束，并在 `runs/apple/check` 下生成结果，就说明数据格式可以使用。第一次运行会自动下载 `yolo11n.pt`，因此电脑需要联网。

## 正式训练

把训练轮数改为 100：

```shell
yolo detect train model=yolo11n.pt data=/你的完整路径/apple_dataset/data.yaml epochs=100 imgsz=640 project=runs/apple name=model exist_ok=True
```

训练结束后使用这个文件：

```text
runs/apple/model/weights/best.pt
```

`best.pt` 是验证效果最好的一轮，不一定是最后一轮。

## 用新图片测试

准备一张没有参加训练的苹果图片：

```shell
yolo detect predict model=runs/apple/model/weights/best.pt source=/测试图片路径 save=True
```

终端会打印结果保存位置。打开图片，确认苹果类别和方框正确。

如果训练图片能识别，新图片却不行，先补充不同苹果、背景和光线的图片。继续增加训练轮数通常不能弥补数据缺失。

## 导出 ONNX

`.pt` 不能直接交给板子转换工具，需要先导出为 `.onnx`。

> **本页示例的兼容性提醒**
>
> 下面这条网页转换路线以 YOLO11 为例，请固定安装 `ultralytics==8.4.104`，并保留 `opset=17`、`dynamic=False`。不同模型或不同转换路线可能有自己的版本和参数要求，不能直接照搬本页设置。

MaixCAM 和 MaixCAM Pro 常用 `320x224`：

```shell
yolo export model=runs/apple/model/weights/best.pt format=onnx imgsz=224,320 opset=17 simplify=True dynamic=False
```

MaixCAM2 可以先用 `320x240`：

```shell
yolo export model=runs/apple/model/weights/best.pt format=onnx imgsz=240,320 opset=17 simplify=True dynamic=False
```

需要识别更小的目标时，MaixCAM2 可以尝试 `640x480`，但运行会更慢：

```shell
yolo export model=runs/apple/model/weights/best.pt format=onnx imgsz=480,640 opset=17 simplify=True dynamic=False
```

命令里的尺寸顺序是“高,宽”。导出成功后，`best.pt` 旁边会出现 `best.onnx`。

`opset` 是 ONNX 文件所用的规则版本，这里必须保持为 `17`。`dynamic=False` 表示固定模型输入尺寸，`simplify=True` 用于简化模型结构。这三个值都不要删除或修改。

## 转换并在板子上运行

接下来按顺序完成：

1. 使用[网页转换 YOLO 模型](../ai_model_converter/online_converter.md)，把 `best.onnx` 转成板子模型包。
2. 按[上板和运行教程](../ai_model_converter/ai_model_deploy.md#把模型传到板子)上传并测试。

摄像头画面出现正确标签和方框后，训练、转换和上板运行就完成了。如果愿意让其他用户下载和交流，可以再选择[分享到 MaixHub](../ai_model_converter/ai_model_deploy.md#可选分享到-maixhub)。

## 使用其它 YOLO 版本

想换成 YOLO26 或 YOLOv8，可以把训练命令中的基础模型改为 `yolo26n.pt` 或 `yolov8n.pt`。但不要直接照搬本页的工具版本和导出参数，请先查看对应模型的说明。

旧 `ultralytics/yolov5` 仓库训练的 YOLOv5 与新版 YOLOv5u 输出不同，目前不能使用简单网页转换。维护旧项目时，请使用 [MaixCAM 手动转换](../ai_model_converter/maixcam.md)或[MaixCAM2 手动转换](../ai_model_converter/maixcam2.md)。新项目建议使用 YOLO11。

姿态、分割和旋转框使用不同的标注格式，而且网页转换暂不支持。需要这些功能时，请继续阅读对应的[人体关键点检测](./body_key_points.md)、[图像语义分割](./segmentation.md)或[旋转框检测](./detect_obb.md)文档。
