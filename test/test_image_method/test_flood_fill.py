from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.clear()
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. flood fill
img = src_img.copy()
img.flood_fill(200, 200, seed_threshold = 0.5, floating_threshold = 0.5, color = image.COLOR_BLUE)
img.save("out/out_flood_fill.jpg")

# 3. flood fill and invert
img = src_img.copy()
img.flood_fill(200, 200, seed_threshold = 0.5, floating_threshold = 0.5, color = image.COLOR_BLUE, invert = True)
img.save("out/out_flood_fill_invert.jpg")

# 4. flood fill and invert with mask
img = src_img.copy()
img.flood_fill(200, 200, seed_threshold = 0.5, floating_threshold = 0.5, color = image.COLOR_BLUE, clear_background = True)
img.save("out/out_flood_fill_invert_mask.jpg")