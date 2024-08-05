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

    circles = img.find_circles(threshold = 3000)
    for a in circles:
        img.draw_circle(a.x(), a.y(), a.r(), (255,0,0), 2)
        img.draw_string(a.x() + a.r() + 5, a.y() + a.r() + 5, "r: " + str(a.r()) + "magnitude: " + str(a.magnitude()), (255,0,0))

    lcd.display(img)
