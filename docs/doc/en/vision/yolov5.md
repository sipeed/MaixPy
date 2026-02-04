# MaixPy: Object Detection with YOLOv5 / YOLOv8 / YOLO11 / YOLO26 Models
## Concept of Object Detection
Object detection refers to identifying the positions and categories of targets in images or videos—for example, detecting objects like apples and airplanes in an image and marking their locations.

Unlike image classification, it includes positional information, so the result of object detection is usually a bounding box that outlines the object's position.

## Using Object Detection in MaixPy
MaixPy natively supports the **YOLOv5**, **YOLOv8**, **YOLO11** and **YOLO26** models, which can be used directly:
> YOLOv8 requires MaixPy >= 4.3.0.
> YOLO11 requires MaixPy >= 4.7.0.
> YOLO26 requires MaixPy >= 4.12.5.
```python
from maix import camera, display, image, nn, app

detector = nn.YOLOv5(model="/root/models/yolov5s.mud", dual_buff=True)
# detector = nn.YOLOv8(model="/root/models/yolov8n.mud", dual_buff=True)
# detector = nn.YOLO11(model="/root/models/yolo11n.mud", dual_buff=True)
# detector = nn.YOLO26(model="/root/models/yolo26n.mud", dual_buff=True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
    disp.show(img)
```

Demo Video:
<div>
<video playsinline controls autoplay loop muted preload src="/static/video/detector.mp4" type="video/mp4">
</video>
</div>

The code above captures images via the camera, passes them to the `detector` for inference, and then displays the detection results (category names and positions) on the screen after obtaining them.

You can switch between **YOLO11/v5/v8/26** simply by replacing the corresponding model initialization code—note to modify the model file path as well.

See the appendix of this article for the list of 80 object categories supported by the pre-trained models.

For more API details, refer to the documentation of the [maix.nn](/api/maix/nn.html) module.

## Dual Buffer Acceleration (`dual_buff`)
You may notice the `dual_buff` parameter is used during model initialization (it is `True` by default). Enabling this parameter can improve runtime efficiency and frame rate. For the specific principle and usage notes, see [Introduction to dual_buff](./dual_buff.md).

## More Input Resolutions
The default model input resolutions are **320x224** for MaixCam and **640x480** for MaixCam2, as these aspect ratios are close to the native screen resolutions of the devices. You can also manually download models with other resolutions for replacement:

YOLOv5: [https://maixhub.com/model/zoo/365](https://maixhub.com/model/zoo/365)
YOLOv8: [https://maixhub.com/model/zoo/400](https://maixhub.com/model/zoo/400)
YOLO11: [https://maixhub.com/model/zoo/453](https://maixhub.com/model/zoo/453)

Higher resolutions yield higher detection accuracy but take longer to run. Choose the appropriate resolution based on your application scenario.

## Which to Choose: YOLOv5, YOLOv8, YOLO11 or YOLO26?
The pre-provided models include **YOLOv5s**, **YOLOv8n**, **YOLO11n** and **YOLO26n**. The YOLOv5s model has a larger size, while YOLOv8n, YOLO11n and YOLO26n run slightly faster. According to official data, the accuracy ranking is **YOLO26n > YOLO11n > YOLOv8n > YOLOv5s**. You can conduct actual tests and select the model that fits your needs.

You can also try the **YOLOv8s** or **YOLO11s** models—their frame rates will be slightly lower (e.g., yolov8s_320x224 runs 10ms slower than yolov8n_320x224), but their accuracy is higher than the nano versions. These models can be downloaded from the model libraries mentioned above or exported by yourself from the official YOLO repositories.

## Is It Allowed to Use Different Resolutions for Camera and Model?
When using the `detector.detect(img)` function for inference, if the resolution of `img` differs from the model's input resolution, the function will automatically call `img.resize` to scale the image to match the model's input resolution. The default resizing method is `image.Fit.FIT_CONTAIN`, which scales the image while maintaining its aspect ratio and fills the surrounding areas with black pixels. The detected bounding box coordinates are also automatically mapped back to the coordinates of the original `img`.

## Train Custom Object Detection Models Online with MaixHub
If you need to detect specific objects instead of using the pre-trained 80-class model, visit [MaixHub](https://maixhub.com) to learn and train custom object detection models—simply select **Object Detection Model** when creating a project. For details, refer to [MaixHub Online Training Documentation](./maixhub_train.md).

You can also find models shared by the community in the [MaixHub Model Zoo](https://maixhub.com/model/zoo?platform=maixcam).

## Train Custom Object Detection Models Offline
It is highly recommended to start with MaixHub online training—offline training is more complex and not suggested for beginners.

This method assumes you have basic relevant knowledge (which will not be covered in this article). Search online for solutions if you encounter problems.

See [Offline Training of YOLOv5 Models](./customize_model_yolov5.md) or [Offline Training of YOLOv8/YOLO11/YOLO26 Models](./customize_model_yolov8.md) for details.

## Appendix: 80 Object Categories
The 80 object categories of the COCO dataset are as follows:
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