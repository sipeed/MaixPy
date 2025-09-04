from maix import camera, display, app, time, nn, touchscreen, image, sys
from maix.version import version_major, version_minor

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

def check_env():
    if sys.device_id() == "maixcam2" and version_major * 100 + version_minor < 412:
        msg = f"MaixPy version must >= 4.12"
        msg2 = "please upgrade system"
        msg_size = image.string_size(msg)
        msg2_size = image.string_size(msg2)
        img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
        y = (img.height() - msg_size.height() * 2) // 2
        img.draw_string((img.width() - msg_size.width()) // 2, y, msg, image.COLOR_WHITE)
        img.draw_string((img.width() - msg2_size.width()) // 2, y + msg_size.height(), msg2, image.COLOR_WHITE)
        disp.show(img)
        while not app.need_exit():
            time.sleep_ms(100)
        return False
    return True

def main(disp):
    # Initialize variables
    if sys.device_id() == "maixcam2":
        if not check_env():
            return
        threshold = 0.5
        update_interval = 200
        lost_find_interval = 60
        model_path = "/root/models/mixformer_v2.mud"
        tracker = nn.MixFormerV2(model_path, update_interval, lost_find_interval)
        print(f"Load MixFormerV2 model {model_path} success")
    else:
        model_path = "/root/models/nanotrack.mud"
        tracker = nn.NanoTrack(model_path)
        print(f"Load NanoTrack model {model_path} success")
        threshold = 0.9

    touch = touchscreen.TouchScreen()
    cam = camera.Camera(disp.width(), disp.height(), tracker.input_format())
    print("Open camera success")

    status = 0  # 0: select target box, 1: tracking
    pressing = False
    target = nn.Object()
    btn_str = "Select"
    font_size = image.string_size(btn_str)
    img_back = image.load("/maixapp/share/icon/ret.png")
    back_rect = [0, 0, img_back.width(), img_back.height()]

    while not app.need_exit():
        img = cam.read()
        touch_status = touch.read()
        if status == 0:  # Selecting target
            if touch_status[2]:  # Finger press detected
                if not pressing:
                    target.x = touch_status[0]
                    target.y = touch_status[1]
                    print("Start select")
                pressing = True
            else:
                if pressing:  # Finger released, finalize selection
                    target.w = touch_status[0] - target.x
                    target.h = touch_status[1] - target.y
                    if target.w > 0 and target.h > 0:
                        print(f"Init tracker with rectangle x: {target.x}, y: {target.y}, w: {target.w}, h: {target.h}")
                        tracker.init(img, target.x, target.y, target.w, target.h)
                        print("Init tracker ok")
                        status = 1
                    else:
                        print(f"Rectangle invalid, x: {target.x}, y: {target.y}, w: {target.w}, h: {target.h}")
                pressing = False
            if pressing:
                img.draw_string(2, img.height() - font_size[1] * 2, "Select and release to complete", image.Color.from_rgb(255, 0, 0), 1.5)
                img.draw_rect(target.x, target.y, touch_status[0] - target.x, touch_status[1] - target.y, image.Color.from_rgb(255, 0, 0), 3)
            else:
                img.draw_string(2, img.height() - font_size[1] * 2, "Select target on screen", image.Color.from_rgb(255, 0, 0), 1.5)
        else:  # Tracking
            if touch_status[2]:  # Button pressed, return to selection mode
                pressing = True
            else:
                if pressing and is_in_button(touch_status[0], touch_status[1], [disp.width() - 100, disp.height() - 60, 100, 60]):
                    status = 0
                pressing = False
            r = tracker.track(img, threshold)
            img.draw_rect(r.x, r.y, r.w, r.h, image.Color.from_rgb(255, 0, 0), 4)
            img.draw_rect(r.points[0], r.points[1], r.points[2], r.points[3], image.Color.from_rgb(158, 158, 158), 1)
            img.draw_rect(r.points[4] - r.points[7] // 2, r.points[5] - r.points[7] // 2, r.points[7], r.points[7], image.Color.from_rgb(158, 158, 158), 1)
            if len(r.points) > 8:
                img.draw_rect(r.points[8] - r.points[10] // 2, r.points[9] - r.points[11] // 2, r.points[10], r.points[11], image.Color.from_rgb(0, 255, 0), 4)
            img.draw_string(r.x, r.y - font_size[1] - 2, f"{r.score:.2f}", image.Color.from_rgb(255, 0, 0), 1.5)
            img.draw_rect(disp.width() - 100, disp.height() - 60, 100, 60, image.Color.from_rgb(255, 255, 255), 4)
            img.draw_string(disp.width() - 100 + (100 - font_size[0]) // 2, disp.height() - 60 + (60 - font_size[1]) // 2, btn_str, image.Color.from_rgb(255, 255, 255), 1)
        if touch_status[2] and is_in_button(touch_status[0], touch_status[1], back_rect):
            app.set_exit_flag(True)
        img.draw_image(0, 0, img_back)
        disp.show(img)


disp = display.Display()
try:
    while not app.need_exit():
        main(disp)
except Exception:
    import traceback
    msg = traceback.format_exc()
    print(msg)
    img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
    img.draw_string(0, 0, msg, image.COLOR_WHITE)
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(100)

