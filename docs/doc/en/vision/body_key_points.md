# Title: MaixPy Human Keypoint Pose Detection

## Introduction

With MaixPy, you can easily detect the coordinates of keypoints on human joints, useful for applications like posture detection, such as sitting posture analysis, or input for motion-sensing games.

MaixPy implements human pose detection based on [YOLOv8-Pose](https://github.com/ultralytics/ultralytics), which can detect `17` keypoints on the human body.

## Usage

Using MaixPy's `maix.nn.YOLOv8` class, you can easily implement this functionality:

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv8(model="/root/models/yolov8n_pose.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
dis = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
        detector.draw_pose(img, obj.points, 8 if detector.input_width() > 480 else 4, image.COLOR_RED)
    dis.show(img)
```

And you can also find code in [MaixPy/examples/vision](https://github.com/sipeed/MaixPy/tree/main/examples/vision/ai_vision) directory.

As you can see, by using `YOLOv8-Pose`, we directly utilize the `YOLOv8` class. The only difference from the `YOLOv8` object detection model is the model file, and the `detect` function returns an additional `points` value, which is a list of `17` integer coordinates arranged in sequence. For example, the first value is the x-coordinate of the nose, the second value is the y-coordinate of the nose, and so on, in the following order:

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

If certain parts are occluded, the corresponding values will be `-1`.

## Higher Input Resolution Models

The default model input resolution is `320x224`. If you wish to use a model with a higher resolution, you can download it from the [MaixHub Model Library](https://maixhub.com/model/zoo/401) and transfer it to your device.

Higher resolutions theoretically offer better accuracy but come with a decrease in processing speed. Choose the resolution based on your use case. Additionally, if the provided resolutions do not meet your requirements, you can train your own model using the [YOLOv8-Pose](https://github.com/ultralytics/ultralytics) source code to export your own ONNX model, which can then be converted to a model supported by MaixCAM (method detailed in subsequent articles).


