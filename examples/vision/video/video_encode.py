from maix import camera, display, time, image, app, video

cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)   # Manually set resolution, default is too large
disp = display.Display()

v = video.Video("/root/output.h265", cam.width(), cam.height(), capture = True)
v.bind_camera(cam)

record_ms = 5000
start_ms = time.ticks_ms()
while not app.need_exit():
    v.encode()
    img = v.capture()

    disp.show(img)

    if time.ticks_ms() - start_ms > record_ms:
        v.finish()
        app.set_exit_flag(True)
