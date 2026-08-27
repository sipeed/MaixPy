---
title: 网页转换 YOLO 模型
---

电脑训练得到的 `.pt` 或 `.onnx` 不能直接在 MaixCAM 上运行。MaixHub 网页转换工具会生成板子需要的 `.mud`、`.cvimodel` 或 `.axmodel`，不用在电脑上安装转换环境。

## 确认模型是否支持

网页目前支持 MaixCAM、MaixCAM Pro 和 MaixCAM2，以及下面这些目标检测模型：

- YOLO26
- YOLO11
- YOLOv8
- YOLOv5u

目标检测指的是“找出物体并画框”。分类、姿态、分割、旋转框和旧版 YOLOv5 暂不支持，需要使用页面末尾的手动转换入口。

YOLOv5u 是 Ultralytics 工具中的新版 YOLOv5，与旧 `ultralytics/yolov5` 仓库里的模型不同。模型来源不明确时，先向模型作者确认版本。

## 只有 PT 时先导出 ONNX

`.pt` 是训练结果，`.onnx` 是网页转换工具接收的模型格式。已经有 `.onnx` 时，可以跳过这一节。

> **本页示例的兼容性提醒**
>
> 本页介绍的是网页支持的 YOLO 目标检测模型。按下面命令导出时，固定使用 `ultralytics==8.4.104`，并保留 `opset=17`、`dynamic=False`。其他模型或转换路线可能有不同要求，请以对应文档为准。

先安装导出工具：

```shell
python -m pip install ultralytics==8.4.104 ultralytics-thop onnx onnxslim onnxruntime
```

假设模型名是 `best.pt`。MaixCAM 和 MaixCAM Pro 使用：

```shell
yolo export model=best.pt format=onnx imgsz=224,320 opset=17 simplify=True dynamic=False
```

MaixCAM2 使用：

```shell
yolo export model=best.pt format=onnx imgsz=240,320 opset=17 simplify=True dynamic=False
```

导出成功后，`best.pt` 旁边会出现 `best.onnx`。命令中的尺寸顺序是“高,宽”。`opset=17` 是转换所需的 ONNX 规则版本，`dynamic=False` 表示固定输入尺寸；其余参数也保持不变。

## 准备转换参考图片

从真实使用场景中选择 20 到 100 张图片。例如苹果模型以后要看桌面，就选择不同桌面、光线和摆放方式的图片。

这些图片只帮助转换工具适配板子，不会重新训练模型，所以不用画框，也不用加入标注文件。

把图片直接压缩成 ZIP：

```text
apple_images.zip
├── 001.jpg
├── 002.jpg
├── 003.png
└── ...
```

ZIP 不能超过 100MB。图片数量不要少于 20，也不要多于 100。

网页需要接收模型和图片。如果文件包含隐私或商业机密，不要上传，请改用本地手动转换。

## 创建转换任务

1. 打开 [MaixHub 工具箱](https://maixhub.com/toolbox)，进入模型转换工具。
2. 选择自己的板子、YOLO 版本和目标检测。
3. 上传 `best.onnx` 和图片 ZIP。
4. 检查标签。网页没有自动读出时，手动填写，并保持与训练时相同的顺序。
5. 开始转换，等页面显示成功后下载结果。

任务可能需要排队。页面仍在转换时，不要重复提交。

## 检查并运行结果

解压下载的文件。MaixCAM 和 MaixCAM Pro 应该有 `.mud` 和 `.cvimodel`；MaixCAM2 应该有 `.mud` 和一个或两个 `.axmodel`。

同一个模型包里的文件要一起上传，不能只上传 `.mud`。接着按[把模型传到板子](./ai_model_deploy.md#把模型传到板子)和[运行模型](./ai_model_deploy.md#运行模型)完成测试。

摄像头画面出现正确标签和方框，就说明转换成功。到这里，转换和上板运行已经完成。如果愿意交流或提供模型下载，可以再选择[分享到 MaixHub](./ai_model_deploy.md#可选分享到-maixhub)。

## 转换失败怎么办

- **上传后立即失败**：确认文件是 `.onnx`，模型属于网页支持的 YOLO 版本，并且导出时使用了固定尺寸。
- **提示图片不足**：页面填写的图片数量不能多于 ZIP 中的实际图片数。
- **转换成功但没有方框**：先在电脑上测试同一个 `.onnx`。电脑上也没有结果时，应回到训练或导出步骤检查。
- **模型或图片不能上传到外部服务**：不要使用网页转换，改用本地手动转换。

网页不支持时，再看[MaixCAM2 手动转换](./maixcam2.md)、[MaixCAM 手动转换](./maixcam.md)或[移植新模型](../pro/customize_model.md)。这些进阶路线需要安装专用转换环境，并了解模型的输入和输出。
