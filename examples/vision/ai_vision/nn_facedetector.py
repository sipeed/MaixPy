from maix import camera, display, image, nn, app
import math

# download model from:
#                     https://maixhub.com/model/zoo/377 (face_detector https://github.com/biubug6/Face-Detector-1MB-with-landmark)
#                     https://maixhub.com/model/zoo/378 (retinafate https://github.com/biubug6/Pytorch_Retinaface)
# detector = nn.FaceDetector(model="/root/models/face_detector.mud")
detector = nn.Retinaface(model="/root/models/retinaface.mud", dual_buff = True)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
dis = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.4, iou_th = 0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        radius = math.ceil(obj.w / 10)
        img.draw_keypoints(obj.points, image.COLOR_RED, size = radius if radius < 5 else 4)
    dis.show(img)
