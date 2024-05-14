from maix import wdt, app, time

w = wdt.WDT(0, 1000)

while not app.need_exit():
    w.feed()
    # here sleep op is our operation
    # 200 ms is normal, if > 1000ms will cause system reset
    time.sleep_ms(200)

