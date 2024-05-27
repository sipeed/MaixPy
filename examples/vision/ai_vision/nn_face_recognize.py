from maix import nn, camera, display, image, key, time
import os
import math

recognizer = nn.FaceRecognizer(detect_model="/root/models/retinaface.mud", feature_model = "/root/models/face_feature.mud")

# if os.path.exists("/root/faces.bin"):
#     recognizer.load_faces("/root/faces.bin")

cam = camera.Camera(recognizer.input_width(), recognizer.input_height(), recognizer.input_format())
dis = display.Display()

g_pressed = False

def on_key(key_id, state):
    global g_pressed
    print(f"key: {key_id}, state: {state}")
    if state == key.State.KEY_RELEASED:
        g_pressed = True

# Init key will cancel the default ok button function(exit app)
btn = key.Key(on_key)
learn_id = 0
last_learn_img = None
last_learn_t = 0

while 1:
    img = cam.read()
    learn = g_pressed
    g_pressed = False
    faces = recognizer.recognize(img, 0.5, 0.45, 0.8, learn, learn)
    for obj in faces:
        color = image.COLOR_RED if obj.class_id == 0 else image.COLOR_GREEN
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color = color)
        radius = math.ceil(obj.w / 10)
        img.draw_keypoints(obj.points, color, size = radius if radius < 5 else 4)
        msg = f'{recognizer.labels[obj.class_id]}: {obj.score:.2f}'
        img.draw_string(obj.x, obj.y, msg, color = color)
        if learn and obj.class_id == 0: # unknown face, we add it
            name = f"id_{learn_id}"
            print("add face:", name)
            recognizer.add_face(obj, name)
            learn_id += 1
        if learn:
            last_learn_img = obj.face
            last_learn_t = time.time()
    # show learned face on left-top
    if last_learn_img and time.time() - last_learn_t < 5:
        img.draw_image(0, 0, last_learn_img)
    if learn:
        recognizer.save_faces("/root/faces.bin")
    dis.show(img)


