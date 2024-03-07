from maix import image, display
import numpy as np

screen = display.Display()

a = np.zeros((240, 320, 3), dtype=np.uint8)
img = image.cv2image(a, bgr = True, copy = False)
img_new = image.cv2image(a)
img_cv = image.image2cv(img, copy = False)
print("image.Image object:", img.size(), img.format(), type(img))
print("convert back cv2 object:", img_cv.shape, img_cv.dtype, type(img_cv))


t = img.to_tensor(copy = False)
print("tensor.Tensor object:", t.shape(), t.dtype(), type(t))


print("\nload image from file")
img = image.load("assets/sipeed_splash.jpeg")
print("image.Image object:", img.size(), img.format(), type(img))
print("copy image")
img2 = img.copy()
print("crop image")
img2 = img.crop(100, 150, 200, 200)
img2.save("out/crop.jpg")
print("resize image")
img2 = img.resize(100, 100)
print("rotate image")
img2 = img.rotate(90)
print("img2 size:", img2.size())
print(img2.save("out/rotate.jpg"))
img2 = img.rotate(45)
print(img2.save("out/rotate2.jpg"))
img2 = img.rotate(45, 300, 200)
print(img2.save("out/rotate3.jpg"))
print("affine image")
new_w = 300
new_h = int(new_w / img.width() * img.height())
img3 = img.affine([0, 0, img.width(), img.height(), 0, img.height()], [0, 0, int((img.width() - 20)/img.width() * new_w), int((img.height() - 60)/img.height() * new_h), 0, new_h], new_w, new_h)
print("save jpg image")
print(img3.save("out/out.jpg", quality = 95))
print("save png image")
print(img3.save("out/out.png"))
