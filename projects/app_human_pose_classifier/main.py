from maix import camera, display, image, nn, app, time, touchscreen
import math
import time
import numpy as np

from PoseEstimation import PoseEstimation

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def get_back_btn_img(width):
    ret_width = int(width * 0.1)
    img_back = image.load("/maixapp/share/icon/ret.png")
    w, h = (ret_width, img_back.height() * ret_width // img_back.width())
    if w % 2 != 0:
        w += 1
    if h % 2 != 0:
        h += 1
    img_back = img_back.resize(w, h)
    return img_back

def to_keypoints_np(obj_points):
    keypoints = np.array(obj_points)
    keypoints = keypoints.reshape((-1, 2))
    # print("kps: ", keypoints)
    return keypoints

def main(disp):
    ts = touchscreen.TouchScreen()
    detector = nn.YOLO11(model="/root/models/yolo11n_pose.mud", dual_buff = False)
    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format(), fps=60)
    img_back = get_back_btn_img(cam.width())
    back_rect = [0, 0, img_back.width(), img_back.height()]
    back_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])
    pose_estimator = PoseEstimation()

    while not app.need_exit():
        img = cam.read()
        objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)
        for obj in objs:
            img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
            msg = f'[{obj.score:.2f}], {pose_estimator.evaluate_pose(to_keypoints_np(obj.points))}'
            img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED, scale=0.5)
            detector.draw_pose(img, obj.points, 8 if detector.input_width() > 480 else 4, image.COLOR_RED)
        img.draw_image(0, 0, img_back)
        disp.show(img)

        x, y, preesed = ts.read()
        if is_in_button(x, y, back_rect_disp):
            app.set_exit_flag(True)

image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 32)
# print("fonts:", image.fonts())
image.set_default_font("sourcehansans")

disp = display.Display()
try:
    while not app.need_exit():
        main(disp)
except Exception:
    import traceback
    msg = traceback.format_exc()
    img = image.Image(disp.width(), disp.height())
    img.draw_string(0, 0, msg, image.COLOR_WHITE)
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(100)
