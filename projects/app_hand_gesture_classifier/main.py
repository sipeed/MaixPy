from maix import camera, display, image, nn, app, time, touchscreen

detector = nn.HandLandmarks(model="/root/models/hand_landmarks.mud")
# detector = nn.HandLandmarks(model="/root/models/hand_landmarks_bf16.mud")
landmarks_rel = False

cam = camera.Camera(320, 224, detector.input_format())
disp = display.Display()

ts = touchscreen.TouchScreen()

# Loading screen
img = cam.read()
img.draw_string(100, 112, "Loading...\nwait up to 10s", color = image.COLOR_GREEN)
disp.show(img)


# Train LinearSVC
import numpy as np

from LinearSVC import LinearSVC, LinearSVCManager

from contextlib import contextmanager
@contextmanager
def timer(name):
    import time
    result = {'passed': 0.}  # 使用字典存储结果
    start = time.time()
    yield result
    end = time.time()
    passed = end - start
    result['passed'] = passed
    print(f"{name} 耗时: {passed:.6f} 秒")

print("hello")
name_classes = ("one", "five", "fist", "ok", "heartSingle", "yearh", "three", "four", "six", "Iloveyou", "gun", "thumbUp", "nine", "pink")
last_train_time = 0

npzfile = np.load("trainSets.npz")
X_train = npzfile["X"]
y_train = npzfile["y"]
assert(len(X_train) == len(y_train))
print(f"X_train_len: {len(X_train)}")

# print(f"X_train: {X_train[0]}")
# print(f"y_train: {y_train[0]}")

if 1:
    with timer("加载") as r:
        clfm = LinearSVCManager(LinearSVC.load("clf_dump.npz"), X_train, y_train, pretrained=True)
    last_train_time = r['passed']
else:
    # 创建掩码（mask）
    mask_lt_4 = y_train < 4   # 小于 4 的掩码
    mask_ge_4 = y_train >= 4  # 大于等于 4 的掩码
    with timer("训练前半部分") as r:
        clfm = LinearSVCManager(LinearSVC(C=1.0, learning_rate=0.01, max_iter=100), X_train[mask_lt_4], y_train[mask_lt_4])
    last_train_time = r['passed']
    # with timer("训练后半部分") as r:
    #     clfm.add(X_train[mask_ge_4], y_train[mask_ge_4])
    # last_train_time = r['passed']

# print(f"_W: {clfm.clf._W[0]}")
# print(f"_b: {clfm.clf._B}")

with timer("回归"):
    labels, confs = clfm.test(clfm.samples[0])
    recall_count = len(clfm.samples[1])
    right_count = np.sum(labels == clfm.samples[1])
    print(f"right/all= {right_count}/{recall_count}, acc: {right_count/recall_count}")
# clfm.clf.save("maix_clf_dump.npz")

print(type(clfm.clf))
# clf1 = LinearSVC.load("clf_dump.npz")
# print(f"{clfm.clf._W-clf1._W}, {clfm.clf._B-clf1._B}")

def preprocess(hand_landmarks, is_left=False, boundary=(1,1,1)):
    hand_landmarks = np.array(hand_landmarks).reshape((21, -1))
    vector = hand_landmarks[:,:2]
    vector = vector[1:] - vector[0]
    vector = vector.astype('float64') / boundary[:vector.shape[1]]
    if not is_left: # mirror
        vector[:,0] *= -1
    return vector




