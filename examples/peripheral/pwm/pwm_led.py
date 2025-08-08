from maix import pwm, time, pinmap, sys, err


# get pin and pwm number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "IO1_A25" # LED light
    pwm_id = 6
else:
    pin_name = "A18" # A18 pin
    pwm_id = 6

# set pinmap
err.check_raise(pinmap.set_pin_function(pin_name, f"PWM{pwm_id}"), "set pinmap failed")


SERVO_PERIOD = 100000     # 100kHz 0.01ms

out = pwm.PWM(pwm_id, freq=SERVO_PERIOD, duty=0, enable=True)

for i in range(100):
    print(i)
    out.duty(i)
    time.sleep_ms(100)

for i in range(100):
    print(100 - i)
    out.duty(100 - i)
    time.sleep_ms(100)
