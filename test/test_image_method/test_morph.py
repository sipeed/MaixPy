from maix import image

size = 1
kernel = [-1, -2, -1, -2, 6, -2, -1, -2, -1]

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image morph
img = src_img.copy()
img.morph(size, kernel, mul = 1 / 8, add = 200)
img.save("out/out_morph.jpg")

# 3. image morph with mask
img = src_img.copy()
img.morph(size, kernel, mul = 1 / 8, add = 200, mask = mask_img)
img.save("out/out_morph_mask.jpg")

# 4. image morph with offset
img = src_img.copy()
img.morph(size, kernel, threshold = True, offset = 20)
img.save("out/out_morph_offset.jpg")

# 5. image morph with offset and invert
img = src_img.copy()
img.morph(size, kernel, threshold = True, offset = 20, invert = True)
img.save("out/out_morph_offset_invert.jpg")
