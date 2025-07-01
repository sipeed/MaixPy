---
title: Offline Training of YOLOv5 Model for Custom Object Detection with MaixCAM MaixPy
update:
    - date: 2024-6-20
      version: v1.0
      author: neucrack
      content:
        Documentation written
    - date: 2025-7-01
      version: v2.0
      author: neucrack
      content:
        Add MaixCAM2 Support
---

## Introduction

The default official model provides detection for 80 types of objects. If this does not meet your needs, you can train your own detection objects using two methods:
* Use [MaixHub Online Training](./maixhub_train.md), which is convenient and fast, without needing to buy a server or set up an environment, just a few clicks of the mouse.
* Set up a training environment on your own computer or server.

The former is simple and quick, while the latter uses your own computer and the number of training images is not limited, but the latter is much more difficult.

**Note:** This article explains how to customize training, but some basic knowledge is assumed. If you do not have this knowledge, please learn it yourself:
* This article will not explain how to install the training environment. Please search and install it yourself (Pytorch environment installation) and test it.
* This article will not explain the basic concepts of machine learning or basic Linux usage knowledge.

If you think there is something in this article that needs improvement, feel free to click `Edit this article` in the upper right corner to contribute and submit a documentation PR.


## Process and Goals of this Article

To use our model on MaixPy (MaixCAM), the following process is required:
* Set up the training environment (this is not covered in this article, please search for Pytorch training environment setup).
* Pull the [yolov5](https://github.com/ultralytics/yolov5) source code to your local machine.
* Prepare the dataset and format it as required by the yolov5 project.
* Train the model to get an `onnx` model file, which is the final output file of this article.
* Convert the `onnx` model into a MaixPy-supported `MUD` file. This process is detailed in the model conversion articles:
  * [MaixCAM Model Conversion](../ai_model_converter/maixcam.md)
  * [MaixCAM2 Model Conversion](../ai_model_converter/maixcam2.md)
* Use MaixPy to load and run the model.


## Reference Articles

Since this is a relatively common operational process, this article only provides an overview. For specific details, you can refer to the **[YOLOv5 official code and documentation](https://github.com/ultralytics/yolov5)** (**recommended**), and search for training tutorials to ultimately export the onnx file.

Here are some articles from the MaixHub community:
* [Deploy yolov5s custom model on maixcam](https://maixhub.com/share/23)
* [【Process Sharing】YOLOv5 training custom dataset and deploying on Maixcam](https://maixhub.com/share/32)
* [YOLOv5 cat and dog recognition model—free cloud training (reproducible by beginners)](https://maixhub.com/share/25)

If you find any good articles, feel free to modify this article and submit a PR.

## Exporting YOLOv5 ONNX Model File

YOLOv5 provides an export option. Execute the following command in the `yolov5` directory:
```shell
python export.py --weights ../yolov5s.pt --include onnx --img 224 320
```
This command loads the `pt` parameter file and converts it to `onnx`, while also specifying the resolution. Note that the height comes first, followed by the width. The model was trained with `640x640`, but we re-specified the resolution to improve the running speed. The resolution `320x224` is used because it is closer to the MaixCAM screen ratio for better display. You can set it according to your needs.


## MaixCAM MUD File

When converting an ONNX model to the `mud` format model file, refer to [MaixCAM Model Conversion](../ai_model_converter/maixcam.md) and [MaixCAM2 Model Conversion](../ai_model_converter/maixcam2.md). In the end, you will get a `mud` file and a `cvimodel` file. The content of the `mud` file is as follows:

MaixCAM/MaixCAM-Pro:
```ini
[basic]
type = cvimodel
model = yolov5s_320x224_int8.cvimodel

[extra]
model_type = yolov5
input_type = rgb
mean = 0, 0, 0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
anchors = 10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush
```

MaixCAM2:
```ini
[basic]
type = axmodel
model_npu = yolov5s_640x480_npu.axmodel
model_vnpu = yolov5s_640x480_vnpu.axmodel

[extra]
model_type = yolov5
type=detector
input_type = rgb

input_cache = true
output_cache = true
input_cache_flush = false
output_cache_inval = true

anchors = 10,13, 16,30, 33,23, 30,61, 62,45, 59,119, 116,90, 156,198, 373,326
labels = person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush

mean = 0,0,0
scale = 0.00392156862745098, 0.00392156862745098, 0.00392156862745098
```

Replace the parameters according to the content of your training. For example, if you train to detect digits `0-9`, then just replace `labels=0,1,2,3,4,5,6,7,8,9`, and then place the two files in the same directory and load the `mud` file when running the model.


## Upload share on MaixHub

Share your model on [MaixHub model zoo](https://maixhub.com/model/zoo?platform=maixcam) 上传并分享你的模型，可以多提供几个分辨率供大家选择。



