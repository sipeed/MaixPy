from maix import display, app, time, ext_dev

disp = display.Display()

tof = ext_dev.tof100.Tof100(
    4,
    ext_dev.tof100.Resolution.RES_50x50,
    ext_dev.cmap.Cmap.JET,
    40, 1000)

while not app.need_exit():
    img = tof.image()
    if img is not None:
        disp.show(img)
        print("min: ", tof.min_dis_point())
        print("max: ", tof.max_dis_point())
        print("center: ", tof.center_point())
        fps = time.fps()
        print(f"time: {1000/fps:.02f}ms, fps: {fps:.02f}")