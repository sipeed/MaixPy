from maix.peripheral import pinmap

print("All pins of MaixCAM:")
print(pinmap.get_pins())

print("GPIO A28 pin functions:")
f = pinmap.get_pin_functions("A28")
print(f)

print(f"Set GPIO A28 to {f[0]} function")
pinmap.set_pin_function("A28", f[0])