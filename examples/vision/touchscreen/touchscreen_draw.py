from maix import touchscreen, app, time, display, image

ts = touchscreen.TouchScreen()
disp = display.Display()

pressed_already = False
last_x = 0
last_y = 0
last_pressed = False
img = image.Image(disp.width(), disp.height())

# draw exit button
exit_label = "< Exit"
size = image.string_size(exit_label)
exit_btn_pos = [0, 0, 8*2 + size.width(), 12 * 2 + size.height()]

# draw clear button
clear_label = "Clear"
size = image.string_size(clear_label)
clear_btn_pos = [0, 0, 8*2 + size[0], 12 * 2 + size[1]]
clear_btn_pos[0] = disp.width() - clear_btn_pos[2]

def draw_btns(img):
    img.draw_string(8, 12, exit_label, image.COLOR_WHITE)
    img.draw_rect(exit_btn_pos[0], exit_btn_pos[1], exit_btn_pos[2], exit_btn_pos[3],  image.COLOR_WHITE, 2)

    img.draw_string(clear_btn_pos[0] + 8, 12, clear_label, image.COLOR_WHITE)
    img.draw_rect(clear_btn_pos[0], clear_btn_pos[1], clear_btn_pos[2], clear_btn_pos[3],  image.COLOR_WHITE, 2)

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def on_clicked(x, y):
    global img
    if is_in_button(x, y, exit_btn_pos):
        app.set_exit_flag(True)
    elif is_in_button(x, y, clear_btn_pos):
        img = image.Image(disp.width(), disp.height())
        draw_btns(img)

draw_btns(img)
while not app.need_exit():
    x, y, pressed = ts.read()
    if x != last_x or y != last_y or pressed != last_pressed:
        print(x, y, pressed)
        last_x = x
        last_y = y
        last_pressed = pressed
    if pressed:
        pressed_already = True
        img.draw_circle(x, y, 1, image.Color.from_rgb(255, 255, 255), 2)
    else:
        if pressed_already:
            print(f"clicked, x: {x}, y: {y}")
            pressed_already = False
            on_clicked(x, y)
    disp.show(img)
