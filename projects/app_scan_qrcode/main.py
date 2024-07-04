#!/usr/bin/env python

import struct
from maix import image
from maix import time
from maix.camera import Camera
from maix.display import Display
from maix.touchscreen import TouchScreen
from maix import comm

APP_CMD_REPORT_BARCODE  = 0x05              # defined by user
APP_CMD_REPORT_QRCODE   = 0x06              # defined by user
APP_CMD_REPORT_APRILTAG = 0x07              # defined by user

BARCODE_STR = "barcode"
QRCODE_STR = "qrcode"
APRILTAG_STR = "apriltag(TAG36H11)"
code = QRCODE_STR

exit_cnt = 0

disp = Display()
disp.open()

cam = Camera()
cam.open(disp.width(), disp.height())

screen_width = disp.width()
screen_height = disp.height()
camera_width = cam.width()
camera_height = cam.height()

ts = TouchScreen()

p = comm.CommProtocol()

font_size = 16
image.load_font("sourcehansans", "assets/GenShinGothic-Monospace-Medium-2.ttf", size = font_size)
image.set_default_font("sourcehansans")
def get_str_width(str, thickness = 1):
    return len(str) * font_size // 2 * thickness

def get_str_height(thickness = 1):
    return font_size * thickness

canvas_width = screen_width
canvas_height =  int(screen_height * 0.15)
upper_canvas = image.Image(screen_width, canvas_height)
lower_canvas = image.Image(screen_width, canvas_height)
upper_canvas_x = 0
upper_canvas_y = 0
lower_canvas_x = 0
lower_canvas_y = screen_height - canvas_height

