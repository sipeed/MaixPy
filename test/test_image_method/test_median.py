from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image median
img = src_img.copy()
img.median(2)
img.save("out/out_median.jpg")

# 3. image median with mask
img = src_img.copy()
img.median(2, percentile = 0.5, mask = mask_img)
img.save("out/out_median_mask.jpg")

# 4. image median with offset
img = src_img.copy()
img.median(2, threshold = True, offset = 20)
img.save("out/out_median_offset.jpg")

# 5. image median with offset and invert
img = src_img.copy()
img.median(2, threshold = True, offset = 20, invert = True)
img.save("out/out_median_offset_invert.jpg")
