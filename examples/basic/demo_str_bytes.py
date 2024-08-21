
a = "hello"
b = b'hello'
print(type(a), type(b))
print("")

print(a == b.decode("utf-8"))
print(a.encode("utf-8") == b)
print("")

a = "abc123\x00\x01\x02\x03"
b = b"abc123\x00\x01\x02\x03"
print("a:", a)
print("b:", b)
print("a[0]:", a[0], type(a[0]))
print("b[0]:", b[0], type(b[0]))
print("")

a = 0x61 # 97, b'a'
print(f"hex: 0x{a:x}")
print(f"decimalism: {a}")
print(f"ASCII(str): {chr(a)}")
print("")


a = [97, 98, 99, 49, 50, 51, 0, 1, 2, 3]
print(bytes(a))

