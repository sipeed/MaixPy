#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# difference
img = image.Image("test.jpg")
img2 = image.Image("test2.jpg")
img.difference(img2)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
