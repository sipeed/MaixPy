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

    lines = img.find_lines()
    for a in lines:
        img.draw_line(a.x1(), a.y1(), a.x2(), a.y2(), (255,0,0), 2)
        theta = a.theta()
        rho = a.rho()
        angle_in_radians = math.radians(theta)
        x = int(math.cos(angle_in_radians) * rho)
        y = int(math.sin(angle_in_radians) * rho)
        img.draw_line(0, 0, x, y, (0,255,255), 2)
        img.draw_string(x, y, "theta: " + str(theta) + "," + "rho: " + str(rho), (0,255,0))

    lcd.display(img)
