from maix import video, time, image, camera, display, app

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
disp = display.Display()
e = video.Encoder('/root/output.mp4')

record_ms = 2000
start_ms = time.ticks_ms()
while not app.need_exit():
    img = cam.read()
    e.encode(img)
    disp.show(img)

    if time.ticks_ms() - start_ms > record_ms:
        app.set_exit_flag(True)
