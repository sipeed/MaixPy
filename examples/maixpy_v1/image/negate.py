#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# negate
img = image.Image("test.jpg")
img.negate()
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
