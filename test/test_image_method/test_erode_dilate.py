from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image erode
img = src_img.copy()
img.erode(2)
img.save("out/out_erode.jpg")

# 3. image erode
img = src_img.copy()
img.erode(2, threshold = 16, mask = mask_img)
img.save("out/out_erode_threshold_mask.jpg")

# 4. image dilate
img = src_img.copy()
img.dilate(2)
img.save("out/out_dilate.jpg")

# 5. image dilate with mask
img = src_img.copy()
img.dilate(2, threshold = 0, mask = mask_img)
img.save("out/out_dilate_threshold_mask.jpg")
