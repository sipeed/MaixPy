from maix import image, display, app, time, camera
import cv2

disp = display.Display()
cam = camera.Camera(320, 240, image.Format.FMT_BGR888)

while not app.need_exit():
    img = cam.read()

    # convert maix.image.Image object to numpy.ndarray object
    t = time.ticks_ms()
    img = image.image2cv(img, ensure_bgr=False, copy=False)
    print("time: ", time.ticks_ms() - t)

    # canny method
    edged = cv2.Canny(img, 180, 60)

    # show by maix.display
    img_show = image.cv2image(edged, bgr=True, copy=False)
    disp.show(img_show)


