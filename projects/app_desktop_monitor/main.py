import time
import json
from datetime import datetime
from maix import image, display, app
from maix.touchscreen import TouchScreen
from threading import Thread
from desktop_monitor.util import get_pc_info
from desktop_monitor.scanner import Scanner
from desktop_monitor.i18n import tr
import gc

RGB = image.Format.FMT_RGB888
RGBA = image.Format.FMT_RGBA8888
COLOR_RED = image.Color.from_rgb(185, 95, 107)
COLOR_RED_DARK = image.Color.from_rgb(92, 53, 74)
COLOR_GREEN = image.Color.from_rgb(108, 145, 128)
COLOR_GREEN_DARK = image.Color.from_rgb(42, 65, 73)
COLOR_YELLOW = image.Color.from_rgb(242, 199, 128)
COLOR_WHITE = image.Color.from_rgb(255, 251, 252)
COLOR_WHITE2 = image.Color.from_rgb(245, 236, 239)
COLOR_GRAY = image.Color.from_rgb(153, 150, 171)
COLOR_DARK_GRAY = image.Color.from_rgb(79, 88, 87)
COLOR_DARK_GRAY2 = image.Color.from_rgb(26, 26, 26)
COLOR_DARK_GRAY3 = image.Color.from_rgb(33, 33, 33)

def get_bytes_str(b):
    if b < 1024:
        return f"{b}B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.1f}KB"
    elif b < 1024 * 1024 * 1024:
        return f"{b / 1024 / 1024:.1f}MB"
    else:
        return f"{b / 1024 / 1024 / 1024:.1f}GB"

