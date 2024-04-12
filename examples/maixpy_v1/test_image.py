#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()
print('lcd width:', lcd.width())
print('lcd height:', lcd.height())

img = image.Image("test.jpg")
print('img width:', img.width())
print('img height:', img.height())
print('img format:', img.format())
print('img data size:', img.size())
lcd.display(img)

while True:
    time.sleep(1)
