---
title: 图形化模型转换平台
---

## 简介

看完前面的模型转换教程，是不是已经被一长串命令绕晕了？导出 ONNX、查找输出节点、裁剪模型、准备量化数据集、修改配置文件、运行 Docker……步骤一个接一个，少写一个参数都可能要从头检查。好不容易训练出了 `.pt` 模型，却发现“转换模型”似乎比“训练模型”还让人头大。

别担心，也不用再抱着命令行逐个参数对答案了！Maix Converter Platform 把这些复杂步骤都搬进了一个 Web 页面。你只需要上传模型和量化图片数据集，再选择目标设备、YOLO 版本和输入分辨率，剩下的模型导出、节点处理、量化转换、MUD 文件生成和结果打包，就交给平台自动完成。

不用记复杂命令，也不用反复进出 Docker。点一点、等一等，就可以拿到能够部署到 MaixCAM、MaixCAM Pro 或 MaixCAM2 的 YOLO Detect 模型文件。

## 当前支持

目前平台支持的设备和模型如下：

| 项目 | 支持范围 |
| --- | --- |
| 目标设备 | MaixCAM、MaixCAM Pro、MaixCAM2 |
| 模型类型 | YOLO26、YOLO11、YOLOv8 |
| 任务类型 | 目标检测（Detect） |
| 输入模型 | `.pt`、`.onnx` |
| 量化数据集 | 包含图片的 `.zip` 文件 |

> 当前暂不支持分类、分割、姿态检测和 OBB 等任务。其他模型或者需要自定义转换参数时，请使用前面介绍的手动转换方法。

## 获取转换平台

