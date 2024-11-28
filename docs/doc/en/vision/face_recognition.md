---
title: MaixCAM MaixPy Face Recognition
---

## Introduction to Face Recognition

![face_recognize](../../assets/face_recognize.jpg)

Face recognition involves identifying the location of faces in the current view and who they are.
Thus, in addition to detecting faces, face recognition typically involves a database to store known and unknown individuals.

## Recognition Principles

* Use AI models to detect faces, obtaining coordinates and features of facial components.
* Use the coordinates of these features for affine transformation to align the face in the image to a standard face orientation, facilitating the extraction of facial features by the model.
* Employ a feature extraction model to derive facial feature values.
* Compare these features with those stored in the database (by calculating the cosine distance between the saved and the current facial features, identifying the face in the database with the smallest distance; if it's below a predefined threshold, it is recognized as the person in the database).

## Using MaixPy

MaixPy's `maix.nn` module provides a face recognition API, ready to use with built-in models. Additional models can also be downloaded from the [MaixHub model repository](https://maixhub.com/model/zoo) (select the appropriate hardware platform, such as maixcam).

Recognition:

```python
from maix import nn, camera, display, image
import os
import math

recognizer = nn.FaceRecognizer(detect_model="/root/models/yolov8n_face.mud", feature_model = "/root/models/insghtface_webface_r50.mud", dual_buff=True)
# recognizer = nn.FaceRecognizer(detect_model="/root/models/retinaface.mud", feature_model = "/root/models/face_feature.mud", dual_buff=True)

if os.path.exists("/root/faces.bin"):
    recognizer.load_faces("/root/faces.bin")
cam = camera.Camera(recognizer.input_width(), recognizer.input_height(), recognizer.input_format())
disp = display.Display()

while 1:
    img = cam.read()
    faces = recognizer.recognize(img, 0.5, 0.45, 0.85)
    for obj in faces:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        radius = math.ceil(obj.w / 10)
        img.draw_keypoints(obj.points, image.COLOR_RED, size = radius if radius < 5 else 4)
        msg = f'{recognizer.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
```

When you first run this code, it can detect faces but will not recognize them. We need to enter a mode to learn faces.

> Here `recognizer.labels[0]` is by default `unknown`, and every new face added will automatically append to `labels`.

For example, you can learn faces when a user presses a button:
```python
faces = recognizer.recognize(img, 0.5, 0.45, 0.85, True)
for face in faces:
    print(face)
    # This accounts for the scenario where multiple faces are present in one scene; obj.class_id of 0 means the face is not registered
    # Write your own logic here
    #   For instance, based on face’s class_id and coordinates, you can decide whether to add it to the database and facilitate user interaction, like pressing a button to register
    recognizer.add_face(face, label) # label is the name you assign to the face
recognizer.save_faces("/root/faces.bin")
```

Here, `0.5` is the threshold for face detection, where a higher value indicates stricter detection. `0.45` is the `IOU` threshold, used to filter overlapping face results. `0.85` is the threshold for face comparison, indicating similarity with stored faces in the database. If a face comparison score exceeds this threshold, it is considered a match. A higher threshold improves filtering accuracy, while a lower threshold increases the risk of misidentification and can be adjusted according to practical needs.

The detection model here supports three types: `yolov8n_face`, `retinaface`, and `face_detector`, each differing slightly in speed and accuracy, allowing for selection based on specific requirements.

## Complete Example

A complete example is provided for recording unknown faces and recognizing faces with a button press. This can be found in the [MaixPy example directory](https://github.com/sipeed/MaixPy/tree/main/examples) under `nn_face_recognize.py`.

## dual_buff Dual Buffer Acceleration

You may have noticed that the model initialization uses `dual_buff` (which defaults to `True`). Enabling the `dual_buff` parameter can improve running efficiency and increase the frame rate. For detailed principles and usage notes, see [dual_buff Introduction](./dual_buff.md).


## Replacing Other Default Recognition Models

The recognition model (for distinguishing different individuals) uses `mobilenetv2` and the [insight face resnet50](https://maixhub.com/model/zoo/462) model. If these do not meet accuracy requirements, other models can be substituted. You may need to train a new model or find a pre-trained model compatible with MaixCAM, such as other models from [insightface](https://github.com/deepinsight/insightface). For conversion instructions, refer to the [MaixCAM model conversion documentation](../ai_model_converter/maixcam.md), and follow existing `.mud` files as examples.


