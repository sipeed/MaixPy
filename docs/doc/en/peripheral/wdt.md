# Using Watchdog Timer in MaixCAM MaixPy

## Introduction

To prevent program issues, a watchdog timer (WDT) is often used to automatically restart the system when the program encounters a problem.

The principle is that there is a countdown timer that we need to periodically reset within the program logic (also called "feeding the dog"). If our program gets stuck and fails to reset the countdown timer, the hardware will trigger a system reboot when the timer reaches 0.

## Using WDT in MaixPy

```python
from maix import wdt, app, time

w = wdt.WDT(0, 1000)

while not app.need_exit():
    w.feed()
    # Here, sleep operation is our task
    # 200 ms is normal; if it exceeds 1000 ms, it will cause a system reset
    time.sleep_ms(200)
```

This code sets up a watchdog timer that requires feeding every 1000 ms. If the program fails to feed the watchdog within this period, the system will reset.

