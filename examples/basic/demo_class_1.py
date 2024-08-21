
class Rectangle:
    def __init__(self, x, y, w, h) -> None:
        print("init")
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def print_info(self):
        print(f"{self.x} {self.y} {self.w} {self.h}")


rect1 = Rectangle(10, 10, 20, 40)
rect2 = Rectangle(0, 0, 100, 200)
rect1.print_info()
rect2.print_info()

