from maix import image, display, app, time
import cv2

file_path = "/maixapp/share/icon/detector.png"
img0 = cv2.imread(file_path)

disp = display.Display()

while not app.need_exit():
    img = img0.copy()

    # canny method
    t = time.ticks_ms()
    edged = cv2.Canny(img, 180, 60)
    t2 = time.ticks_ms() - t

    # show by maix.display
    t = time.ticks_ms()
    img_show = image.cv2image(edged)
    print(f"edge time: {t2}ms, convert time: {time.ticks_ms() - t}ms")
    disp.show(img_show)


