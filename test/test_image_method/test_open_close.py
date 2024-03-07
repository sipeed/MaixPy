from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image open
img = src_img.copy()
img.open(2, threshold = 8)
img.save("out/out_open.jpg")

# 3. image open
img = src_img.copy()
img.open(2, threshold = 8, mask = mask_img)
img.save("out/out_open_threshold_mask.jpg")

# 4. image close
img = src_img.copy()
img.close(2)
img.save("out/out_close.jpg")

# 5. image close with mask
img = src_img.copy()
img.close(2, threshold = 0, mask = mask_img)
img.save("out/out_close_threshold_mask.jpg")
