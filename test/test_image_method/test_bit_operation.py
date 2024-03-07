from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

other_img = image.Image(src_img.width(), src_img.height(), src_img.format())
other_img.draw_rect(0, 0, src_img.width(), src_img.height(), image.Color.from_rgb(200, 200, 200), -1)

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.clear()
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 4, image.COLOR_WHITE, -1)

# 2. bitwise and
img = src_img.copy()
img.b_and(other_img)
img.save("out/out_b_and.jpg")

img = src_img.copy()
img.b_and(other_img, mask = mask_img)
img.save("out/out_b_and_mask.jpg")

# 3. bitwise nand
img = src_img.copy()
img.b_nand(other_img)
img.save("out/out_b_nand.jpg")

img = src_img.copy()
img.b_nand(other_img, mask = mask_img)
img.save("out/out_b_nand_mask.jpg")

# 4. bitwise or
img = src_img.copy()
img.b_or(other_img)
img.save("out/out_b_or.jpg")

img = src_img.copy()
img.b_or(other_img, mask = mask_img)
img.save("out/out_b_or_mask.jpg")

# 5. bitwise nor
img = src_img.copy()
img.b_nor(other_img)
img.save("out/out_b_nor.jpg")

img = src_img.copy()
img.b_nor(other_img, mask = mask_img)
img.save("out/out_b_nor_mask.jpg")

# 6. bitwise xor
img = src_img.copy()
img.b_xor(other_img)
img.save("out/out_b_xor.jpg")

img = src_img.copy()
img.b_xor(other_img, mask = mask_img)
img.save("out/out_b_xor_mask.jpg")

# 7. bitwise xnor
img = src_img.copy()
img.b_xnor(other_img)
img.save("out/out_b_xnor.jpg")

img = src_img.copy()
img.b_xnor(other_img, mask = mask_img)
img.save("out/out_b_xnor_mask.jpg")
