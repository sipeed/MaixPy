---
title: Using YOLO World Model on MaixPy MaixCAM2 for Detection of Any Target Without Training
---

## YOLO World Hardware Platform Support

| Hardware Platform | Supported |
| ----------------- | --------- |
| MaixCAM           | No        |
| MaixCAM2          | Yes       |

## Overview of YOLO Object Detection

YOLO is a well-known object detection model suitable for edge device deployment, capable of quickly detecting pre-trained targets. 

For example, if we want to detect the position of `apple` in an image, we need to collect image data of `apple`, train a model, and then export the model to perform detection in MaixPy.

In other words, for each new target to be detected, we need to retrain a model. This process is cumbersome, time-consuming, and most importantly, training cannot be done on the edge device itself; it must be done on a computer or server with a GPU.

## YOLO World Concept

YOLO World, however, eliminates the need for additional training. You simply need to tell the model what target you want to detect, and YOLO World will be able to detect it. Sounds magical, doesn't it?

YOLO World is a new concept, enabling detection of any target. YOLO World achieves this functionality through the use of `Prompt`. The model has incorporated language model capabilities, allowing you to specify the target you want to detect through text descriptions. 

For example, if we want to detect `apple`, we simply input `apple` along with the image to be detected, and the model can detect the coordinates of `apple` in the image.

