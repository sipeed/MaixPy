from maix import camera, display, time, app

cam = camera.Camera(512, 320)   # Manually set resolution, default is too large
disp = display.Display()        # MaixCAM default is 552x368

while not app.need_exit():
    t = time.time_ms()
    img = cam.read()             # Max FPS is determined by the camera hardware and driver settings
    disp.show(img)
    print(f"time: {time.time_ms() - t}ms, fps: {1000 / (time.time_ms() - t)}")

