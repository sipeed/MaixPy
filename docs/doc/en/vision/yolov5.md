---
title: Using YOLOv5 / YOLOv8 Model for Object Detection with MaixPy
---

## Concept of Object Detection

Object detection refers to identifying the position and category of targets in an image or video, such as detecting objects like apples and airplanes in a picture, and marking the position of these objects.

Unlike classification, object detection includes positional information, so the result is usually a rectangular box that frames the location of the object.

## Using Object Detection in MaixPy

MaixPy comes with the `YOLOv5` and `YOLOv8` model by default, which can be used directly:
> MaixPy need >= 4.3.0 to use YOLOv8.

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv5(model="/root/models/yolov5s.mud")
# detector = nn.YOLOv8(model="/root/models/yolov8n.mud")

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
dis = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    dis.show(img)
```

Demonstration video:

<video playsinline controls autoplay loop muted preload src="https://wiki.sipeed.com/maixpy/static/video/detector.mp4" type="video/mp4">

This setup uses a camera to capture images, which are then sent to the `detector` for detection. The results (classification name and position) are displayed on the screen.

And here Replace `YOLOv5` and `YOLOv8` to switch `v5/v8`. Note that the model file path also needs to be modified.

For a list of 80 objects supported by the model, please see the appendix of this article.

For more API usage, refer to the documentation of the [maix.nn](/api/maix/nn.html) module.

## More input resolutions

The default model input is `320x224` resolution, because this resolution ratio is close to the default screen resolution. You can also manually download models with other resolutions to replace:

YOLOv5s: https://maixhub.com/model/zoo/365
YOLOv8n: https://maixhub.com/model/zoo/400

The larger the resolution, the higher the accuracy, but the longer the running time. Just choose the appropriate one according to your application scenario.

## Can the camera resolution and model resolution be different?

When using the `detector.detect(img)` function for detection above, if the resolution of `img` is different from the model resolution, this function will automatically call `img.resize` to scale the image to the same resolution as the model input. `resize` uses the `image.Fit.FIT_CONTAIN` method by default, that is, the aspect ratio is maintained and the surrounding is filled with black. The detected coordinates will also be automatically mapped to the coordinates of the original `img`.

## Training Your Own Object Detection Model

Please visit [MaixHub](https://maixhub.com) to learn and train object detection models. When creating a project, select `Object Detection Model`.

## Appendix: 80 Categories

The 8 objects in the COCO dataset are:


```txt
person
bicycle
car
motorcycle
airplane
bus
train
truck
boat
traffic light
fire hydrant
stop sign
parking meter
bench
bird
cat
dog
horse
sheep
cow
elephant
bear
zebra
giraffe
backpack
umbrella
handbag
tie
suitcase
frisbee
skis
snowboard
sports ball
kite
baseball bat
baseball glove
skateboard
surfboard
tennis racket
bottle
wine glass
cup
fork
knife
spoon
bowl
banana
apple
sandwich
orange
broccoli
carrot
hot dog
pizza
donut
cake
chair
couch
potted plant
bed
dining table
toilet
tv
laptop
mouse
remote
keyboard
cell phone
microwave
oven
toaster
sink
refrigerator
book
clock
vase
scissors
teddy bear
hair drier
toothbrush
```

