from maix import display, image, time, app

disp = display.Display()

img = image.Image(320, 240)
img.draw_rect(100, 100, 100, 100, image.COLOR_WHITE)
img.flood_fill(50, 50, 0.05, 0.05, image.COLOR_ORANGE)
img.flood_fill(110, 110, 0.05, 0.05, image.COLOR_RED)
disp.show(img)

while not app.need_exit():
    time.sleep(1)
