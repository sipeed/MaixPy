
class A:
    static_v1 = 1
    def __init__(self) -> None:
        print("init")
        self.a = 10

    def hello(self):
        print("hello", self.a)
        self.a += 1


obj_1 = A()
obj_2 = A()
print("obj1.static_v1:", obj_1.static_v1)
print("obj_2.static_v1:", obj_2.static_v1)
print("A.static_v1:", A.static_v1)
print("obj1.a:", obj_1.a)
print("obj2.a:",obj_2.a)
obj_2.hello()
print("")

obj_1.static_v1 = 2
print("obj1.static_v1:", obj_1.static_v1)
print("obj_2.static_v1:", obj_2.static_v1)
print("A.static_v1:", A.static_v1)
print("")

A.static_v1 = 2
print("obj1.static_v1:", obj_1.static_v1)
print("obj_2.static_v1:", obj_2.static_v1)
print("A.static_v1:", A.static_v1)

