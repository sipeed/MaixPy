from maix import pwm, time, pinmap, err

SERVO_PERIOD = 50     # 50Hz 20ms
SERVO_MIN_DUTY = 2.5  # 2.5% -> 0.5ms
SERVO_MAX_DUTY = 12.5  # 12.5% -> 2.5ms


# get pin and pwm number according to device id
device_id = sys.device_id()
if device_id == "maixcam2":
    pin_name = "IO0_A31"
    pwm_id = 7
else:
    pin_name = "A19"
    pwm_id = 7

# set pinmap
err.check_raise(pinmap.set_pin_function(pin_name, f"PWM{pwm_id}"), "set pinmap failed")



def angle_to_duty(percent):
    return (SERVO_MAX_DUTY - SERVO_MIN_DUTY) * percent / 100.0 + SERVO_MIN_DUTY


out = pwm.PWM(pwm_id, freq=SERVO_PERIOD, duty=angle_to_duty(0), enable=True)

for i in range(100):
    out.duty(angle_to_duty(i))
    time.sleep_ms(100)

for i in range(100):
    out.duty(angle_to_duty(100 - i))
    time.sleep_ms(100)
