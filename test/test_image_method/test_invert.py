from maix import image

# 1. load image
img = image.load("assets/sipeed_splash.jpeg")

# 2. invert the image
new_img = img.invert()
new_img.save("out/out_invert.jpg")
