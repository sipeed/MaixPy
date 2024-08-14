#!/usr/bin/env python

from maix.v1 import lcd, sensor, image
from maix import time
import math

lcd.init()
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

threshold = [100, 200]
edge_type = image.EDGE_CANNY

while True:
    img = sensor.snapshot()

    img.find_edges(edge_type, threshold)

    lcd.display(img)
