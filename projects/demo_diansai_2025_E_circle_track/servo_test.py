from maix import pwm, time, pinmap


# test_pitch = True
test_pitch = False

SERVO_MIN_DUTY = 2.5  # 2.5% -> 0.5ms
SERVO_MAX_DUTY = 12.5  # 12.5% -> 2.5ms 10% -> 2ms

if test_pitch:
    SERVO_PERIOD = 50     # 50Hz 20ms
    SERVO_MIN_DUTY = 5
    SERVO_MAX_DUTY = 7
    pwm_id = 6
    pin_name = "A18"
else:
    SERVO_PERIOD = 50     # 50Hz 20ms
    SERVO_MIN_DUTY = 6.5  # 2.5% -> 0.5ms
    SERVO_MAX_DUTY = 8.5  # 12.5% -> 2.5ms 10% -> 2ms
    pwm_id = 7
    pin_name = "A19"

init_pos = 50
pinmap.set_pin_function(pin_name, f"PWM{pwm_id}")
pinmap.set_pin_function(pin_name, f"PWM{pwm_id}")



def angle_percent_to_duty(percent):
    return (SERVO_MAX_DUTY - SERVO_MIN_DUTY) * percent / 100.0 + SERVO_MIN_DUTY


out = pwm.PWM(pwm_id, freq=SERVO_PERIOD, duty=angle_percent_to_duty(init_pos), enable=True)

time.sleep(2)

for i in range(0, 100):
    out.duty(angle_percent_to_duty(i))
    time.sleep_ms(100)

