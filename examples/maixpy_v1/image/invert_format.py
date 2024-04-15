#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

from maix import image as maix_img

lcd.init()
img = image.Image("test.jpg")

print('invert format to grayscale')
img.to_grayscale()
lcd.display(img)
time.sleep(1)

print('invert format to rgb888')
img.to_rgb888()
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
