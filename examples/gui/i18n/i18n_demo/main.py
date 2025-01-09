'''
    Please read README.md of this dir fist!!!!!!!
'''

from maix import i18n, image, display, app, time, err

trans = i18n.Trans()
tr = trans.tr

# load translations from translation files
e = trans.load("locales")
err.check_raise(e, "load translation yamls failed")

# load Chinese font
image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 32)
image.set_default_font("sourcehansans")

disp = display.Display()

img = image.Image(disp.width(), disp.height())

# draw hello with system setting language
print("system locale setting:", trans.get_locale())
img.draw_string(2, 2, tr("hello"), image.Color.from_rgb(255, 0, 0))

# manually set locale to zh
trans.set_locale("zh")
img.draw_string(2, 40, tr("hello"), image.Color.from_rgb(255, 0, 0))

# manually set locale to en
trans.set_locale("en")
img.draw_string(2, 80, tr("hello"), image.Color.from_rgb(255, 0, 0))

disp.show(img)
while not app.need_exit():
    time.sleep(1)

