from maix import camera, display, image, nn, app

classifier = nn.Classifier(model="/root/models/mobilenetv2.mud")

cam = camera.Camera(classifier.input_width(), classifier.input_height(), classifier.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    res = classifier.classify(img)
    max_idx, max_prob = res[0]
    msg = f"{max_prob:5.2f}: {classifier.labels[max_idx]}"
    img.draw_string(10, 10, msg, image.COLOR_RED)
    img = img.resize(disp.width(), disp.height(), image.Fit.FIT_CONTAIN)
    disp.show(img)
