from maix import image, camera, display, app, time

cam = camera.Camera(512, 320)   # Manually set resolution, default is too large
disp = display.Display()        # MaixCAM default is 522x368

while 1:
    t = time.time_ms()
    img = cam.read()
    disp.show(img)
    print(f"time: {time.time_ms() - t}ms, fps: {1000 / (time.time_ms() - t)}")

