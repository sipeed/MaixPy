from maix import gpio, pinmap, time

pinmap.set_pin_function("A14", "GPIOA14")
led = gpio.GPIO("GPIOA14", gpio.Mode.OUT)
led.value(0)

while 1:
    led.toggle()
    time.sleep_ms(500)

