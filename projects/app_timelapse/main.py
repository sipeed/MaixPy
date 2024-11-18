from json import decoder
from maix import image, video, camera, display, app, time, touchscreen, fs
import time as time2
import os

ENABLE_PLAYER=0     # The playback function is temporarily disabled due to insufficient memory required for 1440p playback.
ENCODER_BITRATE=8000*1000

disp = display.Display()
disp2 = disp.add_channel()
ts = touchscreen.TouchScreen()
cam = camera.Camera(1280, 720, image.Format.FMT_YVU420SP)
path = ""                   # path foramt: //maixapp/share/video/%Y-%m-%d_%H%M%S.mp4
encoder = None
decoder = None
image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", 26)
image.set_default_font("sourcehansans")

img2 = image.Image(disp2.width(), disp2.height(), image.Format.FMT_BGRA8888)

start_img = image.load("./assets/start.png", image.Format.FMT_BGRA8888)
stop_img = image.load("./assets/stop.png", image.Format.FMT_BGRA8888)
playback_img = image.load("./assets/playback.png", image.Format.FMT_BGRA8888)
playback_stop_img = image.load("./assets/playback_stop.png", image.Format.FMT_BGRA8888)
exit_img = image.load("./assets/exit.jpg").resize(50, 50)
exit_touch_img = image.load("./assets/exit_touch.jpg").resize(50, 50)
record_time_img = image.Image(100, 30, image.Format.FMT_RGB888)
record_time_img.clear()
menu_img = image.Image(100, 30, image.Format.FMT_BGRA8888)
menu_img.clear()
menu_img.draw_string(0, 0, 'MENU', image.COLOR_WHITE)
menu_option_number = 7

