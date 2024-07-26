from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")

# 2. calculate gamma
img = src_img.copy()
img.gamma(gamma = 0.5, contrast = 1.0, brightness = 0.0)
img.save("out/out_gamma.jpg")

# 3. calculate gamma_corr
img = src_img.copy()
img.gamma_corr(gamma = 0.5, contrast = 1.0, brightness = 0.0)
img.save("out/out_gamma_corr.jpg")
