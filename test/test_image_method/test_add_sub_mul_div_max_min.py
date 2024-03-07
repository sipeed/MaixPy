from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")
other_img = image.load("assets/sipeed_splash.jpeg")
other_img.negate()

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image add
img = src_img.copy()
img.add(other = other_img, mask = mask_img)
img.save("out/out_add.jpg")

# 3. image sub
img = src_img.copy()
img.sub(other = other_img, mask = mask_img)
img.save("out/out_sub.jpg")

# 4. image mul
img = src_img.copy()
img.sub(other = other_img, mask = mask_img)
img.save("out/out_mul.jpg")

# 5. image mul and invert
img = src_img.copy()
img.mul(other = other_img, invert = True, mask = mask_img)
img.save("out/out_mul_invert.jpg")

# 6. image div
img = src_img.copy()
img.div(other = other_img, mask = mask_img)
img.save("out/out_div.jpg")

# 7. image div and invert
img = src_img.copy()
img.div(other = other_img, invert = True, mask = mask_img)
img.save("out/out_div_invert.jpg")

# 8. image mod
img = src_img.copy()
img.div(other = other_img, mod = True, mask = mask_img)
img.save("out/out_mod.jpg")

# 9.image min
img = src_img.copy()
img.min(other = other_img, mask = mask_img)
img.save("out/out_min.jpg")

# 10.image max
img = src_img.copy()
img.max(other = other_img, mask = mask_img)
img.save("out/out_max.jpg")