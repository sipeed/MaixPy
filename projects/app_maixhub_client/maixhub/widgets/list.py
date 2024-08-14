from maix import image

class UI_List:
    def __init__(self, items:list, x, y, lines,
            scale = 1, color = image.Color.from_rgb(255, 255, 255), thickness = 2,
            color_active = image.Color.from_rgb(0, 255, 0), rectangle = None,
            default_idx = 0,
            value_items = None):
        '''
            @x -1: center
            @value_items if not None, will return this value in get_selected()
        '''
        self.items = items
        self.curr = default_idx
        self.last = default_idx - 1
        if self.last < 0:
            self.last = len(items) - 1
        self.x = x
        self.y = y
        self.lines = lines
        self.scale = scale
        self.color = color
        self.thickness = thickness
        self.color_active = color_active
        self.rectangle = rectangle
        self.value_items = value_items

    def next(self):
        self.last = self.curr
        self.curr += 1
        if self.curr >= len(self.items):
            self.curr = 0

    def prev(self):
        raise NotImplementedError()

    def remove(self, idx):
        self.items.pop(idx)
        self.curr = 0
        self.last = len(self.items) - 1

    def get_selected(self):
        return self.curr, self.value_items[self.curr] if self.value_items else self.items[self.curr]

    def draw(self, img : image.Image):
        y = self.y
        if self.curr < self.lines:
            active_idx = self.curr
            screen_items = self.items[: self.lines]
        else:
            active_idx = self.lines - 1
            screen_items = self.items[self.curr - self.lines + 1 : self.curr + 1]
        max_w = 0
        items = []
        for i, item in enumerate(screen_items):
            if i == active_idx:
                color = self.color_active
            else:
                color = self.color
            w, h = image.string_size(item, scale = self.scale, thickness = self.thickness)
            if self.x < 0:
                x = (img.width() - w) // 2
            else:
                x = self.x
            items.append([x, y, item, color, w, h])
            y += h
            if w > max_w:
                max_w = w
        if self.rectangle:
            img.draw_rect(self.x - 10, self.y - 10, self.x + max_w + 10, y + 10, color=self.rectangle, thickness=-1)
        for x, y, item, color, w, h in items:
            img.draw_string(x, y, item, scale = self.scale, color = color, thickness = -1)
        return img

