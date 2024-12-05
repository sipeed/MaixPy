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
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            try:
                with open(path, "rb") as f:
                    while chunk := f.read(2097152):
                        self.wfile.write(chunk)
            except Exception as e:
                self.send_error(500, f"File read error: {str(e)}")
        else:
            self.send_error(404, "File not found")

    def preview_file(self):
        query = parse_qs(urlparse(self.path).query)
        path = query.get("path", [None])[0]
        if path and os.path.isfile(path):
            ext = os.path.splitext(path)[-1].lower()
            try:
                if ext in [".txt", ".md", ".py", ".mud", ".json", ".yaml", ".yml", ".conf", ".ini", ".version", ".log"]:
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    with open(path, "r", encoding="utf-8") as f:
                        for line in f:  # 按行读取
                            self.wfile.write(line.encode("utf-8"))
                elif ext in [".jpg", ".jpeg", ".png", ".gif", ".webm", ".ogg", ".avi", ".flv"]:
                    content_type = {
                        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                        ".png": "image/png", ".gif": "image/gif",
                        ".webm": "video/webm", ".ogg": "video/ogg",
                        ".avi": "video/x-msvideo", ".flv": "video/x-flv"
                    }.get(ext, "application/octet-stream")
                    self.send_response(200)
                    self.send_header("Content-Type", content_type)
                    self.end_headers()
                    with open(path, "rb") as f:
                        while chunk := f.read(2097152):  # 每次读取 2MB
                            self.wfile.write(chunk)
                elif ext == ".mp4":  # 单独处理 MP4 文件，支持 Range 请求
                    self.handle_partial_request(path, "video/mp4")
                else:
                    self.send_error(415, "Unsupported Media Type")
            except Exception as e:
                self.send_error(500, f"Error previewing file: {str(e)}")
        else:
            self.send_error(404, "File not found")

    def handle_partial_request(self, file_path, content_type):
        """Handle HTTP Range Requests for streaming"""
        try:
            file_size = os.path.getsize(file_path)
            range_header = self.headers.get("Range", None)
            start, end = 0, file_size - 1

            if range_header:
                import re
                range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
                if range_match:
                    start = int(range_match.group(1))
                    if range_match.group(2):
                        end = int(range_match.group(2))

            if start >= file_size or start > end:
                self.send_error(416, "Requested Range Not Satisfiable")
                return

            self.send_response(206)  # Partial Content
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(end - start + 1))
            self.end_headers()

            with open(file_path, "rb") as f:
                f.seek(start)
                while start <= end:
                    chunk_size = min(8192, end - start + 1)  # 每次读取 8KB
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    start += chunk_size

        except Exception as e:
            self.send_error(500, f"Error handling partial request: {str(e)}")


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