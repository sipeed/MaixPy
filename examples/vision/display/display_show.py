from maix import display, app, image

disp = display.Display()
print("display init done")
print(f"display size: {disp.width()}x{disp.height()}")

y = 0
text = "Hello, MaixPy!"
while not app.need_exit():
    img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888)
    # img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888, bg=image.COLOR_BLACK)
    img.draw_rect(0, y, image.string_size(text, scale=2).width() + 10, 80, color=image.Color.from_rgb(255, 0, 0), thickness=-1)
    img.draw_string(4, y + 4, text, color=image.Color.from_rgb(255, 255, 255), scale=2)

    disp.show(img)

    y = (y + 1) % disp.height()

