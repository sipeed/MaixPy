#!/usr/bin/env python

from maix.v1 import lcd, sensor
from maix import time
import math

lcd.init()
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

while True:
    img = sensor.snapshot()

    rects = img.find_rects(threshold = 10000)
    for a in rects:
        # corners
        corners = a.corners()
        for i in range(4):
            img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], (255,0,0))

        # rect
        rect = a.rect()
        img.draw_rectangle(rect[0], rect[1], rect[2], rect[3], (0,255,0))
        img.draw_string(rect[0] + 5, rect[1] + 5, "rect", (0,255,0))
        img.draw_string(rect[0] + 5, rect[1] + 20, "magnitude: " + str(a.magnitude()), (0,255,0))

    lcd.display(img)