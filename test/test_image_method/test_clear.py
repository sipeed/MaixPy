from maix import image

# 1. clear all of image
img = image.load("assets/sipeed_splash.jpeg")
img.clear()
img.save("out/out_clear_all.jpg")

# 2. clear image with mask
img = image.load("assets/sipeed_splash.jpeg")
mask_img = image.Image(img.width(), img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(img.width() // 4, img.height() // 4, img.width() // 2, img.height() // 4, image.COLOR_WHITE, -1)

img.clear(mask = mask_img)
img.save("out/out_clear_mask.jpg")