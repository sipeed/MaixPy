---
title: MaixPy MaixCAM Using YOLOv5 / YOLOv8 / YOLO11 for Object Detection
---

## Object Detection Concept

Object detection refers to detecting the position and category of objects in images or videos, such as identifying apples or airplanes in a picture and marking their locations.

Unlike classification, object detection includes positional information. Therefore, the result of object detection is generally a rectangular box that marks the location of the object.

## Object Detection in MaixPy

MaixPy provides `YOLOv5`, `YOLOv8`, and `YOLO11` models by default, which can be used directly:
> YOLOv8 requires MaixPy >= 4.3.0.
> YOLO11 requires MaixPy >= 4.7.0.

```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff=True)
# detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff=True)
# detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color=image.COLOR_RED)
    disp.show(img)
```

Example video:

<div>
<video playsinline controls autoplay loop muted preload src="/static/video/detector.mp4" type="video/mp4">
</div>

Here, the camera captures an image, passes it to the `detector` for detection, and then displays the results (classification name and location) on the screen.

You can switch between `YOLO11`, `YOLOv5`, and `YOLOv8` simply by replacing the corresponding line and modifying the model file path.

For the list of 80 objects supported by the model, see the appendix of this document.

For more API usage, refer to the documentation for the [maix.nn](/api/maix/nn.html) module.

## dual_buff for Double Buffering Acceleration

You may notice that the model initialization uses `dual_buff` (default value is `True`). Enabling the `dual_buff` parameter can improve efficiency and increase the frame rate. For more details and usage considerations, see the [dual_buff Introduction](./dual_buff.md).

## More Input Resolutions

The default model input resolution is `320x224`, which closely matches the aspect ratio of the default screen. You can also download other model resolutions:

YOLOv5: [https://maixhub.com/model/zoo/365](https://maixhub.com/model/zoo/365)
YOLOv8: [https://maixhub.com/model/zoo/400](https://maixhub.com/model/zoo/400)
YOLO11: [https://maixhub.com/model/zoo/453](https://maixhub.com/model/zoo/453)

Higher resolutions provide more accuracy, but take longer to process. Choose the appropriate resolution based on your application.

## Which Model to Use: YOLOv5, YOLOv8, or YOLO11?

We provide three models: `YOLOv5s`, `YOLOv8n`, and `YOLO11n`. The `YOLOv5s` model is larger, while `YOLOv8n` and `YOLO11n` are slightly faster. According to official data, the accuracy is `YOLO11n > YOLOv8n > YOLOv5s`. You can test them to decide which works best for your situation.

Additionally, you may try `YOLOv8s` or `YOLO11s`, which will have a lower frame rate (e.g., `yolov8s_320x224` is 10ms slower than `yolov8n_320x224`), but offer higher accuracy. You can download these models from the model library mentioned above or export them yourself from the official `YOLO` repository.

## Different Resolutions for Camera and Model

If the resolution of `img` is different from the model's resolution when using the `detector.detect(img)` function, the function will automatically call `img.resize` to adjust the image to the model's input resolution. The default `resize` method is `image.Fit.FIT_CONTAIN`, which scales while maintaining the aspect ratio and fills the surrounding areas with black. The detected coordinates will also be automatically mapped back to the original `img`.

## Training Your Own Object Detection Model on MaixHub

If you need to detect specific objects beyond the 80 categories provided, visit [MaixHub](https://maixhub.com) to learn and train an object detection model. Select "Object Detection Model" when creating a project. Refer to the [MaixHub Online Training Documentation](./maixhub_train.md).

Alternatively, you can find models shared by community members at the [MaixHub Model Library](https://maixhub.com/model/zoo?platform=maixcam).

## Training Your Own Object Detection Model Offline

We strongly recommend starting with MaixHub for online training, as the offline method is much more difficult and is not suitable for beginners. Some knowledge may not be explicitly covered here, so be prepared to do further research.

Refer to [Training a Custom YOLOv5 Model](./customize_model_yolov5.md) or [Training a Custom YOLOv8/YOLO11 Model Offline](./customize_model_yolov8.md).

## Appendix: 80 Classes

The 80 objects in the COCO dataset are:

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
hair dryer
toothbrush
```

