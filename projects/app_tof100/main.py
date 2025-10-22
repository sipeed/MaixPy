from maix import display, image, app, time, ext_dev

from maix import pinmap

import numpy as np
import cv2

pin_function = {
    "A8": "I2C7_SCL",
    "A9": "I2C7_SDA",
    "B21": "SPI2_CS1",
    "B19": "SPI2_MISO",
    "B18": "SPI2_MOSI",
    "B20": "SPI2_SCK"
}

for pin, func in pin_function.items():
    if 0 != pinmap.set_pin_function(pin, func):
        print(f"Failed: pin{pin}, func{func}")
        exit(-1)

disp = display.Display()

tof = ext_dev.tof100.Tof100(
    2,
    ext_dev.tof100.Resolution.RES_100x100,
    ext_dev.cmap.Cmap.JET,
    40, 1000)

t0 = time.time()
while not app.need_exit():
    img = tof.image()
    if img is not None:
        img_bgr = image.image2cv(img, ensure_bgr=True, copy=True)
        img_bgr = cv2.rotate(img_bgr, cv2.ROTATE_180)
        img_bgr = cv2.resize(img_bgr, (400, 400))

        scr = np.zeros((disp.height(), disp.width(), 3), dtype=np.uint8)
        scr[:img_bgr.shape[0], :img_bgr.shape[1], ...] = img_bgr
        disp.show(image.cv2image(scr))
        fps = time.fps()
        t1 = time.time()
        if t1-t0>1:
            print("min: ", tof.min_dis_point())
            print("max: ", tof.max_dis_point())
            print("center: ", tof.center_point())
            print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")
            print(f"t0:{t0}, t1:{t1}")
            t0=t1
