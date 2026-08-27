---
title: Convert a YOLO Model Online
---

A `.pt` or `.onnx` model made on a computer cannot run directly on MaixCAM. The MaixHub online converter creates the `.mud`, `.cvimodel`, or `.axmodel` files needed by the board, without installing a conversion environment on your computer.

## Check whether the model is supported

The website currently supports MaixCAM, MaixCAM Pro, and MaixCAM2 with these object-detection models:

- YOLO26
- YOLO11
- YOLOv8
- YOLOv5u

Object detection means finding objects and drawing boxes. Classification, pose, segmentation, oriented boxes, and old YOLOv5 are not supported by this route. Use one of the manual conversion links at the end for those models.

YOLOv5u is the newer YOLOv5 in the Ultralytics tool. It differs from models trained with the old `ultralytics/yolov5` repository. If the source is unclear, ask the model author which version it is.

## If you only have PT, export ONNX first

`.pt` is the training result. `.onnx` is the format accepted by the website. Skip this section if you already have an `.onnx` file.

> **Compatibility note for this route**
>
> For the YOLO detection models supported by this page, use `ultralytics==8.4.104` and keep `opset=17` and `dynamic=False` in the export command. Other models or conversion routes may have different requirements; follow their own documentation.

Install the export tools:

```shell
python -m pip install ultralytics==8.4.104 ultralytics-thop onnx onnxslim onnxruntime
```

Assume the trained file is named `best.pt`. For MaixCAM and MaixCAM Pro, run:

```shell
yolo export model=best.pt format=onnx imgsz=224,320 opset=17 simplify=True dynamic=False
```

For MaixCAM2, run:

```shell
yolo export model=best.pt format=onnx imgsz=240,320 opset=17 simplify=True dynamic=False
```

This creates `best.onnx` next to `best.pt`. The size order is **height,width**. `opset=17` selects the ONNX rule version, while `dynamic=False` fixes the input size. Keep the other settings unchanged as well.

## Prepare conversion images

Choose 20 to 100 pictures from the real environment where the model will run. For an apple model used on a table, include different tables, lighting, and apple positions.

These pictures only help the converter adapt the model to the board. They do not retrain the model, so they need no boxes or label files.

Put the pictures directly in a ZIP file:

```text
apple_images.zip
├── 001.jpg
├── 002.jpg
├── 003.png
└── ...
```

The ZIP file must be no larger than 100 MB and must contain 20 to 100 images.

The website receives both your model and images. If they contain private or confidential information, do not upload them; use manual local conversion instead.

## Create a conversion task

1. Open the [MaixHub toolbox](https://maixhub.com/toolbox) and enter the model converter.
2. Choose your board, YOLO version, and object detection.
3. Upload `best.onnx` and the image ZIP.
4. Check the labels. If the website does not read them automatically, enter them in the same order used for training.
5. Start conversion. Download the result after the page reports success.

The task may wait in a queue. Do not submit duplicate tasks while it is still running.

## Check and run the result

Unzip the download. A MaixCAM or MaixCAM Pro package should contain `.mud` and `.cvimodel`. A MaixCAM2 package should contain `.mud` and one or two `.axmodel` files.

Upload every file from the package, not only `.mud`. Then follow [Upload the model](./ai_model_deploy.md#upload-the-model) and [Run the model](./ai_model_deploy.md#run-the-model).

If the camera shows the correct labels and boxes, conversion and board testing are complete. You may [share it on MaixHub](./ai_model_deploy.md#optional-share-on-maixhub), but sharing is optional.

## If conversion fails

- **Fails immediately after upload:** confirm that the file is `.onnx`, the YOLO version is supported, and the model has a fixed input size.
- **Not enough images:** the number entered on the page cannot exceed the actual number of images in the ZIP.
- **Conversion succeeds but no boxes appear:** test the same `.onnx` on your computer first. If it also fails there, return to training or export.
- **Files cannot be uploaded to an external service:** use manual local conversion.

For unsupported models, see [manual conversion for MaixCAM2](./maixcam2.md), [manual conversion for MaixCAM](./maixcam.md), or [port an unsupported model](../pro/customize_model.md). These advanced routes require dedicated conversion tools and knowledge of model inputs and outputs.
