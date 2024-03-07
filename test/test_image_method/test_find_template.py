from maix import camera, display, image
from pynput import keyboard
import threading
import time
import threading
import time
import signal
import sys

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

template_image = image.load("yout/template/image_path")
template_image = template_image.resize(100, 200)

roi = [160, 120, 320, 240]
threshold = 0.5
step = 4
search = image.TemplateMatch.SEARCH_EX
while 1:
    img = cam.read()

    rect = img.find_template(template_image, threshold, roi, step, search)
    if len(rect) > 0:
        img.draw_rect(rect[0], rect[1], rect[2], rect[3], image.COLOR_GREEN, 2)

    img.draw_image(10, 10, template_image)
    img.draw_rect(roi[0], roi[1], roi[2], roi[3], image.COLOR_GREEN)
    img.draw_text(roi[0] + 5, roi[1] + 5, "ROI", image.COLOR_GREEN)
    screen.show(img)
