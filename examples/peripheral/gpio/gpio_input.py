from maix import gpio, pinmap, time, sys

# get pin and GPIO number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "IO0_A2"
    gpio_id = "GPIO0_A2"
else:
    pin_name = "A19"
    gpio_id = "GPIOA19"

# set pinmap
pinmap.set_pin_function(pin_name, gpio_id)

# Init GPIO
led = gpio.GPIO(gpio_id, gpio.Mode.IN)

while 1:
    print(led.value())
    time.sleep_ms(1) # sleep to make cpu free