button_w = screen_width // 4
button_h = int(canvas_height * 0.8)
button_x1 = (screen_width // 3 - button_w) // 2
button_x2 = (screen_width // 3 - button_w) // 2 + screen_width // 3
button_x3 = (screen_width // 3 - button_w) // 2 + screen_width // 3 * 2
button_y = (canvas_height - button_h) // 2

button1 = image.Image(button_w, button_h)
button1.draw_rect(0, 0, button1.width(), button1.height(), image.COLOR_BLACK, thickness = 2)
button2 = button1.copy()
button3 = button1.copy()

button1_touch = button1.copy()
button2_touch = button1.copy()
button3_touch = button1.copy()

button1_text_x = (button_w - get_str_width(BARCODE_STR)) // 2
button2_text_x = (button_w - get_str_width(QRCODE_STR)) // 2
button3_text_x = (button_w - get_str_width(APRILTAG_STR)) // 2
button_text_y = (button_h - get_str_height()) // 2
button1.draw_string(button1_text_x, button_text_y, BARCODE_STR, image.COLOR_WHITE)
button2.draw_string(button2_text_x, button_text_y, QRCODE_STR, image.COLOR_WHITE)
button3.draw_string(button3_text_x, button_text_y, APRILTAG_STR, image.COLOR_WHITE)

button1_touch.draw_rect(0, 0, button1.width(), button1.height(), image.Color.from_rgb(0x1a, 0x1a, 0x1a), thickness = -1)
button1_touch.draw_string(button1_text_x, button_text_y, BARCODE_STR, image.COLOR_WHITE)
button2_touch.draw_rect(0, 0, button1.width(), button1.height(), image.Color.from_rgb(0x1a, 0x1a, 0x1a), thickness = -1)
button2_touch.draw_string(button2_text_x, button_text_y, QRCODE_STR, image.COLOR_WHITE)
button3_touch.draw_rect(0, 0, button1.width(), button1.height(),image.Color.from_rgb(0x1a, 0x1a, 0x1a), thickness = -1)
button3_touch.draw_string(button3_text_x, button_text_y, APRILTAG_STR, image.COLOR_WHITE)
button_is_pressed = [False, True, False]

exit_img = image.load("./assets/exit.jpg")
exit_img_touch = image.load("./assets/exit_touch.jpg")
exit_img_x = int(exit_img.width() * 0.1)
exit_img_y = (canvas_height - exit_img.height()) // 2

roi = [camera_width // 4, camera_height // 4, camera_width // 2, camera_height // 2]

barcode_roi_w = int(camera_width // 1.5)
barcode_roi_h = int(camera_height // 3.5)
barcode_roi_x = (camera_width - barcode_roi_w) // 2
barcode_roi_y = (camera_height - barcode_roi_h) // 2
barcode_roi = [barcode_roi_x, barcode_roi_y, barcode_roi_w, barcode_roi_h]

draw_box_line_y = 0
draw_box_line_dir = 0

def is_button1(x, y, touch):
    if touch == 0:
        return False

    real_x = button_x1 + lower_canvas_x
    real_y = button_y + lower_canvas_y
    if x > real_x and x < real_x + button_w and y > real_y and y < real_y + button_h:
        return True
    else:
        return False

def is_button2(x, y, touch):
    if touch == 0:
        return False

    real_x = button_x2 + lower_canvas_x
    real_y = button_y + lower_canvas_y
    if x > real_x and x < real_x + button_w and y > real_y and y < real_y + button_h:
        return True
    else:
        return False

def is_button3(x, y, touch):
    if touch == 0:
        return False

    real_x = button_x3 + lower_canvas_x
    real_y = button_y + lower_canvas_y
    if x > real_x and x < real_x + button_w and y > real_y and y < real_y + button_h:
        return True
    else:
        return False

def is_exit(x, y, touch):
    if touch == 0:
        return False

    real_x = exit_img_x + upper_canvas_x
    real_y = exit_img_y + upper_canvas_y
    if x > real_x and x < real_x + exit_img.width() and y > real_y and y < real_y + exit_img.height():
        return True
    else:
        return False

def draw_box(img, x, y, w, h, color, tickness = 1, hidden_line = False):
    len = int(w * 0.05)
    img.draw_line(x, y, x + len, y, color, tickness)
    img.draw_line(x, y, x, y + len, color, tickness)
    img.draw_line(x + w, y, x + w - len, y, color, tickness)
    img.draw_line(x + w, y, x + w, y + len, color, tickness)
    img.draw_line(x + w, y + h, x + w - len, y + h, color, tickness)
    img.draw_line(x + w, y + h, x + w, y + h - len, color, tickness)
    img.draw_line(x, y + h, x + len, y + h, color, tickness)
    img.draw_line(x, y + h, x, y + h - len, color, tickness)

    global draw_box_line_y
    global draw_box_line_dir
    if draw_box_line_y == 0:
        draw_box_line_y = y
        draw_box_line_dir = 1
    else:
        if draw_box_line_y > y + h - h * 0.1:
            draw_box_line_dir = -1
        elif draw_box_line_y < y + h * 0.1:
            draw_box_line_dir = 1
        draw_box_line_y += 8 * draw_box_line_dir

    if hidden_line is False:
        img.draw_line(x + int(w * 0.1), draw_box_line_y, x + w - int(w * 0.1), draw_box_line_y, color, tickness)

def find_barcodes(img):
    barcodes = img.find_barcodes(barcode_roi)
    for a in barcodes:
        img.draw_string(a.x(), a.y() - 15, "result(" + str(len(a.payload())) + "): " + a.payload(), image.COLOR_RED)
        p.report(APP_CMD_REPORT_BARCODE, a.payload().encode())

    if (len(barcodes) > 0):
        return True
    else:
        return False

def find_qrcodes(img):
    resize_img = img.resize(320, 240)
    qrcodes = resize_img.find_qrcodes()
    for a in qrcodes:
        corners = a.corners()
        for i in range(4):
            corners[i][0] = corners[i][0] * img.width() // resize_img.width()
            corners[i][1] = corners[i][1] * img.height() // resize_img.height()
        x = a.x() * img.width() // resize_img.width()
        y = a.y() * img.height() // resize_img.height()

        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED, 2)
        img.draw_string(x, y - 15, "result(" + str(len(a.payload())) + "): " + a.payload(), image.COLOR_RED)
        p.report(APP_CMD_REPORT_QRCODE, a.payload().encode())

    if (len(qrcodes) > 0):
        return True
    else:
        return False

def find_apriltags(img):
    families = image.ApriltagFamilies.TAG36H11
    resize_img = img.resize(160, 120)
    new_roi = [1, 1, resize_img.width()-1, resize_img.height() -1]
    apriltags = resize_img.find_apriltags(new_roi, families)
    for a in apriltags:
        corners = a.corners()
        for i in range(4):
            corners[i][0] = corners[i][0] * img.width() // resize_img.width()
            corners[i][1] = corners[i][1] * img.height() // resize_img.height()
        x = a.x() * img.width() // resize_img.width()
        y = a.y() * img.height() // resize_img.height()
        w = a.w() * img.width() // resize_img.width()
        h = a.h() * img.height() // resize_img.height()
        cx = a.cx() * img.width() // resize_img.width()
        cy = a.cy() * img.height() // resize_img.height()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED, 2)

        img.draw_string(x + w + 5, y + 20, "id: " + str(a.id()), image.COLOR_RED)
        img.draw_string(x + w + 5, y + 35, "family: " + str(a.family()), image.COLOR_RED)
        img.draw_string(x + w + 5, y + 50, "coord: (" + str(cx) + "," + str(cy) + ")", image.COLOR_RED)

        data = struct.pack('<BHHHHH',  a.family(), a.id(), x, y, w, h)
        p.report(APP_CMD_REPORT_APRILTAG, data)
    if (len(apriltags) > 0):
        return True
    else:
        return False
while 1:
    img = cam.read()
    if img:
        res = False
        if code == BARCODE_STR:
            res = find_barcodes(img)
        elif code == QRCODE_STR:
            res = find_qrcodes(img)
        elif code == APRILTAG_STR:
            res = find_apriltags(img)
        else:
            print("error code: ", code)
            break

        if not disp.is_opened():
            break

        upper_canvas.clear()
        lower_canvas.clear()

        t = ts.read()
        if is_button1(t[0], t[1], t[2]) is True:
            code = BARCODE_STR
            for i in range(len(button_is_pressed)):
                button_is_pressed[i] = False
            button_is_pressed[0] = True

        if is_button2(t[0], t[1], t[2]) is True:
            code = QRCODE_STR
            for i in range(len(button_is_pressed)):
                button_is_pressed[i] = False
            button_is_pressed[1] = True

        if is_button3(t[0], t[1], t[2]) is True:
            code = APRILTAG_STR
            for i in range(len(button_is_pressed)):
                button_is_pressed[i] = False
            button_is_pressed[2] = True

        draw_roi = roi
        if button_is_pressed[0] is True:
            lower_canvas.draw_image(button_x1, button_y, button1_touch)
            draw_roi = barcode_roi
        else:
            lower_canvas.draw_image(button_x1, button_y, button1)

        if button_is_pressed[1] is True:
            lower_canvas.draw_image(button_x2, button_y, button2_touch)
        else:
            lower_canvas.draw_image(button_x2, button_y, button2)

        if button_is_pressed[2] is True:
            lower_canvas.draw_image(button_x3, button_y, button3_touch)
        else:
            lower_canvas.draw_image(button_x3, button_y, button3)

        if is_exit(t[0], t[1], t[2]) is True:
            upper_canvas.draw_image(exit_img_x, exit_img_y, exit_img_touch)
            exit_cnt = 1
        else:
            upper_canvas.draw_image(exit_img_x, exit_img_y, exit_img)
            if exit_cnt > 0:
                exit_cnt += 1

        if exit_cnt > 2:
            img.clear()
            disp.show(img)
            break

        draw_box(img, draw_roi[0], draw_roi[1], draw_roi[2], draw_roi[3], image.Color.from_rgb(0x4d, 0xdb, 0xff), 2, res)

        title = "Please put your " + code + " in the box"
        upper_canvas.draw_string((canvas_width - get_str_width(title)) // 2, int(canvas_height * 0.4), title, image.COLOR_WHITE)
        img.draw_image(upper_canvas_x, upper_canvas_y, upper_canvas)
        img.draw_image(lower_canvas_x, screen_height - canvas_height, lower_canvas)

        doc = "Learn more from wiki.sipeed.com/maixpy"
        img.draw_string((camera_width - get_str_width(doc)) // 2, upper_canvas_y + canvas_height + int(camera_height * 0.05), doc, image.COLOR_WHITE)
        disp.show(img)






