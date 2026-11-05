from maix import app, light, time


# Fill light(补光灯) on/off example
#
# The light pin is read from the board config file(/boot/board, item "cam_light_io"),
# default is "B25" on MaixCAM2 and "B3" on MaixCAM, so usually you don't need to care about it.
#
# On MaixCAM2 the light is driven by PWM and the brightness can be adjusted, the PWM
# frequency and duty are read from /boot/configs:
#     maix_light_freq: PWM frequency, unit Hz, default 10000
#     maix_light_duty: PWM duty, unit %, range 0 ~ 100, default 50
# On MaixCAM the light is driven by GPIO, so only on/off is supported.

l = light.Light()
print("light pin:", l.pin())
print("pwm freq:", l.freq(), ", duty:", l.duty())

while not app.need_exit():
    print("turn on the fill light")
    l.on()
    time.sleep(1)

    print("turn off the fill light")
    l.off()
    time.sleep(1)

    # On MaixCAM2(freq > 0 means driven by PWM), you can also adjust
    # the brightness at runtime, MaixCAM only supports on/off:
    # l.set_duty(30)   # 30% brightness
    # time.sleep(1)
    # l.set_duty(80)   # 80% brightness, will print a warning because duty > 70,
    #                  # long time high power running may cause the LED to age quickly
    # time.sleep(1)
    # l.off()

del l
