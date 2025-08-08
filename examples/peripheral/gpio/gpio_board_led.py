from maix import gpio, pinmap, time, sys, err

# get pin and GPIO number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "IO0_A6"
    gpio_id = "GPIO0_A6"
else:
    pin_name = "A14"
    gpio_id = "GPIOA14"

# set pinmap
err.check_raise(pinmap.set_pin_function(pin_name, gpio_id), "set pin failed")

led = gpio.GPIO(gpio_id, gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)

