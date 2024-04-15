#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()

# add
img = image.Image("test.jpg")
img2 = image.Image("test2.jpg")
img.add(img2)
lcd.display(img)
time.sleep(1)

# sub
img = image.Image("test.jpg")
img2 = image.Image("test2.jpg")
img.sub(img2)
lcd.display(img)
time.sleep(1)

# mul
img = image.Image("test.jpg")
img2 = image.Image("test2.jpg")
img.mul(img2)
lcd.display(img)
time.sleep(1)

# div
img = image.Image("test.jpg")
img2 = image.Image("test2.jpg")
img.div(img2)
lcd.display(img)
time.sleep(1)

while True:
    time.sleep(1)
