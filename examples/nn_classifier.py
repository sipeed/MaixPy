from maix import camera, display, image, nn

classifier = nn.Classifier(model="/root/models/mobilenetv2.mud")

cam = camera.Camera(classifier.input_width(), classifier.input_height(), classifier.input_format())
dis = display.Display()

while 1:
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_text(10, 10, msg, image.COLOR_RED)
    dis.show(img)
