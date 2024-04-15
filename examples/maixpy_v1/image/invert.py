#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()
img = image.Image("test.jpg")
img.binary([[0, 50]])
lcd.display(img)

while True:
    time.sleep(1)
