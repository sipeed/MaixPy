from maix import camera, display, image, nn, app, time, touchscreen

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def main(disp):
    ts = touchscreen.TouchScreen()
    detector = nn.YOLOv8(model="/root/models/yolov8n_pose.mud")
    img_back = image.load("/maixapp/share/icon/ret.png")
    back_rect = [0, 0, 32, 32]

    cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
    back_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])

    while not app.need_exit():
        img = cam.read()
        objs = detector.detect(img, conf_th = 0.5, iou_th = 0.45, keypoint_th = 0.5)
        for obj in objs:
            img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
            msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
            img.draw_string(obj.x, obj.y, msg, color = image.COLOR_RED)
            detector.draw_pose(img, obj.points, 8 if detector.input_width() > 480 else 4, image.COLOR_RED)
        # img.draw_rect(back_rect[0], back_rect[1], back_rect[2], back_rect[3], image.COLOR_BLACK, -1)
        img.draw_image(0, 0, img_back)
        disp.show(img)
        x, y, preesed = ts.read()
        if is_in_button(x, y, back_rect_disp):
            app.set_exit_flag(True)



disp = display.Display()
try:
    main(disp)
except Exception:
    import traceback
    msg = traceback.format_exc()
    img = image.Image(disp.width(), disp.height())
    img.draw_string(0, 0, msg, image.COLOR_WHITE)
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(100)