I won’t go into more technical details here, but for those interested, please refer to the [YOLO World official repository](https://github.com/AILab-CVC/YOLO-World).

## Using YOLO World in MaixPy

### YOLO World Implementation in MaixPy

MaixPy has ported the official YOLO World model (YOLOv8/YOLO11) from [ultralytics](https://github.com/ultralytics/ultralytics/blob/main/docs/en/models/yolo-world.md) using the project [ONNX-YOLO-World-Open-Vocabulary-Object-Detection](https://github.com/AXERA-TECH/ONNX-YOLO-World-Open-Vocabulary-Object-Detection).

If you want to try it on a PC (**Note: this is not running on MaixCAM**), you can follow this documentation. For instance, you can:

First, specify the target categories you want to detect and save a model that can only detect those specific targets:
```python
from ultralytics import YOLO

model = YOLO("yolov8s-world.pt")  # or select yolov8m/l-world.pt
model.set_classes(["person", "bus"])
model.save("custom_yolov8s.pt")
```

Then use the new model to perform detection:
```python
from ultralytics import YOLO

model = YOLO("custom_yolov8s.pt")
results = model.predict("path/to/image.jpg")
results[0].show()
```

### Principle Overview

As seen above, we first specify the target categories for detection and obtain a new model, which is then used for detection.

The principle is as follows:
Due to the performance and power consumption limitations of edge computing hardware, the YOLO World model (the previously mentioned `yolov8s-world.pt`) is divided into two parts:
* **Language Model (text_feature model)**: This model encodes the language input (`Prompt`) into a text feature vector (which can be simply understood as an array) and stores it in a `.bin` file. This model is large and runs slowly.
* **Detection Model (yolo model)**: This model takes both the image and the feature vector (`.bin`) as input for object detection and outputs the coordinates and class names of the detected objects. This model is smaller and runs faster.

The reason for splitting into two parts is that during actual detection, we only need to run the detection model, avoiding the need to run the language model every time, thus saving runtime and power consumption. For example, if we want to detect `apple`, we only need to run the language model once (which occupies more resources) to encode `apple` into a feature vector (a very small file). Then, for each subsequent detection, we only need to run the detection model, combining the image and the feature vector for detection.

When we need to detect a new target, we can run the language model again to generate a new feature vector file.

Therefore, in the previous example, the model file `yolov8s-world.pt` used on the computer contains both the language model and the detection model. To make it more convenient for edge devices, we split it into two separate model files:
* `yolo-world_4_class.mud`: Detection model, fast and small.
* `yolo-world_text_feature_4_class.mud`: Language model, slow and large.

### Running the Language Model to Specify the Target for Detection

Run the language model once, specify the target to be detected, and generate the feature vector file:
```python
import os

labels = ["apple", "banana", "orange", "grape"]
out_dir = "/root/models"
name = "yolo-world_4_class_my_feature"

feature_file = os.path.join(out_dir, f"{name}.bin")
labels_file = os.path.join(out_dir, f"{name}.txt")
with open(labels_file, "w") as f:
    for label in labels:
        f.write(f"{label}\n")

cmd = f"python -u -m yolo_world_utils gen_text_feature --labels_path {labels_file} --out_feature_path {feature_file}"

print(f"Now run\n\t`{cmd}`\nto generate text feature of\n{labels}")
print("\nplease wait a moment, it may take a few seconds ...\n")
ret = os.system(cmd)
if ret != 0:
    print("[ERROR] execute have error, please see log")
else:
    print(f"saved\n\tlabels to:\n\t{labels_file}\n and text feature to:\n\t{feature_file}")
    print(f"please use yolo-world_{len(labels)}_class.mud model to run detect")
```

Here, we specify four categories to detect by setting `labels`. Two necessary files (`*.bin` and `*.txt`) will be generated.
**Note**: The `labels` format requirements:
* Each category name must be in **English**. It cannot be in Chinese or any other language because the language model only supports English.
* Multiple words are allowed, but the length should not be too long. After BPE encoding, the length should not exceed 75 tokens. If it’s too long, an error will occur, so try it and you'll know.

### Running the Detection Model

We have generated the feature vector, and now we have three files:
1. Text feature vector `yolo-world_4_class_my_feature.bin`.
2. Label text file `yolo-world_4_class_my_feature.txt`.
3. One-category detection model `yolo-world_4_class.mud`, located in the `/root/models` directory.

> Note that this detection model is for `4_class`, meaning it can only detect four categories. The `.txt` file must contain exactly four categories, and they must correspond one by one. For instance, for a one-category model, you would use `yolo-world_1_class.mud`, and the `.txt` would contain only one category.

The system has built-in detection models for 1/4 categories in the `/root/models` directory, namely `yolo-world_1_class.mud` and `yolo-world_4_class.mud`. If you need to detect a different number of categories, download the corresponding model files as outlined in the section **Download More Detection Models with Different Categories**.

Now we can directly use the YOLO World model for real-time object detection. The code is similar to YOLOv8 and YOLO11:

```python
detector = nn.YOLOWorld("/root/models/yolo-world_4_class.mud",
                        "/root/models/yolo-world_4_class_my_feature.bin",
                        "/root/models/yolo-world_4_class_my_feature.txt",
                        dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
```

## Download More Detection Models with Different Categories

There are two ways:

### Download from MaixHub model zoo

Download from [MaixHub model zoo](), the supported class num please refer to MaixHub model zoo's description documentation.


### Generate by yourself


If you need models for other categories, you need to generate them yourself.

> If you don't have the environment or ability to do this, you can request help from other capable group members in QQ group 86234035 or [telegram](https://t.me/maixpy) for paid assistance.

A Docker image is provided, and you can pull the image to run locally to generate models for any number of categories.
* First, ensure you can successfully pull the image from Docker Hub, preferably with a proxy. Refer to [docker proxy setup](https://neucrack.com/p/286).
* You can test with `docker pull hello-world`.
* `docker pull sipeed/yolo-world-generator-maixcam2`

> The `sipeed/sipeed/yolo-world-generator-maixcam2` image relies on the `sipeed/pulsar2` image, which will be automatically downloaded. Alternatively, you can manually download the image from [Pulsar2 official site](https://pulsar2-docs.readthedocs.io/zh-cn/latest/user_guides_quick/quick_start_prepare.html), then load and rename it:
> * `docker load -i *.tar.gz`
> * `docker tag pulsar2:3.3 sipeed/pulsar2:latest`, change `3.3` based on the actual version.

* `docker run -it --rm -v ${PWD}/out:/root/out sipeed/yolo-world-generator-maixcam2 /bin/bash`
Here `-v ${PWD}/out:/root/out` maps the current directory's `out` folder to the container, so files generated inside the container can be viewed in the current directory (use multiple `-v src:dst` arguments for additional directories).

Now you can enter the Docker container and run the conversion command:
```shell
cd /root
./gen_model.sh 1 640 480
```
Here, the three parameters are:
* class_num: The number of categories.
* width: Input resolution width.
* height: Input resolution height.
* After completion, the model file will be available in the `out` directory, compressed. Simply extract and use it.

Model generation takes time, so be patient.

