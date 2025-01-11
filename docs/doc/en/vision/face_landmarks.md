---
title: MaixCAM MaixPy Face 478 Keypoints Detection
update:
  - date: 2025-01-08
    version: v1.0
    author: neucrack
    content: Add face 478 landmarks detection source code, documentation and demo.
---

## Introduction

In the previous article [Face Detection](./face_detection.md), we introduced how to detect faces and a few keypoints (e.g., 5 keypoints). This article explains how to detect more keypoints.

More keypoints have a wide range of applications, such as expression detection, facial feature recognition, face swapping, and more.

![face_landmarks](../../assets/face_landmarks.jpg)

<a href="../../assets/maixcam_face_landmarks_full.jpg" target="_blank">full size 478 landmarks image</a>

## Using Face Keypoints Detection in MaixPy

MaixPy integrates MediaPipe's **478 face keypoints** detection, with the results as shown below:

![maixcam_face_landmarks](../../assets/maixcam_face_landmarks_1.jpg)

Video demonstration:
<video playsinline controls autoplay loop muted preload src="/static/video/maixcam_face_landmarks.mp4" type="video/mp4">
Classifier Result video
</video>

### Code Usage

To use this feature, MaixPy version must be >= 4.10.0. Refer to the latest code in [MaixPy/examples](https://github.com/sipeed/MaixPy):

```python
from maix import camera, display, image, nn, app

detect_conf_th = 0.5
detect_iou_th = 0.45
landmarks_conf_th = 0.5
landmarks_abs = True
landmarks_rel = False
max_face_num = 2
detector = nn.YOLOv8(model="/root/models/yolov8n_face.mud", dual_buff=False)
landmarks_detector = nn.FaceLandmarks(model="/root/models/face_landmarks.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    results = []
    objs = detector.detect(img, conf_th=detect_conf_th, iou_th=detect_iou_th, sort=1)
    count = 0
    for obj in objs:
        img_std = landmarks_detector.crop_image(img, obj.x, obj.y, obj.w, obj.h, obj.points)
        if img_std:
            res = landmarks_detector.detect(img_std, landmarks_conf_th, landmarks_abs, landmarks_rel)
            if res and res.valid:
                results.append(res)
        count += 1
        if count >= max_face_num:
            break
    for res in results:
        landmarks_detector.draw_face(img, res.points, landmarks_detector.landmarks_num, res.points_z)
    disp.show(img)
```

### Explanation of Key Points

- `max_face_num`: Limits the maximum number of faces detected to prevent lag due to too many faces in the frame.
- `landmarks_abs`: Specifies the coordinates of face keypoints in the original `img`. The `points` variable contains 478 keypoints in the order `x0, y0, x1, y1, ..., x477, y477`.
- `landmarks_rel`: Outputs coordinates in `img_std` and appends the results to the `points` variable.
- `points_z`: Represents depth estimation of the keypoints relative to the face's center of gravity. The closer to the camera, the larger the value. If behind the face's center, the value is negative. The values are proportional to the face's width.

## Extracting Partial Keypoints

The 478 keypoints may be excessive for some applications. If you only need specific ones, you can select them based on the <a href="../../assets/maixcam_face_landmarks_full.jpg" target="_blank">high-resolution image</a> index. Common subsets include:
**Note: These are for reference only. Please rely on the actual model output for accuracy.**

* **146 Keypoints:**
```python
sub_146_idxes = [0, 1, 4, 5, 6, 7, 8, 10, 13, 14, 17, 21, 33, 37, 39, 40, 46, 52, 53, 54, 55, 58, 61, 63, 65, 66, 67, 70, 78, 80,
                 81, 82, 84, 87, 88, 91, 93, 95, 103, 105, 107, 109, 127, 132, 133, 136, 144, 145, 146, 148, 149, 150, 152, 153, 
                 154, 155, 157, 158, 159, 160, 161, 162, 163, 168, 172, 173, 176, 178, 181, 185, 191, 195, 197, 234, 246, 249, 
                 251, 263, 267, 269, 270, 276, 282, 283, 284, 285, 288, 291, 293, 295, 296, 297, 300, 308, 310, 311, 312, 314, 
                 317, 318, 321, 323, 324, 332, 334, 336, 338, 356, 361, 362, 365, 373, 374, 375, 377, 378, 379, 380, 381, 382, 
                 384, 385, 386, 387, 388, 389, 390, 397, 398, 400, 402, 405, 409, 415, 454, 466, 468, 469, 470, 471, 472, 473, 
                 474, 475, 476, 477]
```

* **68 Keypoints:**
```python
sub_68_idxes = [162, 234, 93, 58, 172, 136, 149, 148, 152, 377, 378, 365, 397, 288, 323, 454, 389, 71, 63, 105, 66, 107, 336,
                296, 334, 293, 301, 168, 197, 5, 4, 75, 97, 2, 326, 305, 33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373,
                380, 61, 39, 37, 0, 267, 269, 291, 405, 314, 17, 84, 181, 78, 82, 13, 312, 308, 317, 14, 87]
```

* **5 Keypoints:**
```python
sub_5_idxes = [468, 473, 4, 61, 291]
```

With these indices, you can use the following code to extract and display specific subsets of keypoints:

```python
def get_sub_landmarks(points, points_z, idxes):
    new_points = []
    new_points_z = []
    for i in idxes:
        new_points.append(points[i * 2])
        new_points.append(points[i * 2 + 1])
        new_points_z.append(points_z[i])
    return new_points, new_points_z

sub_xy, sub_z = get_sub_landmarks(res.points, res.points_z, sub_146_idxes)
landmarks_detector.draw_face(img, sub_xy, len(sub_z), sub_z)
```

