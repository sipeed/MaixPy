from maix import display, image, app, time

file_path = "/maixapp/share/icon/detector.png"
img = image.load(file_path, format = image.Format.FMT_RGBA8888 if file_path.endswith(".png") else image.Format.FMT_RGB888)
if img is None:
    raise Exception(f"load image {file_path} failed")

disp = display.Display()
img_show = image.Image(disp.width(), disp.height(), image.Format.FMT_RGBA8888)
img_show.draw_rect(0, 0, img_show.width(), img_show.height(), image.COLOR_PURPLE, thickness=-1)
img_show.draw_image(0, 0, img)
disp.show(img_show)

while not app.need_exit():
    time.sleep_ms(100)
