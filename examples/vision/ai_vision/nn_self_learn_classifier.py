from maix import nn, image, display, app, time

disp = display.Display()
classifier = nn.SelfLearnClassifier(model="/root/models/mobilenet_v2_no_top.mud", dual_buff = True)

class_path = [
    "/root/1.jpg",
    "/root/2.jpg",
    "/root/3.jpg"
]

samples_path = [
    "/root/sample_1.jpg",
    "/root/sample_2.jpg"
]


class_images = []
for path in class_path:
    # load image from file
    img = image.load(path)
    if img is None:
        raise Exception(f"load image {path} failed")
    class_images.append(img)
    # add new class
    classifier.add_class(img)

sample_images = []
for path in samples_path:
    # load image from file
    img = image.load(path)
    if img is None:
        raise Exception(f"load image {path} failed")
    sample_images.append(img)
    # add new class
    classifier.add_sample(img)

if len(sample_images) > 0:
    print("-- start learn")
    classifier.learn()
    print("-- learn complete")

classifier.learn()

img = image.load("/root/test.jpg")
result = classifier.classify(img)
print(f"distances: {result}")
print(f"min distance idx: {result[0][0]}, distance: {result[0][1]}")

# show result
img_show = image.Image(disp.width(), disp.height())
img = img.resize(disp.width() // 2, disp.height() // 2, image.Fit.FIT_CONTAIN)
img_show.draw_image(0, 0, img)
img_res = class_images[result[0][0]].resize(disp.width() // 2, disp.height() // 2, image.Fit.FIT_CONTAIN)
img_show.draw_image(disp.width() // 2, 0, img_res)
img_show.draw_string(2, disp.height() // 2 + 80, f"distance: {result[0][1]}", scale=1.5)
img_show.draw_string(2, disp.height() // 2 + 40, f"test.jpg", scale=1.5)
img_show.draw_string(disp.width() // 2 + 2, disp.height() // 2 + 40, class_path[result[0][0]], scale=1.5)

disp.show(img_show)


while not app.need_exit():
    time.sleep_ms(100)