menu_option1_img = image.Image(100, (disp2.height() - menu_img.height()) // menu_option_number)
menu_option1_img.draw_string(35, 10, "1S", image.COLOR_WHITE)
menu_option2_img = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option2_img.draw_string(35, 10, "5S", image.COLOR_WHITE)
menu_option3_img = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option3_img.draw_string(35, 10, "15S", image.COLOR_WHITE)
menu_option4_img = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option4_img.draw_string(35, 10, "30S", image.COLOR_WHITE)
menu_option5_img = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option5_img.draw_string(35, 10, "60S", image.COLOR_WHITE)

menu_option1_img_touched = image.Image(100, (disp2.height() - menu_img.height()) // menu_option_number)
menu_option1_img_touched.draw_string(35, 10, "1S", image.Color.from_rgb(0x2f,0x2f,0x2f))
menu_option2_img_touched = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option2_img_touched.draw_string(35, 10, "5S", image.Color.from_rgb(0x2f,0x2f,0x2f))
menu_option3_img_touched = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option3_img_touched.draw_string(35, 10, "15S", image.Color.from_rgb(0x2f,0x2f,0x2f))
menu_option4_img_touched = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option4_img_touched.draw_string(35, 10, "30S", image.Color.from_rgb(0x2f,0x2f,0x2f))
menu_option5_img_touched = image.Image(menu_option1_img.width(), menu_option1_img.height())
menu_option5_img_touched.draw_string(35, 10, "60S", image.Color.from_rgb(0x2f,0x2f,0x2f))
menu_touched = False
menu_touched_number = 1

RECORD_IDLE = 0
RECORD_BUSY = 1
PLAYBACK_IDLE = 0
PLAYBACK_BUSY = 1
record = RECORD_IDLE  # 0, idle; 1, start record; 
playback = PLAYBACK_IDLE  # 0, idle, 1, playback;

start_touch_record = time.ticks_ms()
last_touch_record = time.ticks_ms()
last_touch_playback = time.ticks_ms()
last_touch_menu = time.ticks_ms()

last_record_ms = time.ticks_ms()
record_step_ms = 1 * 1000          # record every 1 seconds
last_playback_ms = time.ticks_ms()

need_exit = False

def touch_box(t, box, oft = 0):
    if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
        return True
    else:
        return False

while not app.need_exit():
    t = ts.read()
    t_ms = time.ticks_ms()
    img = cam.read()
    
    # clear bash image
    img2.clear()

    # exit handle
    box = [0, 0, exit_img.width(), exit_img.height()]
    if touch_box(t, box, 20):
        img2.draw_image(box[0], box[1], exit_touch_img)
        need_exit = True
    else:
        img2.draw_image(box[0], box[1], exit_img)

    if need_exit:
        break

    # menu handle
    box = [img2.width() - menu_img.width(), 0, menu_img.width(), menu_img.height()]
    if touch_box(t, box, 20):
        img2.draw_image(box[0], box[1], menu_img)
        if time.ticks_ms() - last_touch_menu > 300:
            print('menuconfig is touched')
            menu_touched = not menu_touched
            last_touch_menu = time.ticks_ms()
    else:
        img2.draw_image(box[0], box[1], menu_img)

    if menu_touched:
        oft_x = img2.width() - menu_option1_img.width()
        oft_y = menu_img.height()
        # option 1
        box = [oft_x, oft_y, menu_option1_img.width(), menu_option1_img.height()]
        if touch_box(t, box, 0):
            menu_touched_number = 1
            record_step_ms = 1 * 1000
        if menu_touched_number == 1:
            img2.draw_image(box[0], box[1], menu_option1_img)
        else:
            img2.draw_image(box[0], box[1], menu_option1_img_touched)

        # option 2
        box[1] += menu_option1_img.height() + 5
        if touch_box(t, box, 0):
            menu_touched_number = 2
            record_step_ms = 5 * 1000
        if menu_touched_number == 2:
            img2.draw_image(box[0], box[1], menu_option2_img)
        else:
            img2.draw_image(box[0], box[1], menu_option2_img_touched)

        # option 3
        box[1] += menu_option1_img.height() + 5
        if touch_box(t, box, 0):
            menu_touched_number = 3
            record_step_ms = 15 * 1000
        if menu_touched_number == 3:
            img2.draw_image(box[0], box[1], menu_option3_img)
        else:
            img2.draw_image(box[0], box[1], menu_option3_img_touched)

        # option 4
        box[1] += menu_option1_img.height() + 5
        if touch_box(t, box, 0):
            menu_touched_number = 4
            record_step_ms = 30 * 1000
        if menu_touched_number == 4:
            img2.draw_image(box[0], box[1], menu_option4_img)
        else:
            img2.draw_image(box[0], box[1], menu_option4_img_touched)

        # option 5
        box[1] += menu_option1_img.height() + 5
        if touch_box(t, box, 0):
            menu_touched_number = 5
            record_step_ms = 60 * 1000
        if menu_touched_number == 5:
            img2.draw_image(box[0], box[1], menu_option5_img)
        else:
            img2.draw_image(box[0], box[1], menu_option5_img_touched)

    # record handle
    if ENABLE_PLAYER:
        box = [20, img2.height() // 2 - img2.height() // 4 - start_img.height() // 2, start_img.width(), start_img.height()]
    else:
        box = [20, img2.height() // 2 - start_img.height() // 2, start_img.width(), start_img.height()]    # left-center
    if touch_box(t, box, 20):
        if time.ticks_ms() - last_touch_record > 300:
            if playback == PLAYBACK_IDLE:
                record = not record
            last_touch_record = time.ticks_ms()
    
    if record:
        img2.draw_image(box[0], box[1], stop_img)
    else:
        img2.draw_image(box[0], box[1], start_img)

    # playback handle
    if ENABLE_PLAYER:
        box = [20, img2.height() // 2 + img2.height() // 2 - img2.height() // 4 - start_img.height() // 2, playback_img.width(), playback_img.height()]
        if touch_box(t, box, 20):
            if time.ticks_ms() - last_touch_playback > 300:
                if record == RECORD_IDLE:
                    playback = not playback
                last_touch_playback = time.ticks_ms()

        if playback == PLAYBACK_IDLE:
            img2.draw_image(box[0], box[1], playback_img)
        else:
            img2.draw_image(box[0], box[1], playback_stop_img)

    if record == RECORD_BUSY:
        if decoder:
            del decoder
            decoder = None
        if not encoder:
            print('start record!')
            curr_s = time.time_s()
            curr_s_str = time2.strftime("%Y%m%d%H%M%S", time2.gmtime(curr_s))
            dir = '/maixapp/share/video/'+ time2.strftime("%Y-%m-%d", time2.gmtime(curr_s)) + '/'
            os.makedirs(dir, exist_ok=True)
            path = dir + curr_s_str + '.mp4'
            print(f'save to {path}')
            encoder = video.Encoder(path, cam.width(), cam.height(), bitrate=ENCODER_BITRATE)
            start_touch_record = time.ticks_ms()
        if time.ticks_ms() - last_record_ms >= record_step_ms:
            encoder.encode(img=img)
            last_record_ms = time.ticks_ms()
            print('encode img..')

        # show record time
        curr_time = time.ticks_s() - start_touch_record // 1000
        curr_time_str = time2.strftime("%H:%M:%S", time2.gmtime(curr_time))
        record_time_img.clear()
        record_time_img.draw_string(0, 0, curr_time_str, image.COLOR_RED)
        img2.draw_image((img2.width() - record_time_img.width()) // 2, 20, record_time_img)
    else:
        if encoder:
            print('stop record')
            del encoder
            encoder = None

    if playback == PLAYBACK_BUSY:
        if encoder:
            del encoder
            encoder = None
        if not decoder:
            print('start decode!')
            if fs.exists(path):
                print('1111111', path)
                decoder = video.Decoder(path)
                print('22222222')
            else:
                print(f"{path} not found!")
        print('3333333333')
        if decoder:
            ctx = decoder.decode_video()
            if ctx:
                img = ctx.image()
                print(f'decode image:{img}')
                timebase = decoder.timebase()
                wait_ms = ctx.duration() * 1000 / timebase[0] / timebase[1]
                while time.ticks_ms() - last_playback_ms < wait_ms:
                    time.sleep_us(500)
                last_playback_ms = time.ticks_ms()
            else:
                print('decode over')
                playback = PLAYBACK_IDLE
        else:
            playback = PLAYBACK_IDLE
    else:
        if decoder:
            print('stop decode')
            del decoder
            decoder = None
        
    # flush image
    disp.show(img, fit=image.Fit.FIT_COVER)
    disp2.show(img2)
    # print(f"time: {time.ticks_ms() - t_ms}ms, fps: {1000 / (time.ticks_ms() - t_ms)}")




