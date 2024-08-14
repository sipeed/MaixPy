#!/usr/bin/env python

from maix.v1 import lcd, image
from maix import time

lcd.init()
img = image.Image(width = lcd.width(), height = lcd.height())
img.clear()
img.draw_line(0, 0, 50, 50, (255,0,0), 3)
img.draw_rectangle(60, 0, 50, 50, (0,255,0), 3, True)
img.draw_ellipse(200, 50, 50, 50, 50, (0,0,255), 3, True)
img.draw_string(0, 100, "Hello world", (0,255,0))
img.draw_cross(0, 200, (255,0,0))
img.draw_arrow(100, 200, 100, 250, (0,255,0))
new_img=image.Image("/maixapp/share/icon/maixvision.png")
img.draw_image(new_img.mean_pool(4, 4), 150, 200)
img.draw_keypoints((250, 200, 210, 200), (0,0,255))
img.draw_circle(300, 200, 50, (0,255,0))
lcd.display(img)

while True:
    time.sleep(1)
