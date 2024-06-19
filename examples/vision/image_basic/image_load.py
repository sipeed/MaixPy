from maix import display, image, app, time

file_path = "/maixapp/share/icon/detector.png"
img = image.load(file_path, format = image.Format.FMT_RGBA8888 if file_path.endswith(".png") else image.Format.FMT_RGB888)
if img is None:
    raise Exception(f"load image {file_path} failed")

disp = display.Display()
disp.show(img, fit = image.Fit.FIT_CONTAIN)

while not app.need_exit():
    time.sleep_ms(100)
