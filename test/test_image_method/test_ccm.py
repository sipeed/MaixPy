from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

# 2. calculate ccm
matrix = [
    0.4, 0, 0,
    0.3, 1, 0,
    0.3, 0, 1,
]
img = src_img.copy()
img.ccm(matrix)
img.save("out/out_ccm_3x3.jpg")

# 3. calculate ccm
matrix = [
    0.9, 0.3, 0,
    0, 0.4, 0,
    0, 0.3, 1,
    0.1, 0, 0
]
img = src_img.copy()
img.ccm(matrix)
img.save("out/out_ccm_3x4.jpg")