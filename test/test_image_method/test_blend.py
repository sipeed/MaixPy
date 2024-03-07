from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")
other_img = image.load("assets/sipeed_splash.jpeg")
other_img.draw_rect(src_img.width() // 4, src_img.height() // 4, other_img.width() // 2, other_img.height() // 2, image.COLOR_BLACK, -1)

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image blend
img = src_img.copy()
img.blend(other_img, alpha = 128, mask = mask_img)
img.save("out/out_blend.jpg")