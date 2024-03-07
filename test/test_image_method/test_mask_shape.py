from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")
src_img.save("out/out_src.jpg")

# 2. zeros a rectangular part of the image
img = src_img.copy()
img.mask_rectange()
img.save("out/out_mask_rectange_default.jpg")

img = src_img.copy()
img.mask_rectange(0, 0 , img.width() // 2, img.height() // 2)
img.save("out/out_mask_rectange.jpg")

# 3. zeros a circular part of the image
img = src_img.copy()
img.mask_circle()
img.save("out/out_mask_circle_default.jpg")

img = src_img.copy()
img.mask_circle(0, 0, img.width() // 2)
img.save("out/out_mask_circle.jpg")

# 4. zeros a ellipse part of the image
img = src_img.copy()
img.mask_ellipse()
img.save("out/out_mask_ellipse_default.jpg")

img = src_img.copy()
img.mask_ellipse(0, 0 , img.width() // 2, img.height() // 2, 80)
img.save("out/out_mask_ellipse.jpg")