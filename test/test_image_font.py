from maix import display, image
from maix.err import Err
import time

screen = display.Display(device = None, width = 640, height = 480)

# https://github.com/adobe-fonts/source-han-sans/releases
image.load_font("sourcehansans", "SourceHanSansCN-Normal.otf", size = 32)
# image.load_font("sourcehansans2", "SourceHanSansCN-Normal.otf", size = 32)
print("fonts:", image.fonts())
image.set_default_font("sourcehansans")

img_show = image.Image(screen.width(), screen.height(), image.Format.FMT_RGBA8888)

size = image.text_size("Hello, world!", font = "hershey_simplex")
img_show.draw_rect(0, 0, size[0], size[1], image.Color.from_rgba(255, 255, 0, 0.5))
img_show.draw_text(0, 0, "Hello, world!", image.Color.from_rgba(255, 255, 255, 1), font = "hershey_simplex")
size = image.text_size("你好！Hello, world!")
x_start = image.text_size("Hello, world!", font = "hershey_simplex")[0]
img_show.draw_rect(x_start, 0, size[0], size[1], image.Color.from_rgba(255, 255, 0, 0.5))
img_show.draw_text(x_start, 0, "你好！Hello, world!", image.Color.from_rgba(255, 0, 0, 1))

screen.show(img_show, fit = image.Fit.FIT_NONE)

count = 6
while count > 0:
    time.sleep(1)
    if not screen.is_opened():
        break
    count -= 1
