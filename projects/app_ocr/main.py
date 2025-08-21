from maix import camera, display, image, nn, app, time, touchscreen

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

def main(disp):
    model = "/root/models/pp_ocr.mud"
    ocr = nn.PP_OCR(model)

    cam = camera.Camera(ocr.input_width(), ocr.input_height(), ocr.input_format())
    ts = touchscreen.TouchScreen()
    img_back = get_back_btn_img(cam.width())
    back_rect = [0, 0, img_back.width(), img_back.height()]
    back_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])

    image.load_font("ppocr", "/maixapp/share/font/ppocr_keys_v1.ttf", size = 20)
    image.set_default_font("ppocr")

    while not app.need_exit():
        img = cam.read()
        objs = ocr.detect(img)
        for obj in objs:
            points = obj.box.to_list()
            img.draw_keypoints(points, image.COLOR_RED, 4, -1, 1)
            img.draw_string(obj.box.x4, obj.box.y4, obj.char_str(), image.COLOR_RED)
        img.draw_image(0, 0, img_back)
        disp.show(img)
        x, y, pressed = ts.read()
        if is_in_button(x, y, back_rect_disp):
            app.set_exit_flag(True)




if __name__ == '__main__':
    screen = display.Display()
    try:
        main(screen)
    except Exception:
        import traceback
        e = traceback.format_exc()
        print(e)
        img = image.Image(screen.width(), screen.height())
        img.draw_string(2, 2, e, image.COLOR_WHITE, font="hershey_complex_small", scale=0.6)
        screen.show(img)
        while not app.need_exit():
            time.sleep(0.2)
