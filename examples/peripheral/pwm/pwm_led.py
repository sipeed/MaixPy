from maix import pwm, time, pinmap, sys


# get pin and pwm number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "IO0_A30"
    pwm_id = 6
else:
    pin_name = "A18"
    pwm_id = 6

# set pinmap
pinmap.set_pin_function(pin_name, f"PWM{pwm_id}")


SERVO_PERIOD = 100000     # 100kHz 0.01ms

out = pwm.PWM(pwm_id, freq=SERVO_PERIOD, duty=0, enable=True)

for i in range(100):
    print(i)
    out.duty(i)
    time.sleep_ms(100)

for i in range(100):
    print(i)
    out.duty(100 - i)
    time.sleep_ms(100)
