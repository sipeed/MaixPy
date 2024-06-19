from maix import nn, image, camera, display, app, time, touchscreen
import os

def get_learn_btn_rect(x, y, w, h, label):
    s = image.string_size(label)
    sc = image.string_size("a")
    btn_w = s.width() + sc.width() * 2
    btn_h = s.height()  + sc.height() * 2
    y = y - btn_h - 10
    return x, y, btn_w, btn_h, x + sc.width(), y + sc.height()

def draw_btns(img: image.Image, btns):
    for k, r in btns.items():
        img.draw_rect(r[0], r[1], r[2], r[3], image.COLOR_WHITE)
        img.draw_string(r[4], r[5], k, image.COLOR_WHITE)

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def draw_string_center(img, msg):
    img.draw_string((img.width() - image.string_size(msg, scale=2, thickness=6)[0]) // 2, img.height() // 2, msg, image.COLOR_WHITE, scale=2, thickness=6)
    img.draw_string((img.width() - image.string_size(msg, scale=2, thickness=6)[0]) // 2, img.height() // 2, msg, image.COLOR_RED, scale=2, thickness=2)

def main(disp):
    cam = camera.Camera(disp.width(), disp.height())
    ts = touchscreen.TouchScreen()

    btns = {}
    btns["Learn"] = get_learn_btn_rect(2, cam.height(), cam.width(), cam.height(), "Learn")
    btns["< Exit"] = get_learn_btn_rect(2, btns["Learn"][3] + 10, cam.width(), cam.height(), "< Exit")
    btns["+ Class"] = get_learn_btn_rect(2, cam.height() - btns["Learn"][3] - 50, cam.width(), cam.height(), "+ Class")
    btns["+ Sample"] = get_learn_btn_rect(2, cam.height() - btns["Learn"][3] - btns["+ Class"][3] - 100, cam.width(), cam.height(), "+ Sample")
    btns["Clear"] = get_learn_btn_rect(cam.width() - btns["Learn"][2], cam.height(), cam.width(), cam.height(), "Clear")


    classifier = nn.SelfLearnClassifier(model="/root/models/mobilenet_v2_no_top.mud")
    labels = []
    if os.path.exists("/root/my_classes.bin"):
        labels = classifier.load("/root/my_classes.bin")
    learn_times = 0
    show_msg = ""
    show_msg_t = 0

    res_max = None
    last_pressed = False
    while not app.need_exit():
        img = cam.read()
        # recognize
        crop = img.resize(classifier.input_width(), classifier.input_height(), image.Fit.FIT_COVER)
        if classifier.class_num() > 0:
            res_max = classifier.classify(crop)[0]

        # learn
        x, y, pressed = ts.read()
        if pressed:
            if not last_pressed:
                last_pressed = True
                if is_in_button(x, y, btns["+ Class"]):
                    classifier.add_class(crop)
                    labels.append(f"Class {len(labels) + 1}")
                    classifier.save("/root/my_classes.bin", labels=labels)
                elif is_in_button(x, y, btns["+ Sample"]):
                    classifier.add_sample(crop)
                    classifier.save("/root/my_classes.bin", labels=labels)
                elif is_in_button(x, y, btns["< Exit"]):
                    app.set_exit_flag(True)
                elif is_in_button(x, y, btns["Learn"]):
                    msg = "Learning ..."
                    draw_string_center(img, msg)
                    disp.show(img)
                    epoch = classifier.learn()
                    if epoch > 0:
                        learn_times += 1
                        classifier.save("/root/my_classes.bin", labels=labels)
                        show_msg = "Learn complete"
                        show_msg_t = time.ticks_s()
                    else:
                        show_msg = "Already learned"
                        show_msg_t = time.ticks_s()
                elif is_in_button(x, y, btns["Clear"]):
                    if os.path.exists("/root/my_classes.bin"):
                        os.remove("/root/my_classes.bin")
                    classifier.clear()
                    labels.clear()
                    res_max = None
                    learn_times = 0
        else:
            last_pressed = False

        # show
        min_len = min(img.width(), img.height())
        if img.width() == min_len:
            x = 0
            y = (img.height() - min_len) // 2
        else:
            x = (img.width() - min_len) // 2
            y = 0
        img.draw_rect(x, y, min_len, min_len, image.COLOR_WHITE, thickness=2)
        img.draw_string(x, y + 2, f"class: {classifier.class_num()}, sample: {classifier.sample_num()}, learn: {learn_times}", image.COLOR_RED, scale=1.5)
        img.draw_string(x, y + 4, f"class: {classifier.class_num()}, sample: {classifier.sample_num()}, learn: {learn_times}", image.COLOR_WHITE, scale=1.5)
        if res_max:
            img.draw_string(x, y + 30, f"{labels[res_max[0]]}", image.COLOR_WHITE, scale=2, thickness=6)
            img.draw_string(x, y + 32, f"{labels[res_max[0]]}", image.COLOR_RED, scale=2, thickness=2)
            img.draw_string(x, y + 62, f"similarity: {res_max[1]:.2f}", image.COLOR_WHITE, scale=1.5, thickness=4)
            img.draw_string(x, y + 64, f"similarity: {res_max[1]:.2f}", image.COLOR_RED, scale=1.5, thickness=2)
        draw_btns(img, btns)
        if show_msg and time.ticks_s() - show_msg_t < 3:
            draw_string_center(img, show_msg)
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
