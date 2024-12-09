from maix import app, rtsp, camera, image, display, touchscreen, time, audio

# init display
disp = display.Display()
ts = touchscreen.TouchScreen()

# init camera
cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
cam2 = cam.add_channel(disp.width(), disp.height())

# init audio
audio_recorder = audio.Recorder()

# init rtsp server
server = rtsp.Rtsp()
server.bind_camera(cam)
server.bind_audio_recorder(audio_recorder)
server.start()
urls = server.get_urls()
print(server.get_urls())

img_exit = image.load("./assets/exit.jpg").resize(50, 50)
img_exit_touch = image.load("./assets/exit_touch.jpg").resize(50, 50)
img_eye_open = image.load("./assets/img_eye_open.png").resize(50, 50)
img_eye_close = image.load("./assets/img_eye_close.png").resize(50, 50)
img_eye_last_change = time.ticks_ms()

def touch_box(t, box, oft = 0):
    if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
        return True
    else:
        return False

need_exit = False
show_urls = False
while not app.need_exit():
    img = None
    try:
        img = cam2.read()
    except:
        time.sleep_ms(10)
        continue

    t = ts.read()

    box = [20, 15, img_exit.width(), img_exit.height()]
    if touch_box(t, box, 20):
        img.draw_image(box[0], box[1], img_exit_touch)
        need_exit = True
    else:
        img.draw_image(box[0], box[1], img_exit)

    box = [img.width() - img_eye_open.width() - 20, 15, img_eye_open.width(), img_eye_open.height()]
    if touch_box(t, box, 20) and time.ticks_ms() - img_eye_last_change > 200:
        img_eye_last_change = time.ticks_ms()
        show_urls = not show_urls

    if show_urls:
        img.draw_image(box[0], box[1], img_eye_open)
        for i, url in enumerate(urls):
            img.draw_string(100, i * 20 + 50, url)
    else:
        img.draw_image(box[0], box[1], img_eye_close)

    disp.show(img)

    if need_exit:
        break