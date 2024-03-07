from maix import image

# 1. load image
src_img = image.load("/home/sipeed/sipeed/maix_group/MaixCDK/examples/image_method/assets/test_640x480.png")
src_img.binary([[20, 80]])
mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. image top_hat
img = src_img.copy()
img.top_hat(2)
img.save("out/out_top_hat.jpg")

# 3. image top_hat
img = src_img.copy()
img.top_hat(2, threshold = 0, mask = mask_img)
img.save("out/out_top_hat_threshold_mask.jpg")

# 4. image black_hat
img = src_img.copy()
img.black_hat(2)
img.save("out/out_black_hat.jpg")

# 5. image black_hat with mask
img = src_img.copy()
img.black_hat(2, threshold = 0, mask = mask_img)
img.save("out/out_black_hat_threshold_mask.jpg")

close_img=src_img.copy()
close_img.close(2, threshold = 0, mask = mask_img)
close_img.save("out/out_close_threshold_mask.jpg")

diff_img=src_img.copy()
diff_img.difference(close_img, mask = mask_img)
diff_img.save("out/out_diff_threshold_mask.jpg")
