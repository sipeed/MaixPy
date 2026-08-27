---
title: Train a YOLO Detection Model on a Computer
---

This guide continues with the apple example. You will train YOLO11 on a computer, get `best.pt`, and export `best.onnx` for the board converter.

For the easiest first project, use [online training on MaixHub](./maixhub_train.md). Computer training requires Python, but it keeps your data on your computer and gives you control over training.

## Prepare the dataset first

Follow [Prepare a Model and Dataset](../pro/datasets.md) to arrange the pictures, labels, and `data.yaml`. The standard folder layout is explained there, so this page starts with installing the training tool.

## Install the training tool

YOLO is a family of object-detection models. This guide uses the training tool provided by Ultralytics.

Install Python 3 from the [Python website](https://www.python.org/downloads/); Python 3.11 is recommended. On Windows, select **Add Python to PATH** during installation so the terminal can find it.

Open PowerShell on Windows, or Terminal on macOS or Linux. Check Python:

```shell
python --version
```

If you see `Python 3...`, install the training tool. If `python` is not found, use `python3` in the commands instead.

```shell
python -m pip install ultralytics==8.4.104
```

Check the installation:

```shell
yolo checks
```

If the terminal prints the Python and environment information, training can start. If `yolo` is not found, close and reopen the terminal, then try again.

## Run 3 rounds to check the data

This command trains for only three rounds. Its purpose is to find bad paths, images, or labels quickly:

```shell
yolo detect train model=yolo11n.pt data=/full/path/to/apple_dataset/data.yaml epochs=3 imgsz=640 project=runs/apple name=check exist_ok=True
```

`yolo11n.pt` is a small starter model. `epochs=3` means the tool reads the training set three times. `imgsz=640` means it processes the pictures at 640 pixels for training. Keep these values for the first check.

If the command finishes and creates `runs/apple/check`, the dataset format is usable. The first run downloads `yolo11n.pt`, so the computer must be online.

## Train the model

Now train for 100 rounds:

```shell
yolo detect train model=yolo11n.pt data=/full/path/to/apple_dataset/data.yaml epochs=100 imgsz=640 project=runs/apple name=model exist_ok=True
```

When training ends, use:

```text
runs/apple/model/weights/best.pt
```

`best.pt` comes from the round with the best validation result, which may not be the final round.

## Test with a new picture

Choose an apple picture that was not used for training:

```shell
yolo detect predict model=runs/apple/model/weights/best.pt source=/path/to/test.jpg save=True
```

The terminal prints where it saved the result. Open that image and check the label and box.

If training pictures work but new ones do not, add pictures with different apples, backgrounds, and lighting. More training rounds usually cannot replace missing variety.

## Export ONNX

The board converter cannot use `.pt` directly, so export it as `.onnx`.

> **Compatibility note for this example**
>
> This YOLO11 route uses `ultralytics==8.4.104`. Keep `opset=17` and `dynamic=False` in the commands below. Other models or conversion routes may require different versions and settings; follow their own documentation instead of copying these values.

For MaixCAM and MaixCAM Pro, a common size is `320x224`:

```shell
yolo export model=runs/apple/model/weights/best.pt format=onnx imgsz=224,320 opset=17 simplify=True dynamic=False
```

For MaixCAM2, start with `320x240`:

```shell
yolo export model=runs/apple/model/weights/best.pt format=onnx imgsz=240,320 opset=17 simplify=True dynamic=False
```

For smaller objects, MaixCAM2 can use `640x480`, but it runs more slowly:

```shell
yolo export model=runs/apple/model/weights/best.pt format=onnx imgsz=480,640 opset=17 simplify=True dynamic=False
```

The size order in these commands is **height,width**. A successful export creates `best.onnx` next to `best.pt`.

`opset` is the ONNX rule version; keep it at `17` for this route. `dynamic=False` fixes the input size, and `simplify=True` simplifies the model structure. Keep all three settings.

## Convert and run on the board

1. Use [Convert a YOLO Model Online](../ai_model_converter/online_converter.md) to convert `best.onnx` into a board model package.
2. Follow [Upload the model](../ai_model_converter/ai_model_deploy.md#upload-the-model) and test it.

When the camera image shows the correct label and box, training, conversion, and board deployment are complete. You may then [share it on MaixHub](../ai_model_converter/ai_model_deploy.md#optional-share-on-maixhub), but sharing is not required.

## Other YOLO versions

To try YOLO26 or YOLOv8, replace the starter model with `yolo26n.pt` or `yolov8n.pt`. Check the documentation for that model before reusing version or export settings.

The old YOLOv5 from the `ultralytics/yolov5` repository is different from the newer YOLOv5u and cannot use this simple web-conversion route. For an old project, use [manual conversion for MaixCAM](../ai_model_converter/maixcam.md) or [MaixCAM2](../ai_model_converter/maixcam2.md). YOLO11 is recommended for a new project.

Pose, segmentation, and oriented boxes use different annotation formats and are not supported by this online conversion route. See [Body Keypoints](./body_key_points.md), [Semantic Segmentation](./segmentation.md), or [Oriented Bounding Boxes](./detect_obb.md).
