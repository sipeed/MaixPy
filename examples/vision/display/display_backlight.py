from maix import pwm, time, display, image

disp = display.Display()

def show(i):
    img = image.Image(disp.width(), disp.height())
    img.draw_circle(disp.width() // 2, disp.height() //2, 50, image.COLOR_RED, thickness=-1)
    img.draw_string(2, 2, f"{i}%", image.COLOR_WHITE, scale=2)
    disp.show(img)

for i in range(100):
    disp.set_backlight(i)
    show(i)
    time.sleep_ms(50)

for i in range(100):
    disp.set_backlight(100 - i)
    show(100 - i)
    time.sleep_ms(50)
