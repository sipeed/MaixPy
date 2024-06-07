from maix import camera, image

class Scanner:
    def __init__(self, w, h):
        self.cam = camera.Camera(200, 200)

    def scan(self):
        img = self.cam.read()
        if img is None:
            return None, None
        # scan qrcode
        qrs = img.find_qrcodes()
        for qr in qrs:
            addr = qr.payload()
            if addr.startswith("http"):
                return addr, img
            corners = qr.corners()
            for i in range(4):
                img.draw_line(corners[i][0], corners[i][1], corners[(i + 1) % 4][0], corners[(i + 1) % 4][1], image.COLOR_RED)
        return None, img
        # return "http://127.0.0.1:9999", img

