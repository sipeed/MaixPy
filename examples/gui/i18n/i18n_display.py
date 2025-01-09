from maix import i18n, image, display, app, time

trans_dict = {
    "zh": {
        "hello": "你好"
    },
    "en": {
    }
}

trans = i18n.Trans(trans_dict)
tr = trans.tr
trans.set_locale("zh")

disp = display.Display()


image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 24)
image.set_default_font("sourcehansans")

img = image.Image(disp.width(), disp.height())
img.draw_string(10, 10, tr("hello"), image.COLOR_WHITE, scale=2)
disp.show(img)

while not app.need_exit():
    time.sleep_ms(100)

