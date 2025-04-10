from maix import display, image, app, time

disp = display.Display()
img = image.Image(320, 240, image.Format.FMT_RGBA8888)
img.draw_rect(0, 0, img.width(), img.height(), image.COLOR_BLUE, -1)

img2 = image.Image(160, 120, image.Format.FMT_RGBA8888)
img2.draw_rect(0, 0, img2.width(), img2.height(), image.COLOR_RED, -1)

img3 = image.Image(160, 120, image.Format.FMT_RGBA8888)
img3.draw_rect(0, 0, img3.width(), img3.height(), image.COLOR_WHITE, -1)

for y in range(img3.height()):
    for x in range(img3.width()):
        values = img3.get_pixel(x, y)
        value = values[0] & 0x00ffffff
        value = value | 0x7f000000
        img3.set_pixel(x, y, [value])

img.draw_image(0, 0, img2)
img.draw_image(50, 50, img3)
disp.show(img)

while not app.need_exit():
    time.sleep_ms(100)

