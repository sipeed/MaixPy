from maix import camera, display, time, app, rtmp, image, touchscreen, audio

font_size = 16
image.load_font("font", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = font_size)
image.set_default_font("font")

# cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
cam = None
disp = display.Display()
audio_recorder = audio.Recorder()
ts = touchscreen.TouchScreen()
rtmp_client = None

str_height_1 = image.string_size('font', 1).height()
str_height_2 = image.string_size('font', 2).height()
str_height_1_5 = image.string_size('font', 1.5).height()
str_find_not_url = 'Click icon to start scan'
str_rtmp_is_running1 = 'rtmp live running'
str_rtmp_is_running2 = 'rtmp live running .'
str_rtmp_is_running3 = 'rtmp live running . .'
str_btn_tips = 'touch to scan qrcode'
str_no_url_tips1 = 'Get RTMP server address from live platforms'
str_no_url_tips2 = 'Generate QRCode with server address'
str_scan_tips1 = '1. Get RTMP server addr from live platform'
str_scan_tips2 = ' format like rtmp://xxx.com/app/stream'
str_scan_tips3 = '2. Generate QRCode with server addr, scan'

img_exit = image.load("./assets/exit.jpg").resize(50, 50)
img_exit_touch = image.load("./assets/exit_touch.jpg").resize(50, 50)
img_scan = image.load("./assets/scan.png")
img_start = image.load("./assets/start.png").resize(120, 120)
img_running = image.load("./assets/running.png")

global_status = 0  # 0, do nothing 1, scan qrcode 2, init rtmp 3, run rtmp
# global_url = 'rtmp://192.168.0.30/live/live'
global_url = ''
global_host = ''
global_port = 0
global_application = ''
global_stream = ''
global_bitrate = 1000 * 1000
global_err_msg = ''
base_img = image.Image(disp.width(), disp.height())

run_last_ms = time.ticks_ms()
run_cnt = 0
def touch_box(t, box, oft = 0):
    if t[2] and t[0] + oft > box[0] and t[0] < box[0] + box[2] + oft and t[1] + oft > box[1] and t[1] < box[1] + box[3] + oft:
        return True
    else:
        return False

def parse_url(url):
    host = ''
    port = 0
    application = ''
    stream = ''
    res1 = url.split('//')
    if len(res1) < 2:
        print('parse url failed: {}'.format(url))
        return (False, host, port, application, stream)
    res2 = res1[1].split('/')
    if len(res2) < 3:
        print('parse url failed: {}'.format(url))
        return (False, host, port, application, stream)

    res3 = res2[0].split(':')
    if len(res3) == 1:
        host = res3[0]
        port = 1935
    elif len(res3) == 2:
        host = res3[0]
        port = int(res3[1])
    else:
        print('parse url failed: {}'.format(url))
        return (False, host, port, application, stream)

    application = res2[1]
    stream = res2[2]
    return (True, host, port, application, stream)