Maix Converter Platform 是一个开源工具，源代码在 [github.com/sipeed/maix_converter_platform](https://github.com/sipeed/maix_converter_platform)。

使用 Git 下载源代码：

```shell
git clone https://github.com/sipeed/maix_converter_platform.git
cd maix_converter_platform
```

## 准备 Python 环境

建议使用 Conda 创建一个独立的 Python 3.11 环境，避免与电脑中已有的软件包产生冲突：

```shell
conda create -n maix-converter python=3.11 -y
conda activate maix-converter
pip install -r requirements-web.txt
```

如果需要上传 `.pt` 模型并让平台自动导出 ONNX，还需要安装 Ultralytics 和 ONNX：

```shell
pip install ultralytics onnx
```

如果只上传已经导出的 `.onnx` 模型，可以不安装 `ultralytics`。对于自己训练的模型，仍然建议安装 `onnx`，平台可以尝试从模型信息中读取类别名称并写入 MUD 文件。

## 准备 Docker 环境

模型转换工具链运行在 Docker 中。请先安装 Docker，并确认当前用户可以正常运行：

```shell
docker --version
docker ps
```

如果 `docker ps` 没有出现权限错误，说明 Docker 已经可以使用。

> 不同设备使用不同的转换工具链。如果只需要转换一种设备的模型，只准备对应的 Docker 镜像即可。

### MaixCAM2 转换镜像

MaixCAM2 使用 Pulsar2 工具链，平台默认使用的镜像名称是 `pulsar2:6.0`。Pulsar2 镜像的下载和导入方法请参考[将 ONNX 模型转换为 MaixCAM2 模型](./maixcam2.md)。

下载镜像包后使用下面的命令导入：

```shell
docker load -i pulsar2_vxx.tar.gz
docker images
```

如果导入后的镜像名称不是 `pulsar2:6.0`，需要根据实际名称添加一个标签，例如：

```shell
docker tag pulsar2:3.3 pulsar2:6.0
```

最后检查 Pulsar2 是否可以正常运行：

```shell
docker run --rm pulsar2:6.0 -c "pulsar2 version"
```

### MaixCAM / MaixCAM Pro 转换镜像

MaixCAM 和 MaixCAM Pro 使用 TPU-MLIR 工具链。平台最终使用的镜像名称是 `maixcam-tpumlir:v3.4`。首先需要获取 `sophgo/tpuc_dev` 基础镜像，镜像的下载方法可以参考[将 ONNX 模型转换为 MaixCAM 模型](./maixcam.md)。

下载镜像包后使用下面的命令导入，并查看实际的镜像名称：

```shell
docker load -i tpuc_dev_vxx.tar.gz
docker images
```

转换平台提供的 Dockerfile 默认使用 `sophgo/tpuc_dev:v3.4`。如果导入后的镜像名称已经是这个名称，就不需要修改；如果名称或标签不同，再根据 `docker images` 中显示的实际名称添加标签。例如导入后显示为 `sophgo/tpuc_dev:latest`，执行：

```shell
docker tag sophgo/tpuc_dev:latest sophgo/tpuc_dev:v3.4
```

确认基础镜像名称正确后，在转换平台根目录构建平台使用的镜像：

```shell
docker build -f docker/maixcam-tpumlir.Dockerfile -t maixcam-tpumlir:v3.4 .
```

构建完成后再次查看镜像，并验证转换命令：

```shell
docker images
docker run --rm maixcam-tpumlir:v3.4 model_transform.py --help
```

看到 `model_transform.py` 的帮助信息，就说明转换环境准备完成了。

## 启动转换平台

进入项目根目录并激活前面创建的 Conda 环境：

```shell
cd maix_converter_platform
conda activate maix-converter
```

启动 Web 服务：

```shell
uvicorn web.app:app --host 0.0.0.0 --port 8000
```

在浏览器中访问：

```text
http://127.0.0.1:8000
```

如果在另一台电脑上访问这台转换服务器，请将 `127.0.0.1` 替换为服务器的 IP 地址。

## 准备模型和量化数据集

模型文件支持 `.pt` 和 `.onnx` 两种格式：

- 上传 `.pt` 时，平台会使用页面中填写的宽度和高度，通过 Ultralytics 自动导出对应输入分辨率的 ONNX。
- 上传 `.onnx` 时，平台会直接进行后续处理和转换，并使用模型自身的静态输入尺寸，不会根据页面中填写的宽度和高度重新调整模型尺寸。建议填写与 ONNX 模型实际输入尺寸相同的值。

量化数据集需要打包为 `.zip` 文件，压缩包中只需要图片，不需要标注文件。支持 `.jpg`、`.jpeg`、`.png` 和 `.bmp` 格式。

压缩包中可以直接放置图片：

```text
dataset.zip
  000001.jpg
  000002.jpg
  000003.jpg
```

也可以包含多层目录：

```text
dataset.zip
  images/
    000001.jpg
    000002.jpg
```

量化图片应该尽量接近模型部署后的真实使用场景。例如模型将用于摄像头拍摄，就优先使用同类摄像头在实际环境中采集的图片。快速测试可以先准备 50～100 张，正式转换时可以根据数据集情况适当增加。

## 创建转换任务

打开网页后，按照页面从上到下填写转换参数：

| 参数 | 说明 |
| --- | --- |
| 模型文件 | 上传需要转换的 `.pt` 或 `.onnx` 模型 |
| 量化数据集 | 上传只包含量化图片的 `.zip` 文件 |
| 模型名称 | 转换后文件的基础名称，例如 `yolo11n` |
| 目标设备 | 根据实际设备选择 MaixCAM2 或 MaixCAM / Pro |
| YOLO 版本 | 必须与上传模型的实际版本一致 |
| 图片数量 | 参与量化的图片数量，不能超过压缩包中的实际图片数量 |
| 宽度、高度 | 上传 `.pt` 时用于设置导出的模型输入分辨率；上传 `.onnx` 时以模型自身的静态输入尺寸为准。当前平台要求填写的宽和高在 32～4096 之间，并且都是 32 的倍数 |
| 快速模式 | 跳过部分检查以缩短转换时间，适合先验证流程 |

填写完成后点击“开始转换”。页面会显示文件上传进度、当前任务状态和实时转换日志。转换时间与模型大小、量化图片数量以及电脑性能有关，请耐心等待。

> 快速模式适合调试环境和验证流程。准备正式部署的模型时，建议关闭快速模式并重新完整转换一次。

## 下载转换结果

转换成功后，页面中的“下载结果”按钮会变为可用状态。点击按钮可以下载打包好的 ZIP 文件。

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

将 ZIP 解压后，把其中的所有模型文件复制到设备的同一个目录。MaixPy 程序只需要加载 `.mud` 文件，MUD 文件会自动引用同目录中的实际模型文件。

下面以 YOLO11 为例：

```python
from maix import app, camera, display, image, nn

detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)
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

如果转换的是 YOLO26 或 YOLOv8，请将示例中的 `nn.YOLO11` 换成对应的 MaixPy 模型接口。

## 查看任务和日志

每次转换都会在项目的 `jobs/` 目录中创建一个独立任务目录：

```text
jobs/<job_id>/
```

网页会显示最近的转换任务，并提供状态、日志、结果下载和任务删除功能。转换失败时，可以先查看网页中的实时日志，也可以打开任务目录中的以下文件排查：

```text
api.log
convert.log
job.json
```

其中 `convert.log` 记录了模型工具链的主要输出，通常最适合用来定位模型节点、量化数据集、Docker 镜像或转换参数问题。

## 常见问题

### Docker 没有权限

如果 `docker ps` 提示权限不足，Linux 用户可以将当前用户加入 Docker 用户组：

```shell
sudo usermod -aG docker $USER
```

执行后需要重新登录系统，再运行 `docker ps` 检查。

### 找不到 Docker 镜像

如果日志中出现 `Unable to find image`，使用下面的命令检查镜像名称：

```shell
docker images
```

MaixCAM2 需要 `pulsar2:6.0`，MaixCAM / MaixCAM Pro 需要 `maixcam-tpumlir:v3.4`。镜像名称或标签不同也会导致平台找不到转换环境。

### 量化图片数量不足

页面中的“图片数量”不能大于 ZIP 文件中实际包含的有效图片数量。如果只准备了 50 张图片，就不要将图片数量设置为 100。

### 自训练模型的类别不正确

平台会尝试从 `.pt` 或 ONNX metadata 中读取类别名称。如果模型运行后类别数量或名称不正确，请检查生成的 `.mud` 文件中 `labels` 的内容是否与训练模型一致。

### Windows 下转换时挂载目录失败

Windows 用户需要确保 Docker Desktop 已经启动，并启用 WSL2 backend。建议把项目放在纯英文且层级较浅的目录中，例如 `C:\maix_converter_platform`，避免中文、特殊字符或过长路径影响 Docker 目录挂载。

## 项目源代码

如果遇到问题、发现错误或者希望支持更多模型，可以在项目仓库提交 Issue：

[github.com/sipeed/maix_converter_platform](https://github.com/sipeed/maix_converter_platform)
