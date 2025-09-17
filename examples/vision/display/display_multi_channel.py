from maix import camera, display, app, time, image
import threading
from datetime import datetime

fps_main = 0

def check_pos(dir, value, range, speed):
    edge = False
    if dir == 0:
        value += speed
        if value > range[1]:
            value = range[1]
            dir = 1
            edge = True
    else:
        value -= speed
        if value < range[0]:
            value = range[0]
            dir = 0
            edge = True
    return dir, value, edge

def ui_thread(disp_ui : display.Display):
    x = 0
    y = disp_ui.height() // 2
    r = 5
    dir = [0, 0, 0]
    fps_obj = time.FPS(20)
    speed_fast = 10
    speed = speed_fast
    last_t = time.ticks_ms()
    while not app.need_exit():
        # draw info and animation
        fps = int(fps_obj.fps())
        img = image.Image(disp_ui.width(), disp_ui.height(), disp_ui.format(), bg=image.Color.from_rgba(0, 0, 0, 0))
        img.draw_circle(x, y, r, image.COLOR_WHITE, -1)
        time_now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        img.draw_string(10, 10, time_now_str, image.COLOR_RED, 2, -4)
        img.draw_string(10, 10, time_now_str, image.COLOR_WHITE, 2, -2)
        img.draw_string(10, 60, f"ui: {fps}fps, main: {fps_main}fps", image.COLOR_RED, 2, -4)
        img.draw_string(10, 60, f"ui: {fps}fps, main: {fps_main}fps", image.COLOR_WHITE, 2, -2)

        # show
        disp_ui.show(img)

        # change circle position and size
        dir[0], x, edge1 = check_pos(dir[0], x, [r, img.width() - r], speed)
        dir[1], y, edge2 = check_pos(dir[1], y, [r, img.height() - r], speed)
        dir[2], r, edge3 = check_pos(dir[2], r, [5, img.height() // 4], 1)
        if time.ticks_ms() - last_t > 50:
            speed = max(1, speed - 1)
            last_t = time.ticks_ms()
        if edge1 or edge2:
            speed = speed_fast


disp = display.Display()
cam = camera.Camera(disp.width(), disp.height(), image.Format.FMT_YVU420SP)

disp_ui = disp.add_channel()
# disp_ui = display.Display(device="/dev/fb0") # must init main display first to enable fb

th = threading.Thread(target=ui_thread, args=(disp_ui,))
th.daemon = True
th.start()

while not app.need_exit():
    img = cam.read(block=False)
    if img is not None:
        fps_main = int(time.fps())
        disp.show(img)
    time.sleep_ms(10) # release for ui thread faster



