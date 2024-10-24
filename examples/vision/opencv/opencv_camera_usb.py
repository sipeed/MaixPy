
# Set USB mode to HOST first !!! Refer to http://wiki.sipeed.com/maixpy/doc/zh/vision/opencv.html

from maix import image, display, app
import cv2
import sys

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# cap.set(cv2.CAP_PROP_CONVERT_RGB, 0)

disp = display.Display()

if not cap.isOpened():
    print("无法打开摄像头")
    sys.exit(1)
print("开始读取")
while not app.need_exit():
    ret, frame = cap.read()
    if not ret:
        print("无法读取帧")
        break
    img = image.cv2image(frame, bgr=True, copy=False)
    disp.show(img)
