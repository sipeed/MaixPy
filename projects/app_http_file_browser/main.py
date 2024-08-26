import http.server
import socketserver
from maix import display, image, i18n, touchscreen, app, time
import os
import socket
import psutil
import threading

err_msg = ""
img_back = image.load("/maixapp/share/icon/ret.png")
back_rect = [0, 0, 32, 32]

def start_http_server(port=8000):
    global err_msg
    os.chdir("/")
    try:
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), handler) as httpd:
            print(f"Serving HTTP on port {port}...")
            httpd.serve_forever()
    except Exception:
        import traceback
        err_msg = traceback.format_exc()
        print(err_msg)

def get_ips(ignores = ["127.0.0.1"]):
    ip_addresses = []
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET:
                if snic.address in ignores:
                    continue
                ip_addresses.append(snic.address)
    return ip_addresses

def is_in_button(x, y, btn_pos):
    return x > btn_pos[0] and x < btn_pos[0] + btn_pos[2] and y > btn_pos[1] and y < btn_pos[1] + btn_pos[3]

def draw_msg(img, tr, port):
    msg = tr("msg") + "\n"
    msg_size = image.string_size(msg)
    ips = get_ips()
    for ip in ips:
        msg += f"\nhttp://{ip}:{port}"
    img.draw_string((img.width() - msg_size.width()) // 2, (img.height() - msg_size.height() * (len(ips) + 2)) // 2, msg)

def main(disp, ts):
    global err_msg
    port = 8000
    trans_dict = {
        "zh": {
            "msg": "电脑或手机打开浏览器访问:"
        },
        "en": {
            "msg": "PC or Mobile open browser visit:"
        }
    }
    image.load_font("sourcehansans", "/maixapp/share/font/SourceHanSansCN-Regular.otf", size = 24)
    image.set_default_font("sourcehansans")
    trans = i18n.Trans(trans_dict)
    tr = trans.tr
    img = image.Image(disp.width(), disp.height())
    draw_msg(img, tr, port)
    img.draw_image(0, 0, img_back)
    disp.show(img)
    th = threading.Thread(target=start_http_server, args=(port,))
    th.daemon = True
    th.start()
    while not app.need_exit():
        x, y, preesed = ts.read()
        if is_in_button(x, y, back_rect):
            app.set_exit_flag(True)
        if err_msg:
            if "Address in use" in err_msg:
                err_msg = ""
                port += 1
                img = image.Image(disp.width(), disp.height())
                draw_msg(img, tr, port)
                img.draw_image(0, 0, img_back)
                disp.show(img)
                th = threading.Thread(target=start_http_server, args=(port,))
                th.daemon = True
                th.start()
                continue
            img = image.Image(disp.width(), disp.height())
            img.draw_string(2, 2, err_msg, image.COLOR_WHITE, scale=0.8)
            img.draw_image(0, 0, img_back)
            disp.show(img)
            err_msg = ""
        time.sleep_ms(1)


if __name__ == '__main__':
    screen = display.Display()
    ts = touchscreen.TouchScreen()
    try:
        main(screen, ts)
    except Exception:
        import traceback
        e = traceback.format_exc()
        print(e)
        img = image.Image(screen.width(), screen.height())
        img.draw_string(2, 2, e, image.COLOR_WHITE, font="hershey_complex_small", scale=0.6)
        img.draw_image(0, 0, img_back)
        screen.show(img)
        while not app.need_exit():
            x, y, preesed = ts.read()
            if is_in_button(x, y, back_rect):
                app.set_exit_flag(True)
            time.sleep(0.2)