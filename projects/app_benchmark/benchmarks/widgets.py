from maix import image, time


class StrButton:
    def __init__(self, label, img_w, img_h, disp_w, disp_h, switch=False, switch_on = False):
        self.pos = [0, 0]
        self.last_pushed_time = 0
        self.pushed = False
        self.switch = switch
        self.switch_on = switch_on
        self.color_idx = 0
        if self.switch:
            if not self.switch_on:
                self.color_idx = 1
            self.color = [image.Color.from_rgb(56, 142, 60), image.Color.from_rgb(211, 47, 47)]
            self.color_pushed = [image.Color.from_rgb(27, 94, 32), image.Color.from_rgb(183, 28, 28)]
            self.color_border = [image.Color.from_rgb(24, 77, 28), image.Color.from_rgb(157, 24, 24)]
            self.color_border_list = [[self.color_border[0].r, self.color_border[0].g, self.color_border[0].b],
                                    [self.color_border[1].r, self.color_border[1].g, self.color_border[1].b]]
        else:
            self.color = [image.Color.from_rgb(30, 83, 219)]
            self.color_pushed = [image.Color.from_rgb(0, 40, 138)]
            self.color_border = [image.Color.from_rgb(0, 51, 182)]
            self.color_border_list = [[self.color_border[0].r, self.color_border[0].g, self.color_border[0].b]]
        self.update_vars(label, img_w, img_h, disp_w, disp_h)

    def update_vars(self, label, img_w, img_h, disp_w, disp_h):
        self.label = label
        self.img_w = img_w
        self.img_h = img_h
        self.disp_w = disp_w
        self.disp_h = disp_h
        if img_h >= 1440:
            self.scale = 5
            self.thickness = 4
        elif img_h >= 1080:
            self.scale = 4
            self.thickness = 4
        elif img_h >= 720:
            self.scale = 3
            self.thickness = 3
        elif img_h >= 480:
            self.scale = 2
            self.thickness = 2
        else:
            self.scale = 1.2
            self.thickness = 2
        self.string_size = image.string_size(self.label, scale=self.scale, thickness=self.thickness)
        self.padding = (self.string_size.height(), self.string_size.height() * 2 // 3)
        self.padding_2x = (int(self.padding[0] * 2), int(self.padding[1] * 2))
        self.btn_size = (self.string_size.width() + self.padding_2x[0], self.string_size.height() + self.padding_2x[1])
        self.set_pos(self.pos)

    def set_pos(self, pos):
        self.pos = pos
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_lb(self, pos_lb):
        self.pos = (pos_lb[0], pos_lb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rt(self, pos_rt):
        self.pos = (pos_rt[0] - self.btn_size[0], pos_rt[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rb(self, pos_rb):
        self.pos = (pos_rb[0] - self.btn_size[0], pos_rb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pushed(self, pushed):
        if pushed:
            self.last_pushed_time = time.ticks_ms()
        elif self.switch and self.pushed:
            self.switch_on = not self.switch_on
            self.color_idx = 0 if self.switch_on else 1
        self.pushed = pushed

    def draw(self, img):
        pushed = self.pushed
        if not pushed and time.ticks_ms() - self.last_pushed_time < 50:
            pushed = True
        if pushed:
            img.draw_rect(self.pos[0] + 1, self.pos[1] + 1, self.btn_size[0] - 1, self.btn_size[1] - 1, self.color_pushed[self.color_idx] , thickness=-1)
            img.draw_rect(self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1], self.color_border[self.color_idx], thickness=1)
        else:
            img.draw_rect(self.pos[0] + 1, self.pos[1] + 1, self.btn_size[0] - 1, self.btn_size[1] - 1, self.color[self.color_idx], thickness=-1)
            img.draw_rect(self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1], self.color_border[self.color_idx], thickness=1)
        img.set_pixel(self.pos[0], self.pos[1], self.color_border_list[self.color_idx])
        img.set_pixel(self.pos[0] + self.btn_size[0] - 1, self.pos[1], self.color_border_list[self.color_idx])
        img.set_pixel(self.pos[0] + self.btn_size[0] - 1, self.pos[1] + self.btn_size[1] - 1, self.color_border_list[self.color_idx])
        img.set_pixel(self.pos[0], self.pos[1] + self.btn_size[1] - 1, self.color_border_list[self.color_idx])
        # img.draw_rect(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1], self.string_size.width(), self.string_size.height(), image.COLOR_WHITE, thickness=1)
        img.draw_string(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1] + 2, self.label, image.COLOR_WHITE, scale=self.scale, thickness=self.thickness)

class ImgButton:
    def __init__(self, img_path, img_pushed_path, img_w, img_h, disp_w, disp_h, padding = [0, 0]):
        self.btn_img = image.load(img_path, image.Format.FMT_RGBA8888)
        self.btn_img_pushed = image.load(img_pushed_path, image.Format.FMT_RGBA8888) if img_pushed_path else self.btn_img
        self.pos = [0, 0]
        self.padding = padding
        self.pushed = False
        self.last_pushed_time = 0
        self.update_vars(img_w, img_h, disp_w, disp_h)

    def update_vars(self, img_w, img_h, disp_w, disp_h):
        btn_img_h = int(img_h * 0.1)
        btn_img_w = int(btn_img_h * self.btn_img.width() / self.btn_img.height())
        if btn_img_h % 2 != 0:
            btn_img_h += 1
        if btn_img_w % 2 != 0:
            btn_img_w += 1
        if btn_img_h != self.btn_img.height() or btn_img_w != self.btn_img.width():
            self.btn_img = self.btn_img.resize(btn_img_w, btn_img_h, image.Fit.FIT_CONTAIN)
            self.btn_img_pushed = self.btn_img_pushed.resize(btn_img_w, btn_img_h, image.Fit.FIT_CONTAIN)
        self.img_w = img_w
        self.img_h = img_h
        self.disp_w = disp_w
        self.disp_h = disp_h
        self.padding_2x = (int(self.padding[0] * 2), int(self.padding[1] * 2))
        self.btn_size = (self.btn_img.width() + self.padding_2x[0], self.btn_img.height() + self.padding_2x[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos(self, pos):
        self.pos = pos
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_lb(self, pos_lb):
        self.pos = (pos_lb[0], pos_lb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rt(self, pos_rt):
        self.pos = (pos_rt[0] - self.btn_size[0], pos_rt[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pos_rb(self, pos_rb):
        self.pos = (pos_rb[0] - self.btn_size[0], pos_rb[1] - self.btn_size[1])
        self.rect = [self.pos[0], self.pos[1], self.btn_size[0], self.btn_size[1]]
        self.rect_disp = image.resize_map_pos(self.img_w, self.img_h, self.disp_w, self.disp_h, image.Fit.FIT_CONTAIN, self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def set_pushed(self, pushed):
        self.pushed = pushed
        if self.pushed:
            self.last_pushed_time = time.ticks_ms()

    def draw(self, img):
        pushed = self.pushed
        if not pushed and time.ticks_ms() - self.last_pushed_time < 50:
            pushed = True
        if pushed:
            if img.format() != self.btn_img_pushed.format():
                self.btn_img_pushed = self.btn_img_pushed.to_format(img.format())
            img.draw_image(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1], self.btn_img_pushed)
        else:
            if img.format() != self.btn_img.format():
                self.btn_img = self.btn_img.to_format(img.format())
            img.draw_image(self.pos[0] + self.padding[0], self.pos[1] + self.padding[1], self.btn_img)

