from maix import camera, display, image, nn, app

detect_conf_th = 0.5
detect_iou_th = 0.45
emotion_conf_th = 0.5
max_face_num = -1
crop_scale = 0.9

# detect face model
detector = nn.YOLOv8(model="/root/models/yolov8n_face.mud", dual_buff = False)
# we only use one of it's function to crop face from image, wo we not init model actually
landmarks_detector = nn.FaceLandmarks(model="")
# emotion classify model
classifier = nn.Classifier(model="/root/models/face_emotion.mud", dual_buff=False)

cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

# for draw result info
max_labels_length = 0
for label in classifier.labels:
    size = image.string_size(label)
    if size.width() > max_labels_length:
        max_labels_length = size.width()

max_score_length = cam.width() / 4

while not app.need_exit():
    img = cam.read()
    results = []
    objs = detector.detect(img, conf_th = detect_conf_th, iou_th = detect_iou_th, sort = 1)
    count = 0
    idxes = []
    img_std_first : image.Image = None
    for i, obj in enumerate(objs):
        img_std = landmarks_detector.crop_image(img, obj.x, obj.y, obj.w, obj.h, obj.points,
                                            classifier.input_width(), classifier.input_height(), crop_scale)
        if img_std:
            img_std_gray = img_std.to_format(image.Format.FMT_GRAYSCALE)
            res = classifier.classify(img_std_gray, softmax=True)
            results.append(res)
            idxes.append(i)
            if i == 0:
                img_std_first = img_std
            count += 1
            if max_face_num > 0 and count >= max_face_num:
                break
    for i, res in enumerate(results):
        # draw fisrt face detailed info
        if i == 0:
            img.draw_image(0, 0, img_std_first)
            for j in range(len(classifier.labels)):
                idx = res[j][0]
                score = res[j][1]
                img.draw_string(0, img_std_first.height() + idx * 16, classifier.labels[idx], image.COLOR_WHITE)
                img.draw_rect(max_labels_length, int(img_std_first.height() + idx * 16), int(score * max_score_length), 8, image.COLOR_GREEN if score >= emotion_conf_th else image.COLOR_RED, -1)
                img.draw_string(int(max_labels_length + score * max_score_length + 2), int(img_std_first.height() + idx * 16), f"{score:.1f}", image.COLOR_RED)
        # draw on all face
        color = image.COLOR_GREEN if res[0][1] >= emotion_conf_th else image.COLOR_RED
        obj = objs[idxes[i]]
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color, 1)
        img.draw_string(obj.x, obj.y, f"{classifier.labels[res[0][0]]}: {res[0][1]:.1f}", color)
    disp.show(img)

