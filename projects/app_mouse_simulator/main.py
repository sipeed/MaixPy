from maix import image, display, touchscreen, time, hid, app

disp = display.Display()
ts = touchscreen.TouchScreen()
img = image.Image(disp.width(), disp.height(), bg=image.COLOR_BLACK)
mouse = None
try:
    mouse = hid.Hid(hid.DeviceType.DEVICE_MOUSE)
except Exception as e:
    print(e)
    image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 24)
    image.set_default_font("sourcehansans")
    img.draw_string(0, 0, "Maybe the HID device is not enabled.", image.COLOR_WHITE, 1)
    img.draw_string(0, 50, "Try: Settings -> USB Settings -> HID Mouse, then click Confirm and reboot", image.COLOR_WHITE, 1)
    img.draw_string(0, 150, "Click anywhere to exit.", image.COLOR_WHITE, 1)
    while not app.need_exit():
        t = ts.read()
        if t[2]:
            exit(0)
        disp.show(img)

main_x = 0
main_y = 0
main_w = int(disp.width() * 0.8)
main_h = int(disp.height() * 0.8)
key_w = int(main_w / 2)
key_h = int(disp.height() - main_h)
left_key_x = 0
left_key_y = disp.height() - key_h
right_key_x = left_key_x + key_w
right_key_y = left_key_y
wheel_w = disp.width() - main_w
wheel_h = main_h
wheel_x = main_w
wheel_y = 0
exit_w = disp.width() - main_w
exit_h = disp.height() - main_h
exit_x = main_w
exit_y = main_h

main_box = [main_x, main_y, main_w, main_h]
left_key_box = [left_key_x, left_key_y, key_w, key_h]
right_key_box = [right_key_x, right_key_y, key_w, key_h]
wheel_box = [wheel_x, wheel_y, wheel_w, wheel_h]
exit_box = [exit_x, exit_y, exit_w, exit_h]

delay_ms = 100
# left key param
touch_left_key_last_ms = time.ticks_ms()
keep_left_key_last_ms = time.ticks_ms()
left_key_touched = 0
# right key param
touch_right_key_last_ms = time.ticks_ms()
keep_right_key_last_ms = time.ticks_ms()
right_key_touched = 0
# wheel movement param
wheel_first_touch = 0
wheel_first_y = 0
# main param
main_first_touch = 0
main_first_x = 0
main_first_y = 0
main_first_press = 0
main_first_press_x = 0
main_first_press_y = 0
def touch_box(t, box, oft = 0):
    if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
        return True
    else:
        return False

def mouse_set(button, x, y, wheel_move):
    data = [button, x, y, wheel_move]
    mouse.write(data)

