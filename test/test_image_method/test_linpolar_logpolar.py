from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image linpolar
img = src_img.copy()
img.linpolar()
img.save("out/out_linpolar.jpg")

# 3. image linpolar reverse
img = src_img.copy()
img.linpolar(reverse = True)
img.save("out/out_linpolar_reverse.jpg")

# 2. image logpolar
img = src_img.copy()
img.logpolar()
img.save("out/out_logpolar.jpg")

# 3. image logpolar reverse
img = src_img.copy()
img.logpolar(reverse = True)
img.save("out/out_logpolar_reverse.jpg")