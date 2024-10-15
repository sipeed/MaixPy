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

recognizer = nn.FaceRecognizer(detect_model="/root/models/retinaface.mud", feature_model = "/root/models/face_feature.mud", dual_buff = True)
if os.path.exists("/root/faces.bin"):
    recognizer.load_faces("/root/faces.bin")
cam = camera.Camera(recognizer.input_width(), recognizer.input_height(), recognizer.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    faces = recognizer.recognize(img, 0.5, 0.45, 0.8)
    for obj in faces:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        radius = math.ceil(obj.w / 10)
        img.draw_keypoints(obj.points, image.COLOR_RED, size = radius if radius < 5 else 4)
        msg = f'{recognizer.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

When you first run this code, it can detect faces but will not recognize them. We need to enter a mode to learn faces.

> Here `recognizer.labels[0]` is by default `unknown`, and every new face added will automatically append to `labels`.

For example, you can learn faces when a user presses a button:
```python
faces = recognizer.recognize(img, 0.5, 0.45, True)
for face in faces:
    print(face)
    # This accounts for the scenario where multiple faces are present in one scene; obj.class_id of 0 means the face is not registered
    # Write your own logic here
    #   For instance, based on face’s class_id and coordinates, you can decide whether to add it to the database and facilitate user interaction, like pressing a button to register
    recognizer.add_face(face, label) # label is the name you assign to the face
recognizer.save_faces("/root/faces.bin")
```

## Complete Example

A complete example is provided for recording unknown faces and recognizing faces with a button press. This can be found in the [MaixPy example directory](https://github.com/sipeed/MaixPy/tree/main/examples) under `nn_face_recognize.py`.

## dual_buff Dual Buffer Acceleration

You may have noticed that the model initialization uses `dual_buff` (which defaults to `True`). Enabling the `dual_buff` parameter can improve running efficiency and increase the frame rate. For detailed principles and usage notes, see [dual_buff Introduction](./dual_buff.md).


## Replacing Other Default Recognition Models

The current recognition model (used to distinguish different individuals) is based on the MobileNetV2 model. If its accuracy does not meet your requirements, you can replace it with another model, such as the [Insight Face ResNet50](https://maixhub.com/model/zoo/462) model. Of course, you can also train your own model or find other pre-trained models and convert them into a format supported by MaixCAM. For the conversion method, refer to the [MaixCAM Model Conversion Documentation](../ai_model_converter/maixcam.md), and you can write the mud file based on existing examples.

