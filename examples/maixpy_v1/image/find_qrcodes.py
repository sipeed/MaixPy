#!/usr/bin/env python

from maix.v1 import lcd, sensor
from maix import time
import math

lcd.init()
sensor.reset()
sensor.set_framesize(sensor.VGA)
sensor.run(1)

roi = [160, 120, 320, 240]

while True:
    img = sensor.snapshot()

    qrcodes = img.find_qrcodes(roi)
    for a in qrcodes:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], (255,0,0))

        # rect
        rect = a.rect()
        img.draw_rectangle(rect[0], rect[1], rect[2], rect[3], (0,0,255))
        img.draw_string(rect[0] + 5, rect[1] + 5, "rect", (0,0,255))

        # payload
        img.draw_string(a.x() + a.w() + 5, rect[1] + 20, "payload: " + a.payload(), (0,0,255))

        # version
        img.draw_string(a.x() + a.w() + 5, rect[1] + 35, "version: " + str(a.version()), (0,0,255))
        img.draw_string(a.x() + a.w() + 5, rect[1] + 50, "ecc_level: " + str(a.ecc_level()), (0,0,255))
        img.draw_string(a.x() + a.w() + 5, rect[1] + 65, "mask: " + str(a.mask()), (0,0,255))
        img.draw_string(a.x() + a.w() + 5, rect[1] + 80, "data_type: " + str(a.data_type()), (0,0,255))
        img.draw_string(a.x() + a.w() + 5, rect[1] + 95, "eci: " + str(a.eci()), (0,0,255))
        if a.is_numeric():
            img.draw_string(a.x() + a.w() + 5, rect[1] + 110, "is numeric", (0,0,255))
        elif a.is_alphanumeric():
            img.draw_string(a.x() + a.w() + 5, rect[1] + 110, "is alphanumeric", (0,0,255))
        elif a.is_binary():
            img.draw_string(a.x() + a.w() + 5, rect[1] + 110, "is binary", (0,0,255))
        elif a.is_kanji():
            img.draw_string(a.x() + a.w() + 5, rect[1] + 110, "is kanji", (0,0,255))
        else:
            img.draw_string(a.x() + a.w() + 5, rect[1] + 110, "is unknown", (0,0,255))

    img.draw_rectangle(roi[0], roi[1], roi[2], roi[3], (0,255,0))
    img.draw_string(roi[0] + 5, roi[1] + 5, "ROI", (0,255,0))

    lcd.display(img)
