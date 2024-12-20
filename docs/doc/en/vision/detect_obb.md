---
tite: Target Detection with Rotation Angles (OBB, Oriented Bounding Box)
update:
    - date: 2024-12-20
      version: v1.0
      author: neucrack
      content:
        Support YOLO11/YOLOv8 OBB model and add documentation
---

## Introduction

In standard object detection, the output is typically a rectangular bounding box. However, in certain scenarios, objects may have a rotated shape, requiring a bounding box with a rotation angle. This type of bounding box is referred to as an OBB (Oriented Bounding Box).  
![](../../assets/ships-detection-using-obb.jpeg)

**Standard detection results:** `x, y, w, h` represent the top-left or center coordinates of the rectangle, along with its width and height.  
**OBB detection results:** `x, y, w, h, angle` includes an additional parameter for the rotation angle.

## Using Rotated Bounding Boxes (OBB) in MaixPy MaixCAM

`MaixPy` supports the `YOLO11/YOLOv8` OBB model, enabling quick and convenient implementation. Below is an example based on the `nn_yolo11_obb.py` script from [MaixPy/examples](https://github.com/sipeed/maixpy):

```python
from maix import camera, display, image, nn, app

detector = nn.YOLO11(model="/root/models/yolo11n_obb.mud", dual_buff=True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
    for obj in objs:
        points = obj.get_obb_points()
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}, {obj.angle * 180:.1f}'
        img.draw_string(points[0], points[1] - 4, msg, color=image.COLOR_RED)
        detector.draw_pose(img, points, 8 if detector.input_width() > 480 else 4, image.COLOR_RED, close=True)
    disp.show(img)
```

In this example, the `YOLO11` model is used to load an OBB model. After detecting an object, the rotation angle can be accessed via `obj.angle`. The `x, y, w, h` attributes of `obj` represent the unrotated rectangle. The `get_obb_points` method retrieves the four vertices of the rotated rectangle, and `draw_pose` is used to draw the rotated bounding box. The `close` parameter ensures the vertices are connected.

The default model is the official YOLO11 15-class model with the following labels:

```python
plane, ship, storage tank, baseball diamond, tennis court, basketball court, ground track field, harbor, bridge, large vehicle, small vehicle, helicopter, roundabout, soccer ball field, swimming pool
```

The model file can be found at `/root/models/yolo11n_obb.mud`.

## More Input Resolutions

The default input image resolution is `320x224`. For higher resolutions, download from the [MaixHub Model Zoo](https://maixhub.com/model/zoo/869) or customize your own model as described below.

## Customizing Your Own OBB Model for MaixPy MaixCAM

### Using the Model on a Computer

For an introduction to the official `YOLO11` OBB models, refer to [YOLO11 OBB](https://docs.ultralytics.com/tasks/obb/). This documentation explains how to use OBB models on a computer and export ONNX model files.

### Exporting the Model for MaixCAM

Follow the [YOLO11/YOLOv8 Custom Models](./customize_model_yolov8.md) guide to convert an ONNX model into a MUD model compatible with MaixCAM.  
**Note:** Ensure the output names of the model's layers are correctly configured during conversion.

### Training Your Own OBB Model

Refer to the [YOLO11 Official Training Documentation](https://docs.ultralytics.com/datasets/obb/dota-v2/) to prepare your dataset and train your own OBB model.

