from maix import app, webrtc, camera, image, display, touchscreen, time
import sys

font_size = 16
image.load_font("font", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = font_size)
image.set_default_font("font")

disp = display.Display()
ts = touchscreen.TouchScreen()

encoders = ["H.264", "H.265"]
bitrates = ["1 Mbps", "2 Mbps", "4 Mbps", "8 Mbps", "16 Mbps", "32 Mbps", "64 Mbps"]
resolutions = ["720 P", "1080 P", "2 K", "4 K"]

choice_encoder = 0
choice_bitrate = 0
choice_res = 0

def in_box(t, box):
    return t[2] and box[0] <= t[0] <= box[0]+box[2] and box[1] <= t[1] <= box[1]+box[3]

def config_page():
    global choice_encoder, choice_bitrate, choice_res

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
    btn_bps = [btn_x, card_y + btn_padding + btn_h + gap, btn_w, btn_h]
    btn_res = [btn_x, card_y + btn_padding + (btn_h + gap) * 2, btn_w, btn_h]

    exit_btn_w = int(screen_w * 0.15)
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
        draw_setting_row(img, btn_res, "Resolution", resolutions[choice_res])

        draw_round_rect(img, btn_go[0], btn_go[1], btn_go[2], btn_go[3], BTN_P)
        txt = "Start Streaming"
        tsize = image.string_size(txt, scale=2)
        tx = btn_go[0] + (btn_go[2] - tsize.width()) // 2
        ty = btn_go[1] + (btn_go[3] - tsize.height()) // 2
        img.draw_string(tx, ty, txt, color=TXT, scale=2)

        draw_round_rect(img, btn_exit[0], btn_exit[1], btn_exit[2], btn_exit[3], image.Color.from_rgb(200, 60, 60))
        txt_exit = "Exit"
        tsize_exit = image.string_size(txt_exit, scale=2)
        tx_exit = btn_exit[0] + (btn_exit[2] - tsize_exit.width()) // 2
        ty_exit = btn_exit[1] + (btn_exit[3] - tsize_exit.height()) // 2
        img.draw_string(tx_exit, ty_exit, txt_exit, color=TXT, scale=2)

        disp.show(img)

        t = ts.read()
        if not t[2]:
            time.sleep_ms(60)
            continue

        if in_box(t, btn_enc):
            choice_encoder = (choice_encoder + 1) % len(encoders)
        elif in_box(t, btn_bps):
            choice_bitrate = (choice_bitrate + 1) % len(bitrates)
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

    server = webrtc.WebRTC(
        stream_type=stream_type,
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

    need_exit = False

    while not app.need_exit():
        try:
            img = cam2.read()
        except:
            time.sleep_ms(5)
            continue

        t = ts.read()
        box = [20, 15, img_exit.width(), img_exit.height()]
        if in_box(t, box):
            img.draw_image(box[0], box[1], img_exit_touch)
            need_exit = True
        else:
            img.draw_image(box[0], box[1], img_exit)

        if urls:
            screen_w = disp.width()
            screen_h = disp.height()
            url_scale = max(2, int(screen_w / 300))

            url_margin = int(screen_w * 0.05)
            url_max_width = int(screen_w * 0.85)

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

while True:
    if not config_page():
        break
    start_streaming()
