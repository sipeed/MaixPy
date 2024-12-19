from maix import camera, display, app, time, uvc
import time
import atexit

cam = camera.Camera(640, 360, fps=60)   # Manually set resolution
                                # | 手动设置分辨率
# disp = display.Display()        # MaixCAM default is 522x368
                                # | MaixCAM 默认是 522x368
def fill_mjpg_img_cb(buf, size):
    img = cam.read()
    return uvc.helper_fill_mjpg_image(buf, size, img)

uvcs = uvc.UvcServer(fill_mjpg_img_cb)

uvcs.run()

while not app.need_exit():
   time.sleep(1)

# fixme: actually can't reach here, :(
# uvcs.stop()
