from maix import camera, display, image

def draw_histogram(img, list, x, y, color):
    l_len = len(list)
    l_step = 2
    l_max = 100
    img.draw_line(x, y, x + l_step * l_len, y, image.COLOR_RED)
    img.draw_line(x, y, x, y + l_max, image.COLOR_RED)
    for i in range(l_len):
        img.draw_rect(x + i * l_step, y, l_step, int(list[i] * img.width() * img.height() / 100), color)

cam = camera.Camera()
cam.open(width = 640, height = 480)

screen = display.Display(device = None, width = 640, height = 480)
screen.open()

while 1:
    img = cam.read()
    hist = img.get_histogram()
    l_list = hist["L"]
    a_list = hist["A"]
    b_list = hist["B"]

    draw_histogram(img, l_list, 50, 50, image.COLOR_RED)
    draw_histogram(img, a_list, 50, 200, image.COLOR_GREEN)
    draw_histogram(img, b_list, 50, 350, image.COLOR_BLUE)
    screen.show(img)
