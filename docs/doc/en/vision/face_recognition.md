---
title: MaixPy Face Recognition
---

## Introduction to Face Recognition

Face recognition is the process of identifying the location of faces in the current image and determining who they are.
In addition to detecting faces, face recognition generally involves a database of known and unknown individuals.

## Recognition Principle

* Use an AI model to detect faces and obtain the coordinates and coordinates of facial features.
* Use the coordinates of facial features to perform affine transformation on the face in the image, aligning it to a standard face shape, making it easier for the model to extract facial features.
* Use a feature extraction model to extract facial feature values.
* Compare the extracted feature values with the recorded facial feature values in the database (calculate the cosine distance between the saved and current facial feature values, and find the smallest distance match in the database. If the distance is smaller than a set threshold, it is considered to be the same person in the database.)

## Using MaixPy

The MaixPy `maix.nn` module provides an API for face recognition, which can be used directly, and the model is also built-in. You can also download it from the [MaixHub Model Zoo](https://maixhub.com/model/zoo) (filter for the corresponding hardware platform, such as maixcam).

Recognition:

```python
from maix import nn

recognizer = nn.Face_Recognizer(model="/root/models/face_recognizer.mud")
if os.path.exists("/root/faces.bin"):
    recognizer.load_faces("/root/faces.bin")
cam = camera.Camera(recognizer.input_width(), recognizer.input_height(), recognizer.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    faces = recognizer.recognize(img)
    for obj in faces:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{recognizer.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

When running this code for the first time, you will find that it can detect faces, but it doesn't recognize anyone. We need to enter the add face mode to learn faces first.
For example, we can learn faces when the user presses a button:

```python
faces = recognizer.detect_faces(img)
for face in faces:
    print(face)
    # Here we consider the case where there are multiple faces in one image
    # You can decide whether to add the face to the database based on the coordinates of `face`
    recognizer.add_face(face)
recognizer.save_(faces)("/too/faces.bin")
```
