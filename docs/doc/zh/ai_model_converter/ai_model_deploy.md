---
title: AI 模型下载、调试和部署指南
---

## 选择模型部署方式

首次进行 MaixCAM / MaixCAM-Pro / MaixCAM2 本地模型部署时，建议先明确模型来源、目标设备和部署方式。请根据当前已有资源选择对应流程：能直接使用现成模型时不要重新训练；需要识别自定义目标时先训练模型；训练得到 `.pt` 后先导出 ONNX，再优先使用在线转换平台生成设备可部署的模型文件。手动命令行转换适合需要自定义转换参数或排查复杂问题的进阶场景。

| 使用目标 | 建议流程 | 查看文档 |
| --- | --- | --- |
| 使用预置或现成模型 | 优先使用系统预置模型；如需更多分辨率或类别，可在 [MaixHub 模型库](https://maixhub.com/model/zoo) 选择对应设备平台。MaixCAM / MaixCAM-Pro 模型包通常包含 `.mud` 与 `.cvimodel`，MaixCAM2 模型包通常包含 `.mud` 与 `.axmodel`，部署时放入设备同一目录 | [模型与数据集来源](../pro/datasets.md) |
| 训练自定义识别目标 | 使用 MaixHub 在线训练完成数据采集、标注、训练与部署 | [MaixHub 在线训练](../vision/maixhub_train.md) |
| 离线训练 YOLO 模型 | 在电脑上准备数据集并训练 YOLO 模型，训练和导出建议使用指定版本的 Ultralytics。训练得到 `.pt` 后，先按文档导出固定输入尺寸的 `.onnx` | [离线训练 YOLO 模型](../vision/customize_model_yolo.md) |
| 在线转换 YOLO 模型 | 上传 ONNX 模型和 20～100 张量化图片组成的 ZIP 包，在线生成 MaixCAM / MaixCAM-Pro 的 `.mud` + `.cvimodel`，或 MaixCAM2 的 `.mud` + `.axmodel` | [在线图形化模型转换平台](./online_converter.md) |
| 手动转换 ONNX 模型 | 需要自定义输出节点、转换参数、工具链配置，或在线转换无法满足需求时，再使用命令行手动转换流程 | [MaixCAM2 模型转换](./maixcam2.md) / [MaixCAM 模型转换](./maixcam.md) / [裁剪 ONNX 模型输出节点](./onnx_export.md) |
| 私有部署转换平台 | 不方便上传模型到在线服务，或需要内网部署、自管转换服务器、调试平台源码时使用 | [私有部署图形化模型转换平台](./web_converter.md) |
| 移植新的 AI 模型 | MaixPy 尚未封装的模型类型，需要自行处理前后处理、MUD 描述和推理代码 | [移植新的 AI 模型](../pro/customize_model.md) |

选定流程后，进入对应文档继续操作即可。
