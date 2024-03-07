from maix import image

# 1. load image
src_img = image.load("assets/sipeed_splash.jpeg")
other_img = image.load("assets/sipeed_splash.jpeg")
other_img.negate()

mask_img = image.Image(src_img.width(), src_img.height(), image.Format.FMT_GRAYSCALE)
mask_img.draw_rect(src_img.width() // 4, src_img.height() // 4, src_img.width() // 2, src_img.height() // 2, image.COLOR_WHITE, -1)

# 2. replace and rotate 0 degress
img = src_img.copy()
img.replace(hmirror = False, vflip = False, transpose = False, mask = mask_img)
img.save("out/out_replace_0_degress.jpg")

# 3. replace and rotate 90 degress
img = src_img.copy()
img.replace(hmirror = False, vflip = True, transpose = True, mask = mask_img)
img.save("out/out_replace_90_degress.jpg")

# 4. replace and rotate 180 degress
img = src_img.copy()
img.replace(hmirror = True, vflip = True, transpose = False, mask = mask_img)
img.save("out/out_replace_180_degress.jpg")

# 5. replace and rotate 270 degress
img = src_img.copy()
img.replace(hmirror = True, vflip = False, transpose = True, mask = mask_img)
img.save("out/out_replace_270_degress.jpg")

# 6. replace other image and rotate 0 degress
img = src_img.copy()
img.replace(other = other_img, hmirror = False, vflip = False, transpose = False)
img.save("out/out_replace_other_0_degress.jpg")

# 7. replace other image and rotate 90 degress
img = src_img.copy()
img.replace(other = other_img, hmirror = False, vflip = True, transpose = True)
img.save("out/out_replace_other_90_degress.jpg")

# 8. replace other image and rotate 180 degress
img = src_img.copy()
img.replace(other = other_img, hmirror = True, vflip = True, transpose = False)
img.save("out/out_replace_other_180_degress.jpg")

# 9. replace other image and rotate 270 degress
img = src_img.copy()
img.replace(other = other_img, hmirror = True, vflip = False, transpose = True)
img.save("out/out_replace_other_270_degress.jpg")

# 10. set other image and rotate 0 degress
img = src_img.copy()
img.set(other = other_img, hmirror = True, vflip = False, transpose = True, mask = mask_img)
img.save("out/out_set_other_0_degress.jpg")
