from maix import pwm, time, pinmap

SERVO_PERIOD = 50     # 50Hz 20ms
SERVO_MIN_DUTY = 2.5  # 2.5% -> 0.5ms
SERVO_MAX_DUTY = 12.5  # 12.5% -> 2.5ms

# Use PWM7
pwm_id = 7
# !! set pinmap to use PWM7
pinmap.set_pin_function("A19", "PWM7")



def angle_to_duty(percent):
    return (SERVO_MAX_DUTY - SERVO_MIN_DUTY) * percent / 100.0 + SERVO_MIN_DUTY


out = pwm.PWM(pwm_id, freq=SERVO_PERIOD, duty=angle_to_duty(0), enable=True)

for i in range(100):
    out.duty(angle_to_duty(i))
    time.sleep_ms(100)

for i in range(100):
    out.duty(angle_to_duty(100 - i))
    time.sleep_ms(100)
