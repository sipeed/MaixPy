from maix import image

# 1. load image
src_img = image.load("test.jpg")
if src_img is None:
    raise Exception(f"load image {file_path} failed")

# 2. binarize the image
thresholds = ((0, 100, 20, 80, 10, 80))
img = src_img.copy()
img.binary(thresholds)
img.save("binary.jpg")
