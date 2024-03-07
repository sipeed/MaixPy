from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")
mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. binarize the image
thresholds = ((0, 100, 20, 80, 10, 80),)
img = src_img.copy()
img.binary(thresholds)
img.save("out/out_binary.jpg")

# 3. binarize the image with invert
thresholds = ((0, 100, 20, 80, 10, 80),)
img = img = src_img.copy()
img.binary(thresholds, invert = True)
img.save("out/out_binary_invert.jpg")

# 4. binarize the image with zero
thresholds = ((0, 100, 20, 80, 10, 80),)
img = img = src_img.copy()
new_img = img.binary(thresholds, zero = True, mask = mask_img, copy = True)
img.save("out/out_binary_zero_copy_src.jpg")
new_img.save("out/out_binary_zero_copy.jpg")

