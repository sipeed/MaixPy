# Using PWM in MaixCAM MaixPy

## Introduction

To use `PWM` in MaixPy (v4), first set the pin function to `PWM` using `pinmap`.

Each `PWM` corresponds to a specific pin, as shown in the pin diagram of MaixCAM:

![](http://wiki.sipeed.com/hardware/zh/lichee/assets/RV_Nano/intro/RV_Nano_3.jpg)

We recommend using `PWM6` and `PWM7`.

For `MaixCAM`, since `WiFi` uses all pins of `SDIO1`, `PWM4~9` can only be used alternatively with `WiFi`.
> TODO: Provide a method to disable WiFi (requires disabling the WiFi driver in the system, which is quite complex)


## Using PWM to Control a Servo in MaixPy

Here we take controlling a servo as an example, using `PWM7` and the `A19` pin of `MaixCAM`:

```python
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
```

This code controls the servo to rotate from the minimum angle to the maximum angle and then back to the minimum angle.

