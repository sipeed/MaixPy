---
title: Using YOLOv5 / YOLOv8 Models for Object Detection in MaixPy
---

## Concept of Object Detection

Object detection refers to identifying the location and category of objects in images or videos, such as detecting apples, airplanes, etc., and marking their positions. Unlike classification, object detection includes positional information, so the result is generally a rectangle marking the object's position.

## Using Object Detection in MaixPy

MaixPy provides `YOLOv5` and `YOLOv8` models by default, which can be used directly:
> YOLOv8 requires MaixPy >= 4.3.0.

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff = True)
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

Video demonstration:

<div>
<video playsinline controls autoplay loop muted preload src="https://wiki.sipeed.com/maixpy/static/video/detector.mp4" type="video/mp4">
</div>

Here, the camera captures an image, which is then passed to the `detector` for detection. The results (classification names and positions) are displayed on the screen.

You can switch between `YOLOv5` and `YOLOv8` by replacing them in the code. Make sure to update the model file path accordingly.

The list of 80 supported object categories can be found in the appendix.

For more API usage, refer to the documentation of the [maix.nn](/api/maix/nn.html) module.

## dual_buff Dual Buffer Acceleration

You may have noticed that the model initialization uses `dual_buff` (which defaults to `True`). Enabling the `dual_buff` parameter can improve running efficiency and increase the frame rate. For detailed principles and usage notes, see [dual_buff Introduction](./dual_buff.md).

## More Input Resolutions

The default model input resolution is `320x224`, which closely matches the provided screen resolution. You can manually download models with other resolutions if needed:

YOLOv5: [https://maixhub.com/model/zoo/365](https://maixhub.com/model/zoo/365)
YOLOv8: [https://maixhub.com/model/zoo/400](https://maixhub.com/model/zoo/400)

Higher resolutions increase accuracy but also require more processing time. Choose the appropriate resolution based on your application.

## Which to Use: YOLOv5 or YOLOv8?

We provide `YOLOv5s` and `YOLOv8n` models. The former is larger and more accurate, while the latter is slightly faster but with marginally lower accuracy. You can test both to see which suits your needs better.

You can also try `YOLOv8s`, which offers higher accuracy but lower frame rates(e.g. yolov8s_320x224 slower than yolov8n_320x224 about 10ms）. Models can be downloaded from the mentioned model library.

## Can Camera Resolution and Model Resolution Differ?

When using the `detector.detect(img)` function, if `img` resolution differs from the model's resolution, the function will automatically call `img.resize` to adjust the image to the model's input resolution. The `resize` method uses `image.Fit.FIT_CONTAIN` by default, maintaining the aspect ratio and padding with black. The detected coordinates will map back to the original `img` coordinates.

## Training Your Own Object Detection Model on MaixHub

If the default 80-class model doesn't meet your needs, visit [MaixHub](https://maixhub.com) to learn and train your object detection model. Select `Object Detection Model` when creating a project. Refer to [MaixHub online train doc](./maixhub_train.md).

Alternatively, check out the models shared by community members in the [MaixHub Model Library](https://maixhub.com/model/zoo?platform=maixcam).

## Offline Training of Your Own Object Detection Model

We strongly recommend using MaixHub for online training. Offline training is more complex and not suggested for beginners. This method assumes some pre-existing knowledge not covered in this document. For more details, see [Offline Training YOLOv5 Model](./customize_model_yolov5.md).

## Appendix: 80 Categories

The 80 object categories from the COCO dataset are:

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
