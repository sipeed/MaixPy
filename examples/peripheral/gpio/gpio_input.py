from maix import gpio, pinmap, time

pinmap.set_pin_function("A19", "GPIOA19")
led = gpio.GPIO("A19", gpio.Mode.IN)

while 1:
    print(led.value())
    time.sleep_ms(1) # sleep to make cpu free
