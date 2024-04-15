#!/usr/bin/env python

from maix.v1 import lcd, sensor
from maix import time

def draw_histogram(img, list, x, y, color):
    l_len = len(list)
    l_step = 2
    l_max = 100
    img.draw_line(x, y, x + l_step * l_len, y, (255,0,0))
    img.draw_line(x, y, x, y + l_max, (255,0,0))
    for i in range(l_len):
        img.draw_rectangle(x + i * l_step, y, l_step, int(list[i] * img.width() * img.height() / 100), color)

lcd.init()
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

thresholds = [[0, 80, 40, 80, 10, 80]]      # red

while True:
    img = sensor.snapshot()

    hist = img.get_histogram(thresholds)
    l_list = hist["L"]
    a_list = hist["A"]
    b_list = hist["B"]
    draw_histogram(img, l_list, 50, 50, (255,0,0))
    draw_histogram(img, a_list, 50, 200, (0,255,0))
    draw_histogram(img, b_list, 50, 350, (0,0,255))

    lcd.display(img)
