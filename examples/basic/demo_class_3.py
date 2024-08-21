
class Rectangle:
    def __init__(self, x, y, w, h) -> None:
        print("init")
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def print_info(self):
        print(f"{self.x} {self.y} {self.w} {self.h}")

class Result(Rectangle):
    def __init__(self, x, y, w, h, id):
        super(Result, self).__init__(x, y, w, h)
        self.id = id

    def print_info(self):
        print(f"[{self.id}] {self.x} {self.y} {self.w} {self.h}")

class RectangleColor(Rectangle):
    def __init__(self, x, y, w, h, color : int):
        super(RectangleColor, self).__init__(x, y, w, h)
        self.color = color

    def print_info(self):
        print(f"[0x{self.color:06X}] {self.x} {self.y} {self.w} {self.h}")


obj1 = Result(10, 10, 20, 40, "person")
obj2 = RectangleColor(0, 0, 100, 200, 0xff00ff)
obj1.print_info()
obj2.print_info()

