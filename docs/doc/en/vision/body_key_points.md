---
title: MaixCAM MaixPy Human Pose Keypoint Detection
---

## Introduction

Using MaixPy, you can easily detect the coordinates of keypoints on human joints, which can be used for posture detection, such as monitoring sitting posture or providing input for motion-based games.

MaixPy implements human pose detection based on [YOLOv8-Pose / YOLO11-Pose](https://github.com/ultralytics/ultralytics), capable of detecting `17` keypoints on the human body.

![](../../assets/body_keypoints.jpg)

## Usage

You can easily implement this using the `maix.nn.YOLOv8` or `maix.nn.YOLO11` classes in MaixPy:

```python
from maix import camera, display, image, nn, app

detector = nn.YOLO11(model="/root/models/yolo11n_pose.mud", dual_buff=True)
# detector = nn.YOLOv8(model="/root/models/yolov8n_pose.mud", dual_buff=True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45, keypoint_th=0.5)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
        detector.draw_pose(img, obj.points, 8 if detector.input_width() > 480 else 4, image.COLOR_RED)
    disp.show(img)
```

You can also find the code in the [MaixPy/examples/vision](https://github.com/sipeed/MaixPy/tree/main/examples/vision/ai_vision) directory.

Since `YOLOv8-Pose` is used here, the `YOLOv8` class is also used, with the only difference being the model file compared to `YOLOv8` object detection. The same applies to `YOLO11`. The `detect` function returns an additional `points` value, which is a list of `int` containing `17` keypoints. The points are arranged in order; for example, the first value is the x-coordinate of the nose, the second value is the y-coordinate of the nose, and so on:

```python
1. Nose
2. Left Eye
3. Right Eye
4. Left Ear
5. Right Ear
6. Left Shoulder
7. Right Shoulder
8. Left Elbow
9. Right Elbow
10. Left Wrist
11. Right Wrist
12. Left Hip
13. Right Hip
14. Left Knee
15. Right Knee
16. Left Ankle
17. Right Ankle
```

If any of these parts are occluded, the value will be `-1`.

## Models with More Resolutions

The default model input resolution is `320x224`. If you want to use models with higher resolution, you can download and transfer them from the MaixHub model library:
* YOLOv8-Pose: [https://maixhub.com/model/zoo/401](https://maixhub.com/model/zoo/401)
* YOLO11-Pose: [https://maixhub.com/model/zoo/454](https://maixhub.com/model/zoo/454)

Higher resolution generally provides better accuracy but at the cost of lower processing speed. Choose the model based on your application needs. If the provided resolution does not meet your requirements, you can train your own model using the source code from [YOLOv8-Pose / YOLO11-Pose](https://github.com/ultralytics/ultralytics) and export your own ONNX model, then convert it to a format supported by MaixCAM (methods are covered in later articles).

## dual_buff for Double Buffering Acceleration

You may notice that `dual_buff` is used for model initialization (default value is `True`). Enabling the `dual_buff` parameter can improve efficiency and increase the frame rate. For more details and considerations, refer to the [dual_buff Introduction](./dual_buff.md).
