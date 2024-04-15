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

    barcodes = img.find_barcodes(roi)
    for a in barcodes:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], (255,0,0), 2)

        # rect
        rect = a.rect()
        img.draw_rectangle(rect[0], rect[1], rect[2], rect[3], (0,0,255), 2)
        img.draw_string(rect[0] + 5, rect[1] + 5, "rect", (0,0,255))

        # payload
        img.draw_string(a.x() + a.w() + 5, rect[1] + 20, "payload: " + a.payload(), (255,0,0))

        # type
        img.draw_string(a.x() + a.w() + 5, rect[1] + 35, "type: " + str(a.type()), (255,0,0))

        # rotation
        img.draw_string(a.x(), a.y() + 15, "rot: " + str(a.rotation()), (255,0,0))

        # quality
        img.draw_string(a.x(), a.y() + 30, "quality: " + str(a.quality()), (255,0,0))

    img.draw_rectangle(roi[0], roi[1], roi[2], roi[3], (0,255,0))
    img.draw_string(roi[0] + 5, roi[1] + 5, "ROI", (0,255,0))

    lcd.display(img)
