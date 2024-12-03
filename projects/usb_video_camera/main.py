from maix import image, display, app, time, touchscreen
import cv2, os
from datetime import datetime

disp = display.Display()
ts = touchscreen.TouchScreen()

back_btn_pos = (0, 0, 130, 40) # x, y, w, h
back_btn_disp_pos = image.resize_map_pos(disp.width(), disp.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, back_btn_pos[0], back_btn_pos[1], back_btn_pos[2], back_btn_pos[3])
option_btn_pos = (disp.width()-120, 0, 120, 40)
option_btn_disp_pos = image.resize_map_pos(disp.width(), disp.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, option_btn_pos[0], option_btn_pos[1], option_btn_pos[2], option_btn_pos[3])
save_btn_pos = (disp.width()-90, disp.height()-40, 90, 40)
save_btn_disp_pos = image.resize_map_pos(disp.width(), disp.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, save_btn_pos[0], save_btn_pos[1], save_btn_pos[2], save_btn_pos[3])
frame1_btn_disp_pos = image.resize_map_pos(disp.width(), disp.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, int(disp.width()/4), int(disp.height()/4), int(disp.width()/2), int(disp.height()/5))
frame2_btn_disp_pos = image.resize_map_pos(disp.width(), disp.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, int(disp.width()/4), int(disp.height()/4)+int(disp.height()/5), int(disp.width()/2), int(disp.height()/5))
frame3_btn_disp_pos = image.resize_map_pos(disp.width(), disp.height(), disp.width(), disp.height(), image.Fit.FIT_CONTAIN, int(disp.width()/4), int(disp.height()/4)+2*int(disp.height()/5), int(disp.width()/2), int(disp.height()/5))

pressed_flag = [False, False, False, False, False, False]
option_flag = False
save_flag = False
save_time = 0

def draw_btns(img : image.Image):
        img.draw_rect(back_btn_pos[0], back_btn_pos[1], back_btn_pos[2], back_btn_pos[3], image.Color.from_rgb(255, 255, 255), 2)
        img.draw_string(back_btn_pos[0] + 4, back_btn_pos[1] + 8, "< back", image.COLOR_WHITE, 2)
        img.draw_rect(option_btn_pos[0], option_btn_pos[1], option_btn_pos[2], option_btn_pos[3], image.Color.from_rgb(255, 255, 255), 2)
        img.draw_string(option_btn_pos[0] + 4, option_btn_pos[1] + 8, "Option", image.COLOR_WHITE, 2)
        img.draw_rect(save_btn_pos[0], save_btn_pos[1], save_btn_pos[2], save_btn_pos[3], image.Color.from_rgb(255, 255, 255), 2)
        img.draw_string(save_btn_pos[0] + 4, save_btn_pos[1] + 8, "Save", image.COLOR_WHITE, 2)

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def on_touch(x, y, pressed):
    global pressed_flag, learn_id
    if pressed:
        if is_in_button(x, y, back_btn_disp_pos):
            pressed_flag[0] = True
        elif is_in_button(x, y, option_btn_disp_pos):
            pressed_flag[1] = True
        elif is_in_button(x, y, save_btn_disp_pos):
            pressed_flag[2] = True
        elif is_in_button(x, y, frame1_btn_disp_pos):
            pressed_flag[3] = True
        elif is_in_button(x, y, frame2_btn_disp_pos):
            pressed_flag[4] = True
        elif is_in_button(x, y, frame3_btn_disp_pos):
            pressed_flag[5] = True
        else: # cancel
            pressed_flag = [False, False, False, False, False, False]
    else:
        if pressed_flag[0]:
            print("back btn click")
            pressed_flag[0] = False
            return True, False, False, False, False, False
        elif pressed_flag[1]:
            print("option btn click")
            pressed_flag[1] = False
            return False, True, False, False, False, False
        elif pressed_flag[2]:
            print("save btn click")
            pressed_flag[2] = False
            return False, False, True, False, False, False
        elif pressed_flag[3]:
            print("frame1 btn click")
            pressed_flag[3] = False
            return False, False, False, True, False, False
        elif pressed_flag[4]:
            print("frame2 btn click")
            pressed_flag[4] = False
            return False, False, False, False, True, False
        elif pressed_flag[5]:
            print("frame3 btn click")
            pressed_flag[5] = False
            return False, False, False, False, False, True
    return False, False, False, False, False, False

img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888)

if os.path.exists("/boot/usb.host"):
    print("USB is in Host mode.")
