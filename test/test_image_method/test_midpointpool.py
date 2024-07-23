from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

# 2. calculate the mean value of each 2x2 block, and replace the original image
img = src_img.copy()
img.midpoint_pool(2, 2)
img.save("out/out_midpoint_pool.jpg")

# 3. calculate the midpoint pool value of each 2x2 block, and return a new image
# Bias affects the proportion of the maximum and minimum values, the calculation formula is: (maximum * bias + minimum * (1 - bias))
img = src_img.copy()
img.midpoint_pool(2, 2, bias = 0.2)
img.save("out/out_midpoint_pool_bias_0.2.jpg")
img = src_img.copy()
img.midpoint_pool(2, 2, bias = 0.8)
img.save("out/out_midpoint_pool_bias_0.8.jpg")

# 4. calculate the mean value of each 2x2 block, and return a new image
img = src_img.copy()
new_img = img.midpoint_pool(2, 2, copy = True)
img.save("out/out_midpoint_pool_copy_0.jpg")
new_img.save("out/out_midpoint_pool_copy_1.jpg")


