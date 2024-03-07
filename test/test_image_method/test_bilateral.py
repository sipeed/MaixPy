from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image bilateral
img = src_img.copy()
img.bilateral(2, color_sigma = 0.1, space_sigma = 1)
img.save("out/out_bilateral.jpg")

# 3. image bilateral with mask
img = src_img.copy()
img.bilateral(2, color_sigma = 0.1, space_sigma = 1, mask = mask_img)
img.save("out/out_bilateral_mask.jpg")

# 4. image bilateral with offset
img = src_img.copy()
img.bilateral(2, threshold = True, offset = 20)
img.save("out/out_bilateral_offset.jpg")

# 5. image bilateral with offset and invert
img = src_img.copy()
img.bilateral(2, threshold = True, offset = 20, invert = True)
img.save("out/out_bilateral_offset_invert.jpg")
