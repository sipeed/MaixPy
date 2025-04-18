from maix import camera, display, image, nn, app, sys
import math

# download model from:
#                     https://wiki.sipeed.com/maixpy/doc/zh/vision/face_detection.html
# detector = nn.FaceDetector(model="/root/models/face_detector.mud")
# detector = nn.Retinaface(model="/root/models/retinaface.mud", dual_buff = True)
if sys.device_name().lower() == "maixcam2":
    detector = nn.YOLO11(model="/root/models/yolo11s_face.mud", dual_buff = False)
else:
    detector = nn.YOLOv8(model="/root/models/yolov8n_face.mud", dual_buff = False)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.4, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        radius = math.ceil(obj.w / 10)
        img.draw_keypoints(obj.points, image.COLOR_RED, size = radius if radius < 5 else 4)
    disp.show(img)
