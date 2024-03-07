from maix import image, display

screen = display.Display()

# 1. load image, and default convert to RGB888 format
img = image.load("assets/sipeed_splash.jpeg", format = image.Format.FMT_RGB888)

# 2. Compress image to JPEG format, quality is 95
img.compress(quality = 95)
img.save("out/out_compress.jpg")
