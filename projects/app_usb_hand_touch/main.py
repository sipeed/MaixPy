from maix import camera, display, image, nn, app, time, hid, sys

SHOW_IMG = True
DEBUG_MODE = False
trans_img_quality = 19
target_screen_roi = [0.5, 0, 1, 1] # x1, y1, x2, y2 (unit is percent)
detect_roi = [0.1, 0.1, 0.9, 0.8]

if DEBUG_MODE:
    SHOW_IMG = True

target_screen_roi_size = [target_screen_roi[2] - target_screen_roi[0], target_screen_roi[3] - target_screen_roi[1]]

def send_keys(poses, keyboard, keys):
    cmd = [0, 0]
    for pose in poses:
        key_id = keys[pose]
        cmd.append(key_id)
    if len(cmd) < 8:
        cmd.extend([0] * (8 - len(cmd)))
    keyboard.write(cmd)


def touchpad_set(touchpad, button, x_oft : float, y_oft : float, wheel_move : int):
    '''
        button 0:release, 1: left press, 2: right press, 4: wheel press
        x_oft abs pos, value in [0, 100]
        y_oft abs pos, value in [0, 100]
        wheel_move wheel move distance, value in [-127, 127]
    '''
    x_oft = min(1, max(0, x_oft))
    y_oft = min(1, max(0, y_oft))
    x_oft = target_screen_roi[0] + x_oft * target_screen_roi_size[0]
    y_oft = target_screen_roi[1] + y_oft * target_screen_roi_size[1]
    x_oft = int(x_oft * 0x7fff)
    y_oft = int(y_oft * 0x7fff)
    touchpad.write([button,
                    x_oft & 0xff, (x_oft >> 8) & 0xff,
                    y_oft & 0xff, (y_oft >> 8) & 0xff, 
                    wheel_move])

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

class HID_NOT_READY(Exception):
    pass

if sys.device_id() in ["maixcam", "maixcam-pro"]:
    model_id = 1
    models = [
        "/root/models/hand_landmarks.mud",
        "/root/models/hand_landmarks_bf16.mud"
    ]
    cam_w = 320
    cam_h = 240
else:
    model_id = 0
    models = [
        "/root/models/hand_landmarks.mud"
    ]
    cam_w = 640
    cam_h = 480

detect_roi_pixel = [detect_roi[0] * cam_w, detect_roi[1] * cam_h, detect_roi[2] * cam_w, detect_roi[3] * cam_h]
detect_roi_pixel_size = [detect_roi_pixel[2] - detect_roi_pixel[0], detect_roi_pixel[3] - detect_roi_pixel[1]]
print(detect_roi_pixel)
print(detect_roi_pixel_size)

def main(disp):
    detector = nn.HandLandmarks(model=models[model_id])
    img_back = get_back_btn_img(cam_w)
    back_rect = [0, 0, img_back.width(), img_back.height()]
    landmarks_rel = False

    cam = camera.Camera(cam_w, cam_h, detector.input_format())
    cam.hmirror(1)

    try:
        touchpad = hid.Hid(hid.DeviceType.DEVICE_TOUCHPAD)
    except Exception as e:
        print(e)
        raise HID_NOT_READY()

    pressed = 0
    last_press_time = 0
    x = 0
    y = 0
    while not app.need_exit():
        img = cam.read()
        objs = detector.detect(img, conf_th = 0.7, iou_th = 0.45, conf_th2 = 0.8, landmarks_rel = landmarks_rel)
        final_obj = None
        if len(objs) == 1:
            final_obj = objs[0]
        elif len(objs) > 1:
            max_s = 0
            for obj in objs:
                s = obj.w * obj.h
                if s > max_s:
                    final_obj = obj
                    max_s = s
        if final_obj:
            # img.draw_rect(final_obj.x, final_obj.y, final_obj.w, final_obj.h, color = image.COLOR_RED)
            # msg = f'{cstor.labels[final_obj.class_id]}: {final_obj.score:.2f}'
            # img.draw_detetring(final_obj.points[0], final_obj.points[1], msg, color = image.COLOR_RED if final_obj.class_id == 0 else image.COLOR_GREEN, scale = 1.4, thickness = 2)
            detector.draw_hand(img, final_obj.class_id, final_obj.points, 3, 6, box=True)
            # img.draw_string((final_obj.points[8] + final_obj.points[35]) // 2 - 5, (final_obj.points[9] + final_obj.points[36]) // 2 - 4, f"{final_obj.angle / math.pi * 180:.0f}", image.COLOR_WHITE)
            x, y, z = final_obj.points[8 + 24:8 + 24 + 3]
            x_middle, y_middle, z_middle = final_obj.points[8 + 36:8 + 36 + 3]
            x_thumb, y_thumb, z_thumb = final_obj.points[8 + 12:8 + 12 + 3]
            if pow(x_middle - x_thumb, 2) + pow(y_middle - y_thumb, 2) < 900:
                pressed = 1
                last_press_time = time.ticks_ms()
            else:
                pressed = 0
            x = (x - detect_roi_pixel[0]) / detect_roi_pixel_size[0]
            y = (y - detect_roi_pixel[1]) / detect_roi_pixel_size[1]
            touchpad_set(touchpad, pressed, x, y, 0)
        elif time.ticks_ms() - last_press_time > 3: # 3s not find hand
            pressed = False # cancel press status
            touchpad_set(touchpad, pressed, x, y, 0)
        if SHOW_IMG:
            disp.show(img)
            # display.send_to_maixvision(img)

if __name__ == '__main__':
    screen = display.Display()
    # set send to maixvision quality
    try:
        display.set_trans_image_quality(trans_img_quality)
    except Exception:
        pass
    try:
        main(screen)
    except Exception as e:
        if type(e) == HID_NOT_READY:
            msg = 'Set USB HID mode first:\n\n'
            msg += 'Settings -> USB Settings -> HID Touchpad, click Confirm.\n\n'
            msg += 'Or run examples/tools/maixcam_switch_usb_mode.py to enable the HID Touchpad.'
            scale = 1.2
        else:
            import traceback
            msg = traceback.format_exc()
            print(msg)
            scale = 0.6
        msg += "\n\npress button to exit"
        img = image.Image(screen.width(), screen.height(), bg=image.COLOR_BLACK)
        img.draw_string(2, 2, msg, image.COLOR_WHITE, font="hershey_complex_small", scale=scale)
        screen.show(img)
        while not app.need_exit():
            time.sleep(0.2)
