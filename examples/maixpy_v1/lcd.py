#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

img = image.Image("test.jpg")

lcd.init()
lcd.mirror(1)
lcd.display(img)

# lcd.clear()
print('lcd width:', lcd.width())
print('lcd height:', lcd.height())

while True:
    time.sleep(1)
