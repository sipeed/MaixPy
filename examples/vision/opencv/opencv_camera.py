from maix import image, display, app, time, camera
import cv2

disp = display.Display()
cam = camera.Camera(320, 240)

while not app.need_exit():
    img = cam.read()

    # convert maix.image.Image object to numpy.ndarray object
    t = time.time_ms()
    img = image.image2cv(img)
    print("time: ", time.time_ms() - t)

    # canny method
    edged = cv2.Canny(img, 180, 60)

    # show by maix.display
    img_show = image.cv2image(edged)
    disp.show(img_show)


