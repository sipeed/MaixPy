from maix import camera, display, image, nn, app, time, touchscreen
import math

sub_146_idxes = [0, 1, 4, 5, 6, 7, 8, 10, 13, 14, 17, 21, 33, 37, 39, 40, 46, 52, 53, 54, 55, 58, 61, 63, 65, 66, 67, 70, 78, 80,
    81, 82, 84, 87, 88, 91, 93, 95, 103, 105, 107, 109, 127, 132, 133, 136, 144, 145, 146, 148, 149, 150, 152, 153, 154, 155, 157,
    158, 159, 160, 161, 162, 163, 168, 172, 173, 176, 178, 181, 185, 191, 195, 197, 234, 246, 249, 251, 263, 267, 269, 270, 276, 282,
    283, 284, 285, 288, 291, 293, 295, 296, 297, 300, 308, 310, 311, 312, 314, 317, 318, 321, 323, 324, 332, 334, 336, 338, 356, 361,
    362, 365, 373, 374, 375, 377, 378, 379, 380, 381, 382, 384, 385, 386, 387, 388, 389, 390, 397, 398, 400, 402, 405,
    409, 415, 454, 466, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477]

sub_68_idxes = [162, 234, 93, 58, 172, 136, 149, 148, 152, 377, 378, 365, 397, 288, 323, 454, 389, 71, 63, 105, 66, 107, 336,
                296, 334, 293, 301, 168, 197, 5, 4, 75, 97, 2, 326, 305, 33, 160, 158, 133, 153, 144, 362, 385, 387, 263, 373,
                380, 61, 39, 37, 0, 267, 269, 291, 405, 314, 17, 84, 181, 78, 82, 13, 312, 308, 317, 14, 87]

sub_5_idxes = [468, 473, 4, 61, 291]

subs = {
    "478": [],
    "146": sub_146_idxes,
    "68": sub_68_idxes,
    "5": sub_5_idxes,
}
subs_keys = list(subs.keys())
curr_sub = 0

def get_sub_landmarks(points, points_z, idxes):
    if len(idxes) == 0:
        return points, points_z
    new_points = []
    new_points_z = []
    for i in idxes:
        new_points.append(points[i*2])
        new_points.append(points[i*2 + 1])
        new_points_z.append(points_z[i])
    return new_points, new_points_z

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def main(disp):
    global curr_sub

    detect_conf_th = 0.5
    detect_iou_th = 0.45
    landmarks_conf_th = 0.5
    landmarks_abs = True
    landmarks_rel = False
    max_face_num = 4

    mode_pressed = False
    detector = nn.YOLOv8(model="/root/models/yolov8n_face.mud", dual_buff = False)
    landmarks_detector = nn.FaceLandmarks(model="/root/models/face_landmarks.mud")

    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())

    ts = touchscreen.TouchScreen()
    img_back = image.load("/maixapp/share/icon/ret.png")
    back_rect = [0, 0, 32, 32]
    mode_rect = [0, cam.height() - 26, 100, 30]
    back_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])
    mode_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, mode_rect[0], mode_rect[1], mode_rect[2], mode_rect[3])

    while not app.need_exit():
        img = cam.read()
        results = []
        objs = detector.detect(img, conf_th = detect_conf_th, iou_th = detect_iou_th, sort = 1)
        count = 0
        for obj in objs:
            img_std = landmarks_detector.crop_image(img, obj.x, obj.y, obj.w, obj.h, obj.points)
            if img_std:
                res = landmarks_detector.detect(img_std, landmarks_conf_th, landmarks_abs, landmarks_rel)
                if res and res.valid:
                    results.append(res)
            count += 1
            if max_face_num > 0 and count >= max_face_num:
                break
        for res in results:
            sub, sub_z = get_sub_landmarks(res.points, res.points_z, subs[subs_keys[curr_sub]])
            landmarks_detector.draw_face(img, sub, len(sub_z), sub_z)

        img.draw_image(0, 0, img_back)
        img.draw_rect(mode_rect[0], mode_rect[1], mode_rect[2], mode_rect[3], image.COLOR_WHITE)
        img.draw_string(4, img.height() - 20, f"points: {subs_keys[curr_sub]}")
        disp.show(img)
        x, y, preesed = ts.read()
        if preesed:
            mode_pressed = True
        elif mode_pressed:
            mode_pressed = False
            if is_in_button(x, y, back_rect_disp):
                app.set_exit_flag(True)
            if is_in_button(x, y, mode_rect_disp):
                curr_sub = (curr_sub + 1) % len(subs_keys)

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