def draw_time(img, x, y):
    date_now, time_now = datetime.now().strftime("%m-%d$%H:%M:%S").split("$")
    size0 = image.string_size(date_now, font = "tektur_bold", scale = 1.2)
    size1 = image.string_size(time_now, font = "tektur_bold")
    img.draw_string(img.width() - size0.width() - 20, y, f"{date_now}", COLOR_DARK_GRAY, 1.2)
    img.draw_string(img.width() - size1.width() - 20, y + size0.height() + size0.height() // 2, f"{time_now}", COLOR_DARK_GRAY)
    return max(size0.width(), size1.width()), size0.height() + size0.height() // 2 + size1.height()


def draw_cpu_usage(img, x, y, cpu_usage, imgs):
    img_cpu = imgs["img_cpu"]
    cpu_height = 100
    img.draw_image(x, y + cpu_height - img_cpu.height(), img_cpu)
    v = int(cpu_usage[0])
    color = COLOR_GREEN if v < 50 else (COLOR_YELLOW if v < 80 else COLOR_RED)
    img.draw_rect(x + img_cpu.width() + 20, y + cpu_height - v, 20, v, color, thickness=-1)
    bar_w = 20
    if x + img_cpu.width() + 20 + 20 + 20 + (len(cpu_usage) - 1) * bar_w > img.width():
        bar_w = (img.width() - x - img_cpu.width() - 20 - 20 - 20) // (len(cpu_usage) - 1)
    for i in range(1, len(cpu_usage)):
        v = int(cpu_usage[i])
        color = COLOR_GREEN if v < 50 else (COLOR_YELLOW if v < 80 else COLOR_RED)
        img.draw_rect(x + img_cpu.width() + 20 + 20 + i * bar_w, y + cpu_height - v, bar_w, v, color, thickness=-1)
    return img.width(), cpu_height

def draw_mem_usage(img, x, y, max_w, usage, imgs):
    img_mem = imgs["img_mem"]
    used = usage['used']
    total = usage['total']
    percent = used / total
    swap_used = usage['swap_used']
    swap_total = usage['swap_total']
    swap_percent = swap_used / swap_total
    usage_str = f"{get_bytes_str(used)} / {get_bytes_str(total)}"
    usage_swap_str = f"{get_bytes_str(swap_used)} / {get_bytes_str(swap_total)}"
    size0 = image.string_size(usage_str, scale = 0.5, font = "tektur_bold")
    size1 = image.string_size(usage_swap_str, scale = 0.5, font = "tektur_bold")
    img.draw_image(x, y, img_mem)
    bar_x = x + img_mem.width() + 20
    bar_w = max_w - bar_x - size0.width() - 20 - 20
    half_h = img_mem.height() // 2
    bar_h = int(half_h * 0.7)
    color0 = COLOR_GREEN if percent < 0.5 else (COLOR_YELLOW if percent < 0.8 else COLOR_RED)
    color1 = COLOR_GREEN if swap_percent < 0.5 else (COLOR_YELLOW if swap_percent < 0.8 else COLOR_RED)
    img.draw_rect(bar_x, y + (half_h - bar_h) // 2, int(bar_w * percent), bar_h, color0, thickness=-1)
    img.draw_rect(bar_x, y + half_h + (half_h - bar_h) // 2, int(bar_w * swap_percent), bar_h, color1, thickness=-1)
    img.draw_string(bar_x + 5 + int(bar_w * percent), y + (half_h - size0.height()) // 2, usage_str, COLOR_GRAY, 0.5)
    img.draw_string(bar_x + 5 + int(bar_w * swap_percent), y + half_h + (half_h - size0.height()) // 2, usage_swap_str, COLOR_GRAY, 0.5)
    return max_w, img_mem.height()

def draw_net_charts(img, x, y, info, imgs):
    img_net = imgs["img_net"]
    img_upload = imgs["img_upload"]
    img_download = imgs["img_download"]
    img.draw_image(x, y, img_net)
    x += img_net.width() + 20
    text_h = image.string_size("22.5MB/s", scale = 0.5, font = "tektur_bold").height()
    if img_upload.height() != text_h:
        img_upload = img_upload.resize(-1, text_h)
        img_download = img_download.resize(-1, text_h)
    img.draw_image(x, y, img_upload)
    img.draw_image(x, y + img_upload.height() + 10, img_download)
    x += img_upload.width() + 20
    for k, v in info.items():
        speed_rx = v['speed_rx']
        speed_tx = v['speed_tx']
        speed_rx_str = f"{get_bytes_str(speed_rx)}/s"
        speed_tx_str = f"{get_bytes_str(speed_tx)}/s"
        size0 = image.string_size(speed_tx_str, scale = 0.5, font = "tektur_bold")
        size1 = image.string_size(speed_rx_str, scale = 0.5, font = "tektur_bold")
        size_name = image.string_size(k, scale = 0.6, font = "tektur_bold")
        w = max(size0.width(), size1.width(), size_name.width())
        h = size0.height() + size1.height() + size_name.height() + 10 * 2
        img.draw_string(x + (w - size_name.width()) // 2, y + h - size_name.height(), k, COLOR_GRAY, 0.6)
        img.draw_string(x + w - size0.width(), y, speed_tx_str, COLOR_GRAY, 0.5)
        img.draw_string(x + w - size1.width(), y + size0.height() + 10, speed_rx_str, COLOR_GRAY, 0.5)
        x += w + 20
    return img.width(), img_net.height()

def draw_temp(img, x, y, temp, imgs):
    img_temp = imgs["img_temp"]
    cpu_pkg_temp = temp["cpu"][0]
    img.draw_image(x, y, img_temp)
    x += img_temp.width() + 20
    temp_str = f"CPU: {cpu_pkg_temp}"
    temp_unit = "℃"
    size = image.string_size(temp_str, scale = 0.5, font = "tektur_bold")
    img.draw_string(x, y + (img_temp.height() - size.height()) // 2, temp_str, COLOR_GRAY, 0.5, font = "tektur_bold")
    img.draw_string(x + size.width(), y + (img_temp.height() - size.height()) // 2, temp_unit, COLOR_GRAY, 0.5, font = "my_font")
    return img.width(), img_temp.height()

def on_touch(tp, pressed, clicked, click_pos, touch_status, img_size, imgs):
    if touch_status["setting"]:
        if clicked:
            connect_pos = [(img_size.width() - imgs["img_connect"].width()) // 2 - 20, (img_size.height() - imgs["img_connect"].height()) // 2 - 10]
            connect_pos.append(connect_pos[0] + imgs["img_connect"].width() + 40)
            connect_pos.append(connect_pos[1] + imgs["img_connect"].height() + 20)
            scan_w = img_size.width() - img_size.width() // 4
            scan_h = img_size.height() - img_size.height() // 4
            scan_pos = [(img_size.width() - scan_w) // 2, (img_size.height() - scan_h) // 2]
            scan_pos.append(scan_pos[0] + scan_w)
            scan_pos.append(scan_pos[1] + scan_h)
            if click_pos[0] < 60 and click_pos[1] < 40:
                if touch_status["connect"]:
                    touch_status["connect"] = False
                else:
                    touch_status["exit"] = True
            elif not touch_status["connect"] and click_pos[0] > connect_pos[0] and click_pos[0] < connect_pos[2] and click_pos[1] > connect_pos[1] and click_pos[1] < connect_pos[3]:
                touch_status["connect"] = True
            elif touch_status["connect"] and click_pos[0] > scan_pos[0] and click_pos[0] < scan_pos[2] and click_pos[1] > scan_pos[1] and click_pos[1] < scan_pos[3]:
                pass
            elif touch_status["connect"]:
                touch_status["connect"] = False
            else:
                touch_status["setting"] = False
    elif clicked:
        touch_status["setting"] = True

def draw_settings(img, addr, imgs, status, scan_img, scanner_msg):
    img_exit = imgs["img_exit"]
    img.draw_rect(0, 0, img.width(), img.height(), image.Color.from_rgba(0, 0, 0, 0.7), thickness = -1)
    # draw exit button on top left
    img.draw_rect(0, 0, img_exit.width() + 40, img_exit.height() + 20, COLOR_DARK_GRAY2, thickness = -1)
    img.draw_rect(0, 0, img_exit.width() + 40, img_exit.height() + 20, COLOR_DARK_GRAY3, thickness = 2)
    img.draw_image(18, 8, img_exit)
    if not status["connect"]:
        img_connect = imgs["img_connect"]
        x = (img.width() - img_connect.width()) // 2
        y = (img.height() - img_connect.height()) // 2
        img.draw_rect(x - 20, y - 10, img_connect.width() + 40, img_connect.height() + 20, COLOR_DARK_GRAY2, thickness = -1)
        img.draw_rect(x - 20, y - 10, img_connect.width() + 40, img_connect.height() + 20, COLOR_DARK_GRAY3, thickness = 2)
        img.draw_image(x, y, img_connect)
    else:
        scan_w = img.width() - img.width() // 4
        scan_h = img.height() - img.height() // 4
        x = (img.width() - scan_w) // 2
        y = (img.height() - scan_h) // 2
        if scan_img:
            if scan_img.width() != scan_w or scan_img.height() != scan_h:
                scan_img = scan_img.resize(scan_w, scan_h, image.Fit.FIT_COVER)
            img.draw_image(x, y, scan_img)
            img.draw_rect((img.width() - scan_w) // 2, (img.height() - scan_h) // 2, scan_w, scan_h, COLOR_WHITE, thickness=2)
        if scanner_msg:
            img.draw_string(10, img.height() - image.string_size(scanner_msg).height(), scanner_msg, COLOR_WHITE)
        hint1 = tr("scan_qr_title")
        size1 = image.string_size(hint1, font = "my_font")
        hint2 = tr("scan_qr_tip1")
        size2 = image.string_size(hint2, scale = 0.5, font = "my_font")
        hint3 = tr("scan_qr_tip2")
        size3 = image.string_size(hint3, scale = 0.5, font = "my_font")
        hint4 = tr("scan_qr_tip3")
        size4 = image.string_size(hint4, scale = 0.5, font = "my_font")
        img.draw_rect(x, y, scan_w, size1[1] + size2[1] + size3[1] + size4[1] + 10 * 5, image.Color.from_rgba(0, 0, 0, 0.2), thickness = -1)
        img.draw_string((img.width() - scan_w) // 2 + 10, y + 10, hint1, COLOR_WHITE, font = "my_font")
        img.draw_string((img.width() - scan_w) // 2 + 10, y + 10 * 2 + size1[1], hint2, COLOR_WHITE, scale = 0.5, font = "my_font")
        img.draw_string((img.width() - scan_w) // 2 + 10, y + 10 * 3 + size1[1] + size2[1], hint3, COLOR_WHITE, scale = 0.5, font = "my_font")
        img.draw_string((img.width() - scan_w) // 2 + 10, y + 10 * 4+ size1[1] + size2[1] + size3[1], hint4, COLOR_WHITE, scale = 0.5, font = "my_font")
    addr_str = f"{tr('Server')}: {addr}"
    size = image.string_size(addr_str, scale = 0.5, font = "my_font")
    img.draw_string(img.width() - size.width() - 20, 10, addr_str, COLOR_WHITE, 0.5, font = "my_font")

def get_pc_info_process(info):
    info[0] = get_pc_info(info[2])
    if info[0]:
        print(json.dumps(info[0], ensure_ascii=False, indent = 4))
    t = 0
    while 1:
        if time.time() - t > 1 and not info[0]:
            t = time.time()
            info[0] = get_pc_info(info[2])
            if not info[0]:
                info[1] = True
            else:
                info[1] = False
        time.sleep(0.3)


def main():
    # server_addr = 'http://192.168.0.105:9998'
    # server_addr = 'http://127.0.0.1:9999'
    server_addr = app.get_app_config_kv("basic", "server_addr", "http://192.168.1.123:9999")

    screen = display.Display()
    ts = TouchScreen()

    image.load_font("tektur_bold", "assets/Tektur-Bold.ttf", size = 32)
    image.load_font("my_font", "assets/my_font.ttf", size = 32)
    print("fonts:", image.fonts())
    image.set_default_font("tektur_bold")
    imgs = {}
    imgs["img_cpu"] = image.load("assets/cpu.png", format = RGBA)
    imgs["img_mem"] = image.load("assets/memory.png", format = RGBA)
    imgs["img_net"] = image.load("assets/net.png", format = RGBA)
    imgs["img_bg"] = image.load("assets/bg.jpg", format = RGBA)
    imgs["img_bg"] = imgs["img_bg"].resize(-1, screen.height() * 2 // 5)
    imgs["img_upload"] = image.load("assets/upload.png", format = RGBA)
    imgs["img_temp"] = image.load("assets/temp.png", format = RGBA)
    imgs["img_exit"] = image.load("assets/exit.png", format = RGBA)
    imgs["img_connect"] = image.load("assets/connect.png", format = RGBA)
    imgs["img_download"] = image.load("assets/download.png", format = RGBA)

    pc_info = [None, False, server_addr] # info, error, server address
    get_info_th = Thread(target = get_pc_info_process, args=(pc_info,))
    get_info_th.daemon = True
    get_info_th.start()

    t = 0
    pressed = False
    click_pos = [0, 0]
    touch_status = {
        "setting": False,  # setting mode
        "exit": False,     # exit app
        "connect": False   # connect mode
    }
    scanner = None
    scanner_msg = ""
    server_changed = False
    first_time = True
    img = image.Image(screen.width(), screen.height(), RGBA)
    img.draw_rect(0, 0, img.width(), img.height(), COLOR_WHITE, thickness=-1)
    img.draw_image(img.width() - imgs["img_bg"].width(), img.height() - imgs["img_bg"].height(), imgs["img_bg"])
    msg = "Connecting..."
    size = image.string_size(msg)
    img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2 - 10, msg, COLOR_RED)
    show_img = img
    scan_w = img.width() - img.width() // 4
    scan_h = img.height() - img.height() // 4
    while 1:
        scan_img = None
        flush = False
        if first_time:
            first_time = False
            flush = True
        clicked = False
        tp = ts.read()
        if tp[2]:
            pressed = True
        elif pressed:
            print("click:", tp[0:2])
            click_pos = tp[0:2]
            clicked = True
            pressed = False

        on_touch(tp, pressed, clicked, click_pos, touch_status, img.size(), imgs)
        if touch_status["exit"]:
            break

        if touch_status["connect"]:
            if not scanner:
                try:
                    scanner = Scanner(scan_w, scan_h)
                    scanner_msg = ""
                except Exception as e:
                    print("Open camera failed", e)
                    scanner_msg = "Open camera failed"
                    scanner = None
                    touch_status["connect"] = False
            if scanner:
                server_addr, scan_img = scanner.scan()
                if server_addr:
                    pc_info[2] = server_addr
                    server_changed = True
                    touch_status["connect"] = False
                    del scanner
                    gc.collect()
                    scanner = None
        elif scanner:
            del scanner
            gc.collect()
            scanner = None
        if pc_info[0] or pc_info[1]:
            t = time.time()
            img = image.Image(screen.width(), screen.height(), RGBA)
            img.draw_rect(0, 0, img.width(), img.height(), COLOR_WHITE, thickness=-1)
            img.draw_image(img.width() - imgs["img_bg"].width(), img.height() - imgs["img_bg"].height(), imgs["img_bg"])
            if pc_info[1]:
                msg = "Get info failed"
                server_info = f"Server: {server_addr}"
                size = image.string_size(msg)
                img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2 - 10, msg, COLOR_RED)
                size = image.string_size(server_info)
                img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2 + size.height() + 10, server_info, COLOR_RED)
            else:
                if server_changed:
                    server_changed = False
                    app.set_app_config_kv("basic", "server_addr", server_addr)
                info = pc_info[0]
                h = 10
                size = draw_time(img, 10, h)
                h += size[1] + 10
                size = draw_mem_usage(img, 10, h, img.width() - size[0], info['mem'], imgs)
                h += size[1] + 10
                size = draw_cpu_usage(img, 10, h, info['cpu']['usage'], imgs)
                h += size[1] + 20
                size = draw_net_charts(img, 10, h, info['net'], imgs)
                h += size[1] + 20
                size = draw_temp(img, 10, h, info['temp'], imgs)
            show_img = img
            flush = True
            pc_info[0] = None

        if touch_status["setting"]:
            img2 = img.copy()
            draw_settings(img2, pc_info[2], imgs, touch_status, scan_img, scanner_msg)
            show_img = img2
            flush = True
        else:
            if show_img != img:
                flush = True
            show_img = img
        if flush:
            screen.show(show_img)
        time.sleep(0.01)



if __name__ == '__main__':
    main()