def caculate_main_oft(t, last_x, last_y):
    main_oft_x = t[0] - last_x
    main_oft_y = t[1] - last_y
    max_level = 100
    main_oft_x2 = int(main_oft_x  / (main_w // 2) * max_level)
    main_oft_y2 = int(main_oft_y  / (main_h // 2) * max_level)
    print(f"curr:{t[0]} first:{main_first_press_x} x offset:{main_oft_x} x offset2:{main_oft_x2}")
    print(f"curr:{t[1]} first:{main_first_press_y} y offset:{main_oft_y} y offset2:{main_oft_y2}")
    return main_oft_x2, main_oft_y2

while not app.need_exit():
    t = ts.read()
    img.clear()
    img.draw_rect(main_x, main_y, main_w, main_h, image.COLOR_WHITE, 2)
    img.draw_string(main_x + 10, main_y + 10, "TOUCHPAD", image.COLOR_WHITE, 2)

    img.draw_rect(wheel_x, wheel_y, wheel_w, wheel_h, image.COLOR_WHITE, 2)
    img.draw_string(wheel_x + 10, wheel_y + 10, "WHEEL", image.COLOR_WHITE, 2)

    img.draw_rect(exit_x, exit_y, exit_w, exit_h, image.COLOR_WHITE, 2)
    img.draw_string(exit_x + 10, exit_y + 10, "EXIT", image.COLOR_WHITE, 2)

    # check exit
    if touch_box(t, exit_box, 0):
        print('exit')
        break

    # check the left key is touch
    if touch_box(t, left_key_box, 0):
        keep_left_key_last_ms = time.ticks_ms()
        if time.ticks_ms() - touch_left_key_last_ms > delay_ms:
            touch_left_key_last_ms = time.ticks_ms()
            left_key_touched = 1
            print("press left key")
            mouse_set(0x01, 0, 0, 0)

    # check the right key is touch
    if touch_box(t, right_key_box, 0):
        keep_right_key_last_ms = time.ticks_ms()
        if time.ticks_ms() - touch_right_key_last_ms > delay_ms:
            touch_right_key_last_ms = time.ticks_ms()
            right_key_touched = 1
            print("press right key")
            mouse_set(0x02, 0, 0, 0)

    # draw left key
    if left_key_touched:
        img.draw_rect(left_key_x, left_key_y, key_w, key_h, image.COLOR_WHITE, -1)
        img.draw_string(left_key_x + 10, left_key_y + 10, "LEFT KEY", image.COLOR_WHITE, 2)
        if time.ticks_ms() - keep_left_key_last_ms > 30:
            left_key_touched = 0
            print("release left key")
            mouse_set(0, 0, 0, 0)
    else:
        img.draw_rect(left_key_x, left_key_y, key_w, key_h, image.COLOR_WHITE, 2)
        img.draw_string(left_key_x + 10, left_key_y + 10, "LEFT KEY", image.COLOR_WHITE, 2)

    # draw right key
    if right_key_touched:
        img.draw_rect(right_key_x, right_key_y, key_w, key_h, image.COLOR_WHITE, -1)
        img.draw_string(right_key_x + 10, right_key_y + 10, "RIGHT KEY", image.COLOR_WHITE, 2)
        if time.ticks_ms() - keep_right_key_last_ms > 30:
            right_key_touched = 0
            print("release right key")
            mouse_set(0, 0, 0, 0)
    else:
        img.draw_rect(right_key_x, right_key_y, key_w, key_h, image.COLOR_WHITE, 2)
        img.draw_string(right_key_x + 10, right_key_y + 10, "RIGHT KEY", image.COLOR_WHITE, 2)

    # check wheel movement
    if touch_box(t, wheel_box, 0):
        if wheel_first_touch:
            wheel_oft = t[1] - wheel_first_y
            max_level = 6
            wheel_oft2 = int(wheel_oft  / (wheel_h // 2) * max_level)
            mouse_set(0, 0, 0, -wheel_oft2)
            time.sleep_ms(30)
            print(f"curr:{t[1]} first:{wheel_first_y} y offset:{wheel_oft} y offset2:{wheel_oft2}")
        wheel_first_y = t[1]
        wheel_first_touch = 1
    else:
        wheel_first_touch = 0
        wheel_first_y = 0

    # check main
    if touch_box(t, main_box, 0):
        if not main_first_press:
            main_first_press_x = t[0]
            main_first_press_y = t[1]
            main_first_press = 1
        if main_first_touch:
            main_oft_x2,main_oft_y2 = caculate_main_oft(t, main_first_x, main_first_y)
            mouse_set(0, main_oft_x2, main_oft_y2, 0)

        main_first_x = t[0]
        main_first_y = t[1]
        main_first_touch = 1
    else:
        if main_first_press:
            main_oft_x2,main_oft_y2 = caculate_main_oft(t, main_first_press_x, main_first_press_y)
            if main_oft_x2 == 0 and main_oft_y2 == 0:
                mouse_set(0x01, 0, 0, 0)
                time.sleep_ms(30)
                mouse_set(0, 0, 0, 0)
    
        main_first_touch = 0
        main_first_x = 0
        main_first_y = 0
        main_first_press = 0
        main_first_press_x = 0
        main_first_press_y = 0

    # draw red point
    if t[2]:
        img.draw_circle(t[0], t[1], 5, image.COLOR_RED, -1)

    disp.show(img)
