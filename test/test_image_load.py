from maix import display, image
from maix.err import Err
import time

img = image.load("docs/static/image/sipeed_splash.jpeg")
img_bgr = image.load("docs/static/image/sipeed_splash.jpeg", format = image.Format.FMT_BGR888)

img_rgba_jpg = image.load("docs/static/image/sipeed_splash.jpeg", format = image.Format.FMT_RGBA8888)
img_rgba_png = image.load("docs/static/image/camera.png", format = image.Format.FMT_RGBA8888)

screen = display.Display(device = None, width = 640, height = 480)
screen_size = screen.size()

img_show = image.Image(640, 480, image.Format.FMT_RGB888)
img = img.resize(300, -1)
img_show.draw_image(0, 0, img)
img_bgr = img_bgr.resize(300, -1)
img_show.draw_image(340, 0, img_bgr)
img_show.draw_rect(img.width(), 0, 40, 80, image.Color.from_rgb(255, 0, 0))
img_show.draw_rect(img.width(), 90, 40, 80, image.Color.from_rgb(0, 255, 0))
screen.show(img_show, fit = image.Fit.FIT_CONTAIN)
time.sleep(1)

# img_show = img_show.to_format(image.Format.FMT_RGBA8888)
img_show = image.Image(640, 480, image.Format.FMT_RGBA8888)
# img_show.draw_rect(0, 0, img_show.width(), img_show.height(), image.Color.from_rgba(255, 255, 255, 1), -1)
img_rgba_jpg = img_rgba_jpg.resize(300, -1)
img_show.draw_image(0, img.height() + 10, img_rgba_jpg)
img_show.draw_image(0, img.height() + 20, img_rgba_png)
half_w = screen_size[0] // 2
font_h0 = img.height() + 150 + image.text_size("H", scale = 0.5)[1]
font_h = font_h0
img_show.draw_rect(half_w + 100, font_h, 40, 80, image.Color.from_rgb(255, 255, 255))
img_show.draw_rect(half_w + 110, font_h + 10, 40, 80, image.Color.from_rgba(255, 255, 255, 0.5))
img_show.draw_line(half_w + 100, font_h - 10, half_w + 140, font_h + 10, image.COLOR_RED)
img_show.draw_circle(half_w + 100, font_h - 20, 5, image.COLOR_GREEN)
img_show.draw_text(0, font_h, "Hello, world!", image.Color.from_rgba(255, 255, 255, 1), scale = 0.5)
font_h += image.text_size("H", scale = 1)[1]
img_show.draw_text(0, font_h, "Hello, world!", image.Color.from_rgba(255, 255, 255, 1), scale = 1, thickness = 2)
font_h += image.text_size("H", scale = 2)[1]
img_show.draw_text(0, font_h, "Hello, world!", image.Color.from_rgba(255, 255, 255, 1), scale = 2)
img_show.draw_text(half_w, font_h0 - 100, "Hello, world! ABCDEFGHIJKLMNOPQRSTUVWXYZ", image.Color.from_rgba(255, 255, 255, 1))

screen.show(img_show, fit = image.Fit.FIT_NONE)

count = 6
while count > 0:
    time.sleep(1)
    if not screen.is_opened():
        break
    count -= 1
