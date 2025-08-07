from maix.peripheral import pinmap

print("All pins of MaixCAM:")
print(pinmap.get_pins())

print("All pin's functions:")
for pin in pinmap.get_pins():
    funcs = pinmap.get_pin_functions(pin)
    print(f"{pin:10s}: {', '.join(funcs)}")

# set pinmap
# pinmap.set_pin_function("A28", "GPIOA28")

