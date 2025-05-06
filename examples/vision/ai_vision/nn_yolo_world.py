'''
    YOLO-World detection demo, if you want to detect different classes, please use nn_yolo_world_learn.py to generate feature file.
'''
from maix import camera, display, image, nn, app

model = "/root/models/yolo-world_4_class.mud"
feature = "/root/models/yolo-world_4_class_person.bin"
labels = "/root/models/yolo-world_4_class_person.txt"

detector = nn.YOLOWorld(model, feature, labels, dual_buff = True)

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
