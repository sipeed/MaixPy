from maix import gpio, pinmap, time, sys, err

# get pin and GPIO number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "A2"
    gpio_id = "GPIOA2"
else:
    pin_name = "A19"
    gpio_id = "GPIOA19"

# set pinmap
err.check_raise(pinmap.set_pin_function(pin_name, gpio_id), "set pin failed")

# Init GPIO
led = gpio.GPIO(gpio_id, gpio.Mode.IN)

while 1:
    print(led.value())
    time.sleep_ms(1) # sleep to make cpu free
