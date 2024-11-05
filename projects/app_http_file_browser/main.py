import http.server
import socketserver
from maix import display, image, i18n, touchscreen, app, time
import os
import socket
import psutil
import threading
import json
import time as sys_time
import hashlib
from urllib.parse import urlparse, parse_qs

err_msg = ""
img_back = image.load("/maixapp/share/icon/ret.png")
back_rect = [0, 0, 32, 32]

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Serve index.html for root path
        if parsed_path.path == "/":
            self.path = "/index.html"
            return super().do_GET()

        if parsed_path.path == "/list":
            self.list_directory()
        elif parsed_path.path == "/sha256":
            self.calculate_sha256()
        elif parsed_path.path == "/download":
            self.download_file()
        elif parsed_path.path == "/preview":
            self.preview_file()
        else:
            super().do_GET()

    def list_directory(self):
        query = parse_qs(urlparse(self.path).query)
        path = query.get("path", ["/"])[0]
        show_hidden = query.get("showHidden", ["false"])[0] == "true"
        
        try:
            files = []
            for item in sorted(os.listdir(path)):
                if item.startswith(".") and not show_hidden:
                    continue
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "path": item_path,
                    "isDirectory": os.path.isdir(item_path),
                    "time": sys_time.ctime(stat.st_mtime),
                })
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(files).encode("utf-8"))
        except Exception as e:
            self.send_error(404, "Directory not found")

    def calculate_sha256(self):
        query = parse_qs(urlparse(self.path).query)
        path = query.get("path", [None])[0]
        if path and os.path.isfile(path):
            hash_sha256 = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(hash_sha256.hexdigest().encode("utf-8"))
        else:
            self.send_error(404, "File not found")

    def download_file(self):
        query = parse_qs(urlparse(self.path).query)
        path = query.get("path", [None])[0]
        if path and os.path.isfile(path):
            self.send_response(200)
            self.send_header("Content-Disposition", f"attachment; filename={os.path.basename(path)}")
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404, "File not found")

    def preview_file(self):
        query = parse_qs(urlparse(self.path).query)
        path = query.get("path", [None])[0]
        
        if path and os.path.isfile(path):
            ext = os.path.splitext(path)[-1].lower()
            
            if ext in [".txt", ".md", ".py", ".mud", ".json", ".yaml", ".yml", ".conf"]:
                # 文本文件预览
                self.send_response(200)
                self.send_header("Content-type", "text/plain; charset=utf-8")
                self.end_headers()
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.wfile.write(content.encode("utf-8"))
            
            elif ext in [".jpg", ".jpeg", ".png", ".gif"]:
                # 图片文件预览
                self.send_response(200)
                content_type = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png" if ext == ".png" else "image/gif"
                self.send_header("Content-type", content_type)
                self.end_headers()
                with open(path, "rb") as f:
                    self.wfile.write(f.read())

            elif ext == ".mp4":
                # MP4视频文件预览
                self.send_response(200)
                self.send_header("Content-type", "video/mp4")
                self.end_headers()
                with open(path, "rb") as f:
                    self.wfile.write(f.read())
            
            elif ext == ".webm":
                # WebM视频文件预览
                self.send_response(200)
                self.send_header("Content-type", "video/webm")
                self.end_headers()
                with open(path, "rb") as f:
                    self.wfile.write(f.read())
            
            elif ext == ".ogg":
                # Ogg视频文件预览
                self.send_response(200)
                self.send_header("Content-type", "video/ogg")
                self.end_headers()
                with open(path, "rb") as f:
                    self.wfile.write(f.read())
            
            elif ext == ".avi":
                # AVI视频文件预览
                self.send_response(200)
                self.send_header("Content-type", "video/x-msvideo")
                self.end_headers()
                with open(path, "rb") as f:
                    self.wfile.write(f.read())
            
            elif ext == ".flv":
                # FLV视频文件预览
                self.send_response(200)
                self.send_header("Content-type", "video/x-flv")
                self.end_headers()
                with open(path, "rb") as f:
                    self.wfile.write(f.read())
            
            else:
                # 不支持的文件类型
                self.send_error(415, "Unsupported Media Type")
        
        else:
            self.send_error(404, "File not found")


def start_http_server(port=8000):
    global err_msg
    try:
        # handler = http.server.SimpleHTTPRequestHandler
        handler = CustomHandler
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
        time.sleep_ms(10)


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