else:
    print("Please set USB to Host mode.")
    img.draw_rect(0, 0, disp.width(), disp.height(), image.Color.from_bgr(17, 17, 17), -1)
    img.draw_string(20, int(disp.height()*0.45), "Please set USB to Host mode.", image.COLOR_WHITE, 2)
    draw_btns(img)
    disp.show(img)
    while True:
        x, y, pressed = ts.read()
        back, option, _, _, _, _ = on_touch(x, y, pressed)
        if back:
            exit()
        time.sleep_ms(10)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("can't open the camera")
    img.draw_rect(0, 0, disp.width(), disp.height(), image.Color.from_bgr(17, 17, 17), -1)
    img.draw_string(20, int(disp.height()*0.45), "Please check if the camera is connected.", image.COLOR_WHITE, 2)
    draw_btns(img)
    disp.show(img)
    while True:
        x, y, pressed = ts.read()
        back, option, _, _, _, _ = on_touch(x, y, pressed)
        if back:
            exit()
        time.sleep_ms(10)

porp_frame = [(320, 240), (640, 480), (1920, 1080)]
frame_option = (320, 240)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

while not app.need_exit():
    ret, frame = cap.read()
    if not ret:
        print("can't read the frame")
        continue

    img = image.cv2image(frame, True, False)
    img_resize = img.resize(disp.width(), disp.height())

    x, y, pressed = ts.read()
    back, option, save, frame1, frame2, frame3 = on_touch(x, y, pressed)
    if back:
        break
    elif option:
        option_flag = not option_flag
    elif save:
        picture_root_path = app.get_picture_path()
        picture_date = datetime.now().strftime("%Y-%m-%d")
        picture_path = os.path.join(picture_root_path, picture_date)
        if not os.path.exists(picture_path):
            os.makedirs(picture_path)
        file_list = os.listdir(picture_path)
        picture_save_path = os.path.join(picture_path, f"{len(file_list)}.jpg")
        print(f"picture_save_path path: {picture_save_path}") 
        img.save(picture_save_path)
        save_flag = True
        save_time = time.ticks_ms()

    if option_flag == True:
        img_resize.draw_rect(int(disp.width()/4), int(disp.height()/8), int(disp.width()/2), int(disp.height()/1.2), image.Color.from_rgb(17, 17, 17), -1)
        img_resize.draw_string(int(disp.width()/3.1), int(disp.height()/6), "Set Resolution", image.COLOR_WHITE, 1.6)
        img_resize.draw_string(int(disp.width()/2.9), int(disp.height()/3.2), "320 x 240", image.COLOR_WHITE, 2)
        img_resize.draw_string(int(disp.width()/2.9), int(disp.height()/3.2)+int(disp.height()/5), "640 x 480", image.COLOR_WHITE, 2)
        img_resize.draw_string(int(disp.width()/3.2), int(disp.height()/3.2)+2*int(disp.height()/5), "1920 x 1080", image.COLOR_WHITE, 2)

        if frame_option == porp_frame[0]:
            img_resize.draw_string(int(disp.width()/2.9), int(disp.height()/3.2), "320 x 240", image.COLOR_GREEN, 2)
        elif frame_option == porp_frame[1]:
            img_resize.draw_string(int(disp.width()/2.9), int(disp.height()/3.2)+int(disp.height()/5), "640 x 480", image.COLOR_GREEN, 2)
        elif frame_option == porp_frame[2]:
            img_resize.draw_string(int(disp.width()/3.2), int(disp.height()/3.2)+2*int(disp.height()/5), "1920 x 1080", image.COLOR_GREEN, 2)

        if frame1:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, porp_frame[0][0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, porp_frame[0][1])
            frame_option = porp_frame[0]
            print(f"set frame to {porp_frame[0][0]} x {porp_frame[0][1]}")
            option_flag = False
        elif frame2:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, porp_frame[1][0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, porp_frame[1][1])
            frame_option = porp_frame[1]
            print(f"set frame to {porp_frame[1][0]} x {porp_frame[1][1]}")
            option_flag = False
        elif frame3:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, porp_frame[2][0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, porp_frame[2][1])
            frame_option = porp_frame[2]
            print(f"set frame to {porp_frame[2][0]} x {porp_frame[2][1]}")
            option_flag = False

    if save_flag == True:
        img_resize.draw_rect(int(disp.width()/4), int(disp.height()/6), int(disp.width()/2), int(disp.height()/6), image.COLOR_WHITE, -1)
        img_resize.draw_string(int(disp.width()/3.4), int(disp.height()/4.7), "Save Success", image.COLOR_BLACK, 2)
        if time.ticks_ms()-save_time >= 1000:
            save_flag = False

    draw_btns(img_resize)
    disp.show(img_resize)

cap.release()