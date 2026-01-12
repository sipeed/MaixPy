from maix import app, webrtc, camera, image, display, touchscreen, time
import shutil, subprocess

font_size = 16
image.load_font("font", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = font_size)
image.set_default_font("font")

disp = display.Display()
ts = touchscreen.TouchScreen()

encoders = ["H.264", "H.265"]
sensor_size = camera.get_sensor_size()
bitrates = ["1 Mbps", "2 Mbps", "4 Mbps", "8 Mbps", "16 Mbps", "32 Mbps", "64 Mbps"]
if sensor_size[0] > 2560:
    resolutions = ["720 P", "1080 P", "2 K", "4 K"]
else:
    resolutions = ["720 P", "1080 P", "2 K"]

choice_encoder = 0
choice_bitrate = 0
choice_res = 0

choice_rc_type = 0
rc_types = ["CBR", "VBR"]

def in_box(t, box):
    return t[2] and box[0] <= t[0] <= box[0]+box[2] and box[1] <= t[1] <= box[1]+box[3]

def config_page():
    def tailscale_config_page():
        BG = image.Color.from_rgb(15, 15, 15)
        CARD_BG = image.Color.from_rgb(35, 35, 35)
        ACCENT = image.Color.from_rgb(0, 110, 255)
        ACCENT_P = image.Color.from_rgb(0, 80, 200)
        SUCCESS = image.Color.from_rgb(52, 199, 89)
        DANGER = image.Color.from_rgb(255, 59, 48)
        DANGER_P = image.Color.from_rgb(180, 40, 60)
        GRAY = image.Color.from_rgb(90, 90, 95)
        GRAY_P = image.Color.from_rgb(60, 60, 65)
        TXT = image.Color.from_rgb(255, 255, 255)
        WARN = image.Color.from_rgb(255, 180, 0)

        screen_w, screen_h = disp.width(), disp.height()

        pad = 15
        btn_exit = [20 - pad, 15 - pad, 52 + pad * 2, 52 + pad * 2]
        img_exit = image.load("./assets/exit.jpg").resize(52, 52)
        img_exit_p = image.load("./assets/exit_touch.jpg").resize(52, 52)

        btn_h = 52
        btn_y = screen_h - btn_h - 20
        gap = 10
        btn_w = (screen_w - 40 - (gap * 2)) // 3

        btn_on = [20, btn_y, btn_w, btn_h]
        btn_off = [20 + btn_w + gap, btn_y, btn_w, btn_h]
        btn_logout = [20 + (btn_w + gap) * 2, btn_y, btn_w, btn_h]

        def get_status():
            try:
                out = subprocess.check_output(["tailscale", "status"], universal_newlines=True, timeout=1)
                running = "stopped" not in out.lower()
                ip = subprocess.check_output(["tailscale", "ip"], universal_newlines=True, timeout=1).strip().split("\n")[0] if running else "-"
                return running, ip
            except: return False, "-"

        login_url = None
        is_busy = False

        while not app.need_exit():
            img = image.Image(screen_w, screen_h, image.Format.FMT_RGB888)
            img.draw_rect(0, 0, screen_w, screen_h, BG, thickness=-1)

            running, ip = get_status()
            if running and login_url:
                login_url = None
            t = ts.read()

            exit_img = img_exit_p if in_box(t, btn_exit) else img_exit
            img.draw_image(btn_exit[0], btn_exit[1], exit_img)
            img.draw_string(85, 28, "Tailscale", color=TXT, scale=1.8)

            card_x, card_y = 20, 85
            card_w, card_h = screen_w - 40, 120
            img.draw_rect(card_x, card_y, card_w, card_h, CARD_BG, thickness=-1)

            status_text = "ONLINE" if running else "OFFLINE"
            status_col = SUCCESS if running else DANGER

            img.draw_circle(card_x + 30, card_y + 35, 9, status_col, thickness=-1)
            img.draw_string(card_x + 55, card_y + 20, status_text, color=status_col, scale=2.5)
            img.draw_string(card_x + 30, card_y + 80, f"IP Address: {ip}", color=image.Color.from_rgb(200, 200, 200), scale=1.6)

            if login_url:
                msg_y = card_y + card_h + 10
                box_h = 100
                img.draw_rect(card_x, msg_y, card_w, box_h, image.Color.from_rgb(35, 30, 10), thickness=-1)
                tip_scale = 1.8
                url_scale = 1.5
                tip_txt = "Please log in using a web browser:"
                tip_size = image.string_size(tip_txt, scale=tip_scale)
                url_txt = login_url.replace("https://", "")
                if len(url_txt) > 40:
                    url_txt = url_txt[:40] + "..."
                url_size = image.string_size(url_txt, scale=url_scale)
                tip_y = msg_y + 15
                url_y = tip_y + tip_size.height() + 10
                img.draw_string(card_x + (card_w - tip_size.width())//2, tip_y, tip_txt, color=WARN, scale=tip_scale)
                img.draw_string(card_x + (card_w - url_size.width())//2, url_y, url_txt, color=ACCENT, scale=url_scale)

            def draw_action_btn(box, text, color, press_color, enabled):
                if not enabled:
                    fill = image.Color.from_rgb(50, 50, 50)
                    text_col = image.Color.from_rgb(100, 100, 100)
                else:
                    is_pressed = in_box(t, box) and not is_busy
                    fill = press_color if is_pressed else color
                    text_col = TXT

                img.draw_rect(box[0], box[1], box[2], box[3], fill, thickness=-1)

                display_txt = "..." if (is_busy and in_box(t, box)) else text
                tsize = image.string_size(display_txt, scale=1.3)
                img.draw_string(box[0]+(box[2]-tsize.width())//2, box[1]+(box[3]-tsize.height())//2, display_txt, color=text_col, scale=1.3)

            draw_action_btn(btn_on, "Start", ACCENT, ACCENT_P, not running)
            draw_action_btn(btn_off, "Stop", GRAY, GRAY_P, running)
            draw_action_btn(btn_logout, "Logout", DANGER, DANGER_P, True)

            disp.show(img)

            if t[2] and not is_busy:
                if in_box(t, btn_exit):
                    break

                if in_box(t, btn_on) and not running:
                    is_busy = True
                    subprocess.call(["systemctl", "enable", "--now", "tailscaled.service"])
                    proc = subprocess.Popen(["tailscale", "up", "--accept-dns=false"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
                    for _ in range(15):
                        line = proc.stdout.readline()
                        if "https://login.tailscale.com" in line:
                            login_url = line[line.find("https://"):].strip()
                            break
                    time.sleep(1)
                    is_busy = False

                elif in_box(t, btn_off) and running:
                    is_busy = True
                    subprocess.call(["systemctl", "disable", "--now", "tailscaled.service"])
                    subprocess.Popen(["tailscale", "down"])
                    login_url = None
                    time.sleep(1.2)
                    is_busy = False

                elif in_box(t, btn_logout):
                    is_busy = True
                    subprocess.Popen(["tailscale", "logout"])
                    login_url = None
                    time.sleep(1.2)
                    is_busy = False

            time.sleep_ms(25)

    global choice_encoder, choice_bitrate, choice_res, choice_rc_type

    BG = image.Color.from_rgb(25, 25, 25)
    CARD = image.Color.from_rgb(45, 45, 45)
    BTN = image.Color.from_rgb(70, 70, 70)
    BTN_P = image.Color.from_rgb(40, 130, 220)
    TXT = image.Color.from_rgb(255, 255, 255)
    TITLE = image.Color.from_rgb(255, 220, 0)

    screen_w = disp.width()
    screen_h = disp.height()

    title_height = int(screen_h * 0.12)

    bottom_btn_height = int(screen_h * 0.15)
    bottom_margin = int(screen_h * 0.05)

    card_margin = int(screen_w * 0.04)
    card_x = card_margin
    card_y = title_height + int(screen_h * 0.02)
    card_w = screen_w - card_margin * 2
    card_h = screen_h - card_y - bottom_btn_height - bottom_margin - int(screen_h * 0.03)

    btn_padding = int(card_w * 0.04)
    btn_w = card_w - btn_padding * 2
    btn_h = int(card_h * 0.25)
    btn_x = card_x + btn_padding
    gap = int((card_h - btn_h * 3 - btn_padding * 2) / 2)


    btn_enc = [btn_x, card_y + btn_padding, btn_w, btn_h]
    bps_w = int(btn_w * 0.60)
    rc_gap = 20
    rc_w = int(btn_w * 0.40) - rc_gap
    btn_bps = [btn_x, card_y + btn_padding + btn_h + gap, bps_w, btn_h]
    btn_rc  = [btn_x + bps_w + rc_gap, card_y + btn_padding + btn_h + gap, rc_w, btn_h]
    btn_res = [btn_x, card_y + btn_padding + (btn_h + gap) * 2, btn_w, btn_h]

    exit_btn_w = int(screen_w * 0.16)
    tailscale_btn_w = int(screen_w * 0.26)
    go_btn_w = int(screen_w * 0.42)
    rc_gap = 20
    tailscale_installed = shutil.which("tailscale") is not None

    if tailscale_installed:
        total_btn_w = go_btn_w + tailscale_btn_w + exit_btn_w + rc_gap * 2
        left = (screen_w - total_btn_w) // 2
        btn_go = [left, screen_h - bottom_btn_height - bottom_margin, go_btn_w, bottom_btn_height]
        btn_tailscale = [btn_go[0] + go_btn_w + rc_gap, screen_h - bottom_btn_height - bottom_margin, tailscale_btn_w, bottom_btn_height]
        btn_exit = [btn_tailscale[0] + tailscale_btn_w + rc_gap, screen_h - bottom_btn_height - bottom_margin, exit_btn_w, bottom_btn_height]
    else:
        btn_go_w = screen_w - exit_btn_w - card_margin * 3
        btn_go  = [card_margin, screen_h - bottom_btn_height - bottom_margin, btn_go_w, bottom_btn_height]
        btn_exit = [btn_go[0] + btn_go_w + card_margin, screen_h - bottom_btn_height - bottom_margin, exit_btn_w, bottom_btn_height]

    def draw_round_rect(img, x, y, w, h, color):
        img.draw_rect(x, y, w, h, color, thickness=-1)

    def draw_setting_row(img, box, label, value, pressed=False):
        col = BTN_P if pressed else BTN
        draw_round_rect(img, box[0], box[1], box[2], box[3], col)

        pad_x = 14
        scale = 2

        lsize = image.string_size(label, scale=scale)
        vsize = image.string_size(value, scale=scale)

        max_h = lsize.height() if lsize.height() > vsize.height() else vsize.height()
        ty = box[1] + (box[3] - max_h) // 2

        lx = box[0] + pad_x
        img.draw_string(lx, ty, label, color=TXT, scale=scale)

        vx = box[0] + box[2] - pad_x - vsize.width()
        img.draw_string(vx, ty, value, color=TXT, scale=scale)

    def draw_rc_switch(img, box, selected):
        gap = 18
        w = (box[2] - gap) // 2
        h = box[3]
        x0 = box[0]
        x1 = box[0] + w + gap
        y = box[1]

        draw_round_rect(img, x0, y, w, h, BTN_P if selected == 0 else BTN)
        cbr_size = image.string_size("CBR", scale=2)
        img.draw_string(x0 + (w-cbr_size.width())//2, y + (h-cbr_size.height())//2, "CBR", color=TXT, scale=2)

        draw_round_rect(img, x1, y, w, h, BTN_P if selected == 1 else BTN)
        vbr_size = image.string_size("VBR", scale=2)
        img.draw_string(x1 + (w-vbr_size.width())//2, y + (h-vbr_size.height())//2, "VBR", color=TXT, scale=2)


    while not app.need_exit():
        img = image.Image(disp.width(), disp.height(), image.Format.FMT_RGB888)
        img.clear()
        img.draw_rect(0, 0, disp.width(), disp.height(), BG, thickness=-1)

        title = "Stream Settings"
        tsz = image.string_size(title, scale=2)
        img.draw_string((disp.width() - tsz.width()) // 2, 20, title, color=TITLE, scale=2)

        draw_round_rect(img, card_x, card_y, card_w, card_h, CARD)

        draw_setting_row(img, btn_enc, "Encoder", encoders[choice_encoder])
        draw_setting_row(img, btn_bps, "Bitrate", bitrates[choice_bitrate])
        draw_rc_switch(img, btn_rc, choice_rc_type)
        draw_setting_row(img, btn_res, "Resolution", resolutions[choice_res])

        draw_round_rect(img, btn_go[0], btn_go[1], btn_go[2], btn_go[3], BTN_P)
        txt = "Start Streaming"
        tsize = image.string_size(txt, scale=2)
        tx = btn_go[0] + (btn_go[2] - tsize.width()) // 2
        ty = btn_go[1] + (btn_go[3] - tsize.height()) // 2
        img.draw_string(tx, ty, txt, color=TXT, scale=2)

        t = ts.read()

        if tailscale_installed:
            draw_round_rect(img, btn_tailscale[0], btn_tailscale[1], btn_tailscale[2], btn_tailscale[3], image.Color.from_rgb(60, 180, 120))
            txt_ts = "Tailscale"
            tsize_ts = image.string_size(txt_ts, scale=2)
            tx_ts = btn_tailscale[0] + (btn_tailscale[2] - tsize_ts.width()) // 2
            ty_ts = btn_tailscale[1] + (btn_tailscale[3] - tsize_ts.height()) // 2
            img.draw_string(tx_ts, ty_ts, txt_ts, color=TXT, scale=2)
            if in_box(t, btn_tailscale):
                time.sleep_ms(150)
                tailscale_config_page()
                continue

        draw_round_rect(img, btn_exit[0], btn_exit[1], btn_exit[2], btn_exit[3], image.Color.from_rgb(200, 60, 60))
        txt_exit = "Exit"
        tsize_exit = image.string_size(txt_exit, scale=2)
        tx_exit = btn_exit[0] + (btn_exit[2] - tsize_exit.width()) // 2
        ty_exit = btn_exit[1] + (btn_exit[3] - tsize_exit.height()) // 2
        img.draw_string(tx_exit, ty_exit, txt_exit, color=TXT, scale=2)

        disp.show(img)

        if not t[2]:
            time.sleep_ms(60)
            continue

        if in_box(t, btn_enc):
            choice_encoder = (choice_encoder + 1) % len(encoders)
        elif in_box(t, btn_bps):
            choice_bitrate = (choice_bitrate + 1) % len(bitrates)
        elif in_box(t, btn_rc):
            choice_rc_type = (choice_rc_type + 1) % 2
        elif in_box(t, btn_res):
            choice_res = (choice_res + 1) % len(resolutions)
        elif in_box(t, btn_go):
            return True
        elif in_box(t, btn_exit):
            return False

        time.sleep_ms(150)

    return False


def start_streaming():

    res_map = {
        "720 P": (1280, 720),
        "1080 P": (1920, 1080),
        "2 K": (2560, 1440),
        "4 K": (3840, 2160),
    }
    W, H = res_map[resolutions[choice_res]]

    enc = encoders[choice_encoder]
    stream_type = (
        webrtc.WebRTCStreamType.WEBRTC_STREAM_H264
        if enc == "H.264"
        else webrtc.WebRTCStreamType.WEBRTC_STREAM_H265
    )

    bitrate_str = bitrates[choice_bitrate]
    bitrate_m = int(bitrate_str.replace(" Mbps", ""))
    bitrate_value = bitrate_m * 1000 * 1000

    print(f"Start stream: {enc}, {W}x{H}, {bitrate_value}bps")

    cam = camera.Camera(W, H, image.Format.FMT_YVU420SP, fps=30)
    cam2 = cam.add_channel(disp.width(), disp.height())

    rc_type = webrtc.WebRTCRCType.WEBRTC_RC_CBR if choice_rc_type == 0 else webrtc.WebRTCRCType.WEBRTC_RC_VBR
    server = webrtc.WebRTC(
        stream_type=stream_type,
        rc_type=rc_type,
        bitrate=bitrate_value,
        gop=15,
        stun_server="stun:stun.miwifi.com:3478",
    )

    server.bind_camera(cam)
    server.start()

    urls = server.get_urls()
    print("Play URLs:", urls)

    img_exit = image.load("./assets/exit.jpg").resize(50, 50)
    img_exit_touch = image.load("./assets/exit_touch.jpg").resize(50, 50)
    img_eye_open = image.load("./assets/img_eye_open.png").resize(50, 50)
    img_eye_close = image.load("./assets/img_eye_close.png").resize(50, 50)
    img_eye_last_change = time.ticks_ms()

    need_exit = False
    show_urls = False

    while not app.need_exit():
        try:
            img = cam2.read()
        except:
            time.sleep_ms(5)
            continue

        t = ts.read()
        pad = 15
        box_exit = [20 - pad, 15 - pad, img_exit.width() - pad * 2, img_exit.height() - pad * 2]
        if in_box(t, box_exit):
            img.draw_image(box_exit[0], box_exit[1], img_exit_touch)
            need_exit = True
        else:
            img.draw_image(box_exit[0], box_exit[1], img_exit)

        box_eye = [20, 15 + img_exit.height() + 18, img_eye_open.width(), img_eye_open.height()]
        if in_box(t, box_eye) and time.ticks_ms() - img_eye_last_change > 200:
            img_eye_last_change = time.ticks_ms()
            show_urls = not show_urls

        if show_urls:
            img.draw_image(box_eye[0], box_eye[1], img_eye_open)
        else:
            img.draw_image(box_eye[0], box_eye[1], img_eye_close)

        if show_urls and urls:
            screen_w = disp.width()
            screen_h = disp.height()
            url_scale = max(2, int(screen_w / 300))
            url_margin = int(screen_w * 0.05)
            title_text = "WebRTC URL:"
            title_size = image.string_size(title_text, scale=url_scale)
            x = screen_w - title_size.width() - url_margin
            y = int(screen_h * 0.05)
            img.draw_string(x, y, title_text,
                            color=image.Color.from_rgb(0,255,0),
                            scale=url_scale)
            line_spacing = int(title_size.height() * 2)
            y += line_spacing
            for u in urls:
                url_size = image.string_size(u, scale=url_scale)
                x = max(url_margin, screen_w - url_size.width() - url_margin)
                img.draw_string(x, y, u,
                                color=image.Color.from_rgb(0,255,0),
                                scale=url_scale)
                y += int(line_spacing * 0.9)

        disp.show(img)

        if need_exit:
            break

    del server

while not app.need_exit():
    if not config_page():
        break
    start_streaming()
