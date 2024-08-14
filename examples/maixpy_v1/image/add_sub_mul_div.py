from maix.v1 import lcd, image
from maix import time

lcd.init()

img = image.Image("/maixapp/share/icon/maixvision.png")
lcd.display(img)
time.sleep(3)
img2 = image.Image("/maixapp/share/icon/maixhub.png")
lcd.display(img2)
time.sleep(3)

# add
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.add(img2)
lcd.display(img)
time.sleep(3)

# sub
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.sub(img2)
lcd.display(img)
time.sleep(3)

# mul
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.mul(img2)
lcd.display(img)
time.sleep(3)

# div
img = image.Image("/maixapp/share/icon/maixvision.png")
img2 = image.Image("/maixapp/share/icon/maixhub.png")
img.div(img2)
lcd.display(img)
time.sleep(3)