while not app.need_exit():
    t = ts.read()

    if global_status == 0:
        base_img.draw_rect(0, 0, base_img.width(), base_img.height(), image.COLOR_BLACK, -1)
        scan_qrcode = False
        need_exit = False
        run_rtmp = False

        if len(global_err_msg):
            base_img.draw_string(base_img.width()//2 - image.string_size(global_err_msg, 2).width()//2, 50, global_err_msg, image.COLOR_RED, 2)

        if len(global_url) == 0:
            color = image.Color.from_rgb(0x6e, 0x6e, 0x6e)
            base_img.draw_string(base_img.width()//2 - image.string_size(str_no_url_tips1, 1.5).width()//2,  img_exit.height() + 15 , str_no_url_tips1, color, 1.5)
            base_img.draw_string(base_img.width()//2 - image.string_size(str_no_url_tips2, 1.5).width()//2,  img_exit.height() + 15 + str_height_2 + 10, str_no_url_tips2, color, 1.5)
            box = [base_img.width()//2-img_scan.width()//2, base_img.height()//2-50, 100, 100]
            if touch_box(t, box):
                base_img.draw_image(box[0], box[1], img_scan)
                scan_qrcode = True
            else:
                base_img.draw_image(box[0], box[1], img_scan)

            base_img.draw_string(base_img.width()//2 - image.string_size(str_find_not_url, 2).width()//2, int(base_img.height() * 0.75), str_find_not_url, color, 2)
        else:
            color = image.Color.from_rgb(0x6e, 0x6e, 0x6e)
            box = [base_img.width()//2-int(img_scan.width() * 1.25), base_img.height()//2-90, 100, 100]
            if touch_box(t, box):
                base_img.draw_image(box[0], box[1], img_scan)
                scan_qrcode = True
            else:
                base_img.draw_image(box[0], box[1], img_scan)

            base_img.draw_string(box[0] + img_scan.width()//4, box[1] + img_scan.height() + 10, "Scan", color, 2)

            box = [base_img.width()//2+int(img_scan.width() * 0.25), base_img.height()//2-90, 100, 100]
            if touch_box(t, box):
                base_img.draw_image(box[0], box[1], img_start)
                run_rtmp = True
            else:
                base_img.draw_image(box[0], box[1], img_start)

            base_img.draw_string(box[0] + img_scan.width()//4, box[1] + img_scan.height() + 10, "Run", color, 2)

            url_x = 0
            if base_img.width() > image.string_size(global_url).width():
                url_x = base_img.width()//2 - image.string_size(global_url).width()//2
            base_img.draw_string(0, int(base_img.height() * 0.70), "URL:", color, 2)
            base_img.draw_string(url_x, int(base_img.height() * 0.70) + str_height_2 + 10, global_url, color)

        box = [20, 15, img_exit.width(), img_exit.height()]
        if touch_box(t, box, 20):
            base_img.draw_image(box[0], box[1], img_exit_touch)
            need_exit = True
        else:
            base_img.draw_image(box[0], box[1], img_exit)

        disp.show(base_img)

        if scan_qrcode:
            global_status = 1
            global_err_msg = ''
        if run_rtmp:
            global_status = 2
            global_err_msg = ''
        if need_exit:
            app.set_exit_flag(True)
    elif global_status == 1:
        try:
            if cam is None or cam.format() != image.Format.FMT_RGB888:
                if cam is not None:
                    del cam
                    cam = None
                cam = camera.Camera(640, 480, image.Format.FMT_RGB888)
            img = cam.read()
            qrcodes = img.find_qrcodes()
            for q in qrcodes:
                url = q.payload()
                print('qrcode res:{}'.format(url))
                global_url = url
                global_status = 0


            need_exit = False
            box = [20, 20, img_exit.width(), img_exit.height()]
            if touch_box(t, box, 20):
                img.draw_image(box[0], box[1], img_exit_touch)
                need_exit = True
            else:
                img.draw_image(box[0], box[1], img_exit)

            img.draw_string(0, int(img.height() - (str_height_2 * 3 + 3 * 4)), str_scan_tips1, image.Color.from_rgb(0x6e, 0x6e, 0x6e), 2)
            img.draw_string(0, int(img.height() - (str_height_2 * 3 + 3 * 4)) + str_height_2 + 4, str_scan_tips2, image.Color.from_rgb(0x6e, 0x6e, 0x6e), 2)
            img.draw_string(0, int(img.height()  - (str_height_2 * 3 + 3 * 4)) + str_height_2 * 2 + 4*2, str_scan_tips3, image.Color.from_rgb(0x6e, 0x6e, 0x6e), 2)
            disp.show(img)
            del cam
            cam = None
            if need_exit:
                global_status = 0
        except Exception as e:
            global_status = 0
            global_err_msg = 'scan qrcode failed'

    elif global_status == 2:
        try:
            (res, global_host, global_port, global_application, global_stream) = parse_url(global_url)
            if res is True:
                print('parse out: {} {} {} {}'.format(global_host, global_port, global_application, global_stream))
                if cam is None or cam.format() != image.Format.FMT_YVU420SP:
                    if cam is not None:
                        del cam
                        cam = None
                    cam = camera.Camera(640, 480, image.Format.FMT_YVU420SP)
                rtmp_client = rtmp.Rtmp(global_host, global_port, global_application, global_stream, global_bitrate)
                rtmp_client.bind_audio_recorder(audio_recorder)
                rtmp_client.bind_camera(cam)
                rtmp_client.start()
                global_status = 3
            else:
                global_status = 0
                global_err_msg = 'bad url'
        except Exception as e:
            global_status = 0
            global_err_msg = 'rtmp init failed'
    elif global_status == 3:
        base_img.draw_rect(0, 0, base_img.width(), base_img.height(), image.COLOR_BLACK, -1)
        box = [base_img.width()//2-img_scan.width()//2, base_img.height()//2-70, 100, 100]
        if touch_box(t, box):
            base_img.draw_image(box[0], box[1], img_running)
            scan_qrcode = True
        else:
            base_img.draw_image(box[0], box[1], img_running)

        curr_ms = time.ticks_ms()
        if curr_ms - run_last_ms > 500:
            run_last_ms = curr_ms
            if run_cnt == 2:
                run_cnt = 0
            else:
                run_cnt += 1
    
        str_rtmp_is_running_x = base_img.width() // 2 - image.string_size(str_rtmp_is_running1, 2).width()//2
        color = image.Color.from_rgb(0x6e, 0x6e, 0x6e)
        if run_cnt == 0:
            base_img.draw_string(str_rtmp_is_running_x, int(base_img.height() * 0.7), str_rtmp_is_running1, color, 2)
        elif run_cnt == 1:
            base_img.draw_string(str_rtmp_is_running_x, int(base_img.height() * 0.7), str_rtmp_is_running2, color, 2)
        else:
            base_img.draw_string(str_rtmp_is_running_x, int(base_img.height() * 0.7), str_rtmp_is_running3, color, 2)
        
        need_exit = False
        box = [20, 15, img_exit.width(), img_exit.height()]
        if touch_box(t, box, 20):
            base_img.draw_image(box[0], box[1], img_exit_touch)
            need_exit = True
        else:
            base_img.draw_image(box[0], box[1], img_exit)

        disp.show(base_img)

        if need_exit:
            global_status = 0
            rtmp_client.stop()
            del rtmp_client
            rtmp_client = None
            global_status = 0
            time.sleep_ms(100)
    else:
        print('unknown status {}'.format(global_status))
        time.sleep_ms(1000)