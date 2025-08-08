from maix import pinmap, gpio, sys, time, err

# get pin and GPIO number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "IO1_A25"
else:
    pin_name = "B3"

# Every Pin may have multiple functions
print(f"Pin {pin_name} functions:")
funcs = pinmap.get_pin_functions(pin_name)
print(funcs)

# Find GPIO function id and set pin function to it
print(f"Set pin function to GPIO")
gpio_id = None
for func_id in funcs:
    if "GPIO" in func_id:
        print(f"set function as {func_id}")
        err.check_raise(pinmap.set_pin_function(scl_pin_name, func_id), f"set pin {pin_name} function as {func_id} failed")
        gpio_id = func_id
        break

if not gpio_id:
    print(f"Pin {pin_name} not support GPIO function")
else:
    # Now we can use GPIO normally
    # Init GPIO
    led = gpio.GPIO(gpio_id, gpio.Mode.OUT)
    led.value(0)

    while 1:
        led.toggle()
        time.sleep_ms(500)