# main loop
class_nums_changing = False
while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th = 0.7, iou_th = 0.45, conf_th2 = 0.8, landmarks_rel = landmarks_rel)
    for obj in objs:
        time_start = time.time_us()
        hand_landmarks = preprocess(obj.points[8:8+21*3], obj.class_id == 0, (img.width(), img.height(), 1))
        features = np.array([hand_landmarks.flatten()])
        class_idx, pred_conf = clfm.test(features)  # 获取预测类别
        time_predict = time.time_us()
        class_idx, pred_conf = class_idx[0], pred_conf[0]

        # img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = image.COLOR_RED)
        msg = f'{detector.labels[obj.class_id]}: {obj.score:.2f}\n{name_classes[class_idx]}({class_idx})={pred_conf*100:.2f}%\n{time_predict-time_start}us'
        img.draw_string(obj.points[0], obj.points[1], msg, color = image.COLOR_RED if obj.class_id == 0 else image.COLOR_GREEN, scale = 1.4, thickness = 2)
        detector.draw_hand(img, obj.class_id, obj.points, 4, 10, box=True)
        if landmarks_rel:
            img.draw_rect(0, 0, detector.input_width(detect=False), detector.input_height(detect=False), color = image.COLOR_YELLOW)
            for i in range(21):
                x = obj.points[8 + 21*3 + i * 2]
                y = obj.points[8 + 21*3 + i * 2 + 1]
                img.draw_circle(x, y, 3, color = image.COLOR_YELLOW)


    current_n_classes = len(clfm.clf.classes)

    get_color = lambda n: image.COLOR_GREEN if current_n_classes == n else image.COLOR_RED
    img.draw_circle(300, 20, 30, color = get_color(14))
    img.draw_string(300-22, 20-18, "class 14", color = get_color(14))
    img.draw_circle(300, 224-1-20, 30, color = get_color(4))
    img.draw_string(300-22, 224-1-20-18, "class 4", color = get_color(4))
    x, y = 0, 0
    x, y, preesed = ts.read()
    x = int(x / disp.width() * img.width())
    y = int(y / disp.height() * img.height())
    if x >= 300-30:
        # if preesed:
        #     print(f"x, y = {x}, {y}, {preesed}")
        if y <= 20+30:
            if preesed:
                if not class_nums_changing and current_n_classes == 4:
                    class_nums_changing = True
                if class_nums_changing:
                    img.draw_string(30, 112, "Release to upgrade to class 14\n and please wait for Training be done.", color = image.COLOR_RED)
            else:
                if class_nums_changing:
                    class_nums_changing = False
                    with timer("训练后半部分") as r:
                        mask_lt_4 = y_train < 4   # 小于 4 的掩码
                        mask_ge_4 = y_train >= 4  # 大于等于 4 的掩码
                        clfm.add(X_train[mask_ge_4], y_train[mask_ge_4])
                    last_train_time = r['passed']
                    print("success changed to 14")
        elif y >= 224-1-20-30:
            if preesed:
                if not class_nums_changing and current_n_classes == 14:
                    class_nums_changing = True
                if class_nums_changing:
                    img.draw_string(30, 112, "Release to retrain to class 4\n and please wait for Training be done.", color = image.COLOR_RED)
            else:
                if class_nums_changing:
                    class_nums_changing = False
                    with timer("移除后半部分") as r:
                        mask_lt_4 = y_train < 4   # 小于 4 的掩码
                        mask_ge_4 = clfm.samples[1] >= 4  # 大于等于 4 的掩码
                        indices_ge_4 = np.where(mask_ge_4)[0]
                        clfm.rm(indices_ge_4)
                        # clfm = LinearSVCManager(LinearSVC(C=1.0, learning_rate=0.01, max_iter=100), X_train[mask_lt_4], y_train[mask_lt_4])
                    last_train_time = r['passed']
                    print("success changed to 4")
        elif preesed:
            img.draw_string(30, 112, "Press Red circle to make it\n Green(active).", color = image.COLOR_RED)

            img.draw_string(0, 0, f'last_train_time= {last_train_time:.6f}s', color = image.COLOR_GREEN)
    elif preesed:
        img.draw_string(30, 112, "Press Red circle to make it\n Green(active).", color = image.COLOR_RED)

        img.draw_string(0, 0, ','.join(name_classes[:4]), color = image.COLOR_GREEN)
        img.draw_string(0, 20, '\n'.join(name_classes[4:]), color = image.COLOR_YELLOW if current_n_classes == 4 else image.COLOR_GREEN)
    disp.show(img)
