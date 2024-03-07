from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")
other_img = image.load("assets/sipeed_splash.jpeg")
other_img.negate()

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image histeq
img = src_img.copy()
img.histeq()
img.save("out/out_histeq.jpg")

# 3. image histeq with mask
img = src_img.copy()
img.histeq(mask = mask_img)
img.save("out/out_histeq_mask.jpg")

# 4. image histeq with adaptive
img = src_img.copy()
img.histeq(adaptive = True)
img.save("out/out_histeq_adaptive.jpg")

# 5. image histeq with adaptive and clip limit
img = src_img.copy()
img.histeq(adaptive = True, clip_limit = 10)
img.save("out/out_histeq_adaptive_clip_limit.jpg")
