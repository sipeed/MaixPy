from maix import nn, camera, display, image, time, touchscreen, app
import math

pressed_flag = [False, False, False]
learn_id = 0

def main(disp):
    global pressed_flag, learn_id
    recognizer = nn.FaceRecognizer(detect_model="/root/models/retinaface.mud", feature_model = "/root/models/face_feature.mud")

    # if os.path.exists("/root/faces.bin"):
    #     recognizer.load_faces("/root/faces.bin")

    cam = camera.Camera(recognizer.input_width(), recognizer.input_height(), recognizer.input_format())
    ts = touchscreen.TouchScreen()
    back_btn_pos = (0, 0, 70, 30) # x, y, w, h
    learn_btn_pos = (0, recognizer.input_height() - 30, 60, 30)
    clear_btn_pos = (recognizer.input_width() - 60, recognizer.input_height() - 30, 60, 30)
    back_btn_disp_pos = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_btn_pos[0], back_btn_pos[1], back_btn_pos[2], back_btn_pos[3])
    learn_btn_disp_pos = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, learn_btn_pos[0], learn_btn_pos[1], learn_btn_pos[2], learn_btn_pos[3])
    clear_btn_disp_pos = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, clear_btn_pos[0], clear_btn_pos[1], clear_btn_pos[2], clear_btn_pos[3])

    def draw_btns(img : image.Image):
        img.draw_rect(back_btn_pos[0], back_btn_pos[1], back_btn_pos[2], back_btn_pos[3], image.Color.from_rgb(255, 255, 255), 2)
        img.draw_string(back_btn_pos[0] + 4, back_btn_pos[1] + 8, "< back", image.COLOR_WHITE)
        img.draw_rect(learn_btn_pos[0], learn_btn_pos[1], learn_btn_pos[2], learn_btn_pos[3], image.Color.from_rgb(255, 255, 255), 2)
        img.draw_string(learn_btn_pos[0] + 4, learn_btn_pos[1] + 8, "learn", image.COLOR_WHITE)
        img.draw_rect(clear_btn_pos[0], clear_btn_pos[1], clear_btn_pos[2], clear_btn_pos[3], image.Color.from_rgb(255, 255, 255), 2)
        img.draw_string(clear_btn_pos[0] + 4, clear_btn_pos[1] + 8, "clear", image.COLOR_WHITE)

    def is_in_button(x, y, btn_pos):
        return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

    def on_touch(x, y, pressed):
        '''
            Return learn, clear, ret
        '''
        global pressed_flag, learn_id
        if pressed:
            if is_in_button(x, y, back_btn_disp_pos):
                pressed_flag[2] = True
            elif is_in_button(x, y, learn_btn_disp_pos):
                pressed_flag[0] = True
            elif is_in_button(x, y, clear_btn_disp_pos):
                pressed_flag[1] = True
            else: # cancel
                pressed_flag = [False, False, False]
        else:
            if pressed_flag[0]:
                print("learn btn click")
                pressed_flag[0] = False
                return True, False, False
            if pressed_flag[1]:
                print("clear btn click")
                pressed_flag[1] = False
                learn_id = 0
                return False, True, False
            if pressed_flag[2]:
                print("back btn click")
                pressed_flag[2] = False
                return False, False, True
        return False, False, False

    # Init key will cancel the default ok button function(exit app)
    last_learn_img = None
    last_learn_t = 0

    while not app.need_exit():
        x, y, pressed = ts.read()
        learn, clear, back = on_touch(x, y, pressed)
        if back:
            break
        elif clear:
            for i in range(len(recognizer.labels) - 1):
                recognizer.remove_face(0)
        img = cam.read()
        faces = recognizer.recognize(img, 0.5, 0.45, 0.8, learn, learn)
        for obj in faces:
            color = image.COLOR_RED if obj.class_id == 0 else image.COLOR_GREEN
            img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = color)
            radius = math.ceil(obj.w / 10)
            img.draw_keypoints(obj.points, color, size = radius if radius < 5 else 4)
            msg = f'{recognizer.labels[obj.class_id]}: {obj.score:.2f}'
            img.draw_string(obj.x, obj.y - 10, msg, color = color)
            if learn and obj.class_id == 0: # unknown face, we add it
                name = f"id_{learn_id}"
                print("add face:", name)
                recognizer.add_face(obj, name)
                learn_id += 1
            if learn:
                last_learn_img = obj.face
                last_learn_t = time.ticks_s()
        # show learned face on left-top
        if last_learn_img and time.ticks_s() - last_learn_t < 5:
            img.draw_image(0, 0, last_learn_img)
        if learn:
            recognizer.save_faces("/root/faces.bin")
        draw_btns(img)
        disp.show(img)


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
