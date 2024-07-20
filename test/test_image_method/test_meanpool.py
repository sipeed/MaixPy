from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

# 2. calculate the mean value of each 2x2 block, and replace the original image
img = src_img.copy()
img.mean_pool(2, 2)
img.save("out/out_mean_pool.jpg")

# 3. calculate the mean value of each 2x2 block, and return a new image
img = src_img.copy()
new_img = img.mean_pool(2, 2, copy = True)
img.save("out/out_mean_pool_copy_0.jpg")
new_img.save("out/out_mean_pool_copy_1.jpg")
