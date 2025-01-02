from maix import camera, display, image, nn, app, time, touchscreen
import math

model_id = 1
models = [
    "/root/models/hand_landmarks.mud",
    "/root/models/hand_landmarks_bf16.mud"
]

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def main(disp):
    global model_id
    ts = touchscreen.TouchScreen()
    detector = nn.HandLandmarks(model=models[model_id])
    img_back = image.load("/maixapp/share/icon/ret.png")
    back_rect = [0, 0, 32, 32]
    landmarks_rel = False
    history_len = 10
    histories = [[],[]]
    detect_time = [0, 0]

    cam = camera.Camera(320, 224, detector.input_format())
    model_rect = [0, cam.height() - 26, 80, 25]
    back_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])
    model_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, model_rect[0], model_rect[1], model_rect[2], model_rect[3])

    while not app.need_exit():
        img = cam.read()
        objs = detector.detect(img, conf_th = 0.7, iou_th = 0.45, conf_th2 = 0.8, landmarks_rel = landmarks_rel)
        for obj in objs:
            # img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
            msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}'
            img.draw_string(obj.points[0], obj.points[1], msg, color = image.COLOR_RED if obj.class_id == 0 else image.COLOR_GREEN, scale = 1.4, thickness = 2)
            detector.draw_hand(img, obj.class_id, obj.points, 3, 6, box=True)
            histories[obj.class_id].append((obj.points[32], obj.points[33]))
            if len(histories[obj.class_id]) > history_len:
                histories[obj.class_id].pop(0)
            detect_time[obj.class_id] = time.ticks_s()
            img.draw_string((obj.points[8] + obj.points[35]) // 2 - 5, (obj.points[9] + obj.points[36]) // 2 - 4, f"{obj.angle / math.pi * 180:.0f}", image.COLOR_WHITE)
        for i in range(2):
            if time.ticks_s() - detect_time[i] > 3:
                histories[i] = []
        for i, history in enumerate(histories):
            for j in range(1, len(history)):
                img.draw_line(history[j-1][0], history[j-1][1], history[j][0], history[j][1], color = image.COLOR_RED if i == 0 else image.COLOR_GREEN, thickness = 2)
        if len(histories[0]) > 0 and len(histories[1]) > 0:
            img.draw_line(histories[0][-1][0], histories[0][-1][1], histories[1][-1][0], histories[1][-1][1], image.COLOR_YELLOW)

        img.draw_image(0, 0, img_back)
        img.draw_rect(model_rect[0], model_rect[1], model_rect[2], model_rect[3], image.COLOR_WHITE)
        img.draw_string(4, img.height() - 20, f"model: {model_id}")
        disp.show(img)
        x, y, preesed = ts.read()
        if is_in_button(x, y, back_rect_disp):
            app.set_exit_flag(True)
        if is_in_button(x, y, model_rect_disp):
            model_id = (model_id + 1) % 2
            msg = "switching model ..."
            size = image.string_size(msg, scale=1.3)
            img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height())//2, msg, image.COLOR_RED, scale=1.3, thickness=-3)
            img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height())//2, msg, image.COLOR_WHITE, scale=1.3)
            disp.show(img)
            del detector
            break



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
