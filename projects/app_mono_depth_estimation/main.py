from maix import camera, display, image, nn, app, touchscreen, time

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
    cmap = image.CMap.TURBO
    model = nn.DepthAnything(model="/root/models/depth_anything_v2_vits.mud", dual_buff = True)
    cam = camera.Camera(model.input_width(), model.input_height(), model.input_format())
    img_back = get_back_btn_img(cam.width())
    back_rect = [0, 0, img_back.width(), img_back.height()]
    back_rect_disp = image.resize_map_pos(cam.width(), cam.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_rect[0], back_rect[1], back_rect[2], back_rect[3])
    ts = touchscreen.TouchScreen()

    while not app.need_exit():
        img = cam.read()
        res = model.get_depth_image(img, image.Fit.FIT_CONTAIN, cmap)
        if res:
            # show = image.Image(img.width() + res.width(), max(img.height(),res.height()), model.input_format())
            # show.draw_image(0, 0, img)
            # show.draw_image(img.width(), 0, res)
            # disp.show(show)
            res.draw_image(0, 0, img_back)
            disp.show(res)
        x, y, preesed = ts.read()
        if is_in_button(x, y, back_rect_disp):
            app.set_exit_flag(True)

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
