

from maix import image, time, display, touchscreen


class Bechmark:
    name = "Display"

    def __init__(self):
        self.repeat_time = 50
        self.disp = display.Display()
        self.ts = touchscreen.TouchScreen()

    def benchmark_show_img(self, img, items):
        # warm up
        item_name = f"show {img.width()}x{img.height()}"
        msg = f"Testing {item_name} ..."
        print(msg)
        scale = (4 if img.height() >= 1080 else 2) if img.height() >= 480 else 1
        thickness = (4 if img.height() >= 1080 else 2) if img.height() >= 480 else 1
        size = image.string_size(msg, scale = scale, thickness=thickness)
        img.draw_string((img.width() - size.width()) // 2, (img.height() - size.height()) // 2, msg, scale = scale, thickness=thickness)
        self.disp.show(img)
        count = self.repeat_time
        t_sum = 0
        while count > 0:
            t = time.ticks_us()
            self.disp.show(img)
            t_sum += time.ticks_us() - t
            count -= 1
            time.sleep_ms(1)
        t = t_sum // self.repeat_time
        fps = 1000000 // t
        items[item_name] = f"{t} us, {fps} fps"
        print(item_name, ":", items[item_name])

    def run(self):
        items = {
        }

        # show same with disp res
        img = image.Image(self.disp.width(), self.disp.height(), bg=image.COLOR_BLACK)
        self.benchmark_show_img(img, items)

        # show QVGA
        img = image.Image(320, 240, bg=image.COLOR_BLACK)
        self.benchmark_show_img(img, items)

        # show 320x320
        img = image.Image(320, 320, bg=image.COLOR_BLACK)
        self.benchmark_show_img(img, items)

        # show VGA
        img = image.Image(640, 480, bg=image.COLOR_BLACK)
        self.benchmark_show_img(img, items)

        # show 640
        img = image.Image(640, 640, bg=image.COLOR_BLACK)
        self.benchmark_show_img(img, items)

        # show 720p
        img = image.Image(1280, 720, bg=image.COLOR_BLACK)
        self.benchmark_show_img(img, items)

        # show 1080p
        img = image.Image(1920, 1080, bg=image.COLOR_BLACK)
        self.benchmark_show_img(img, items)

        # show results
        if self.disp.height() > 480:
            font_scale = 2.3
            title_font_scale = 3
        elif self.disp.height() > 240:
            font_scale = 1.4
            title_font_scale = 2.1
        img = image.Image(self.disp.width(), self.disp.height(), bg=image.COLOR_BLACK)
        size = image.string_size("aA!~=?")
        y = 2
        for k, v in items.items():
            img.draw_string(2, y , f"{k}: {v}", scale=font_scale)
            y += size.height() + size.height() // 2

        return True, img

if __name__ == "__main__":
    from maix import app

    disp = display.Display()
    obj = Bechmark(disp)
    img = obj.run()
    disp.show(img)
    while not app.need_exit():
        time.sleep_ms(10)
