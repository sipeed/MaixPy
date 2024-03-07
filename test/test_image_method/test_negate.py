from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

# 2. Flip all pixels value
img = src_img.copy()
img.negate()
img.save("out/out_negate.jpg")