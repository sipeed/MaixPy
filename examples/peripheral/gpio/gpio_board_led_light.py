from maix import gpio, pinmap, time, sys

# get pin and GPIO number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "IO1_A25"
    gpio_id = "GPIO1_A25"
else:
    pin_name = "B3"
    gpio_id = "GPIOB3"

# set pinmap
pinmap.set_pin_function(pin_name, gpio_id)

# Init GPIO
led = gpio.GPIO(gpio_id, gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)

