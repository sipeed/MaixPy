from maix import image, display, app, time

image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 32)
print("fonts:", image.fonts())
image.set_default_font("sourcehansans")

disp = display.Display()

img = image.Image(disp.width(), disp.height())
img.draw_string(2, 2, "你好！Hello, world!", image.Color.from_rgb(255, 0, 0))

disp.show(img)
while not app.need_exit():
    time.sleep(1)

