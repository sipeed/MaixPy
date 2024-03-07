from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image laplacian
img = src_img.copy()
img.laplacian(2, mul = 1 / 8, add = 200)
img.save("out/out_laplacian.jpg")

# 3. image laplacian with mask
img = src_img.copy()
img.laplacian(2, sharpen = True, mul = 1 / 8, add = 200)
img.save("out/out_laplacian_mask.jpg")

# 4. image laplacian with mask
img = src_img.copy()
img.laplacian(2, mul = 1 / 8, add = 200, mask = mask_img)
img.save("out/out_laplacian_mask.jpg")

# 5. image laplacian with offset
img = src_img.copy()
img.laplacian(2, threshold = True, offset = 20)
img.save("out/out_laplacian_offset.jpg")

# 6. image laplacian with offset and invert
img = src_img.copy()
img.laplacian(2, threshold = True, offset = 20, invert = True)
img.save("out/out_laplacian_offset_invert.jpg")
