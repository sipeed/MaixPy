import time as time_sys   # We can use Python integrated time module.
from maix import time     # And maix also have time module, have some functions python time module don't have.
from maix import app

# get current system time.
# If system time change(like NTP), there value will be change also,
# so take care, these value may have large change after bootup's NTP sync time from network.
# If you want to calculate time interval please use ticks fufnctions.
print("timestamp  s:", time.time())
print("timestamp ms:", time.time_ms())
print("timestamp us:", time.time_us())
print("time:", time.localtime().strftime("%Y-%m-%d %H:%M:%S"))
print("timezone:", time.timezone())
print("")

# set timezone
# timezones = time.list_timezones()    # Get all supportted timezones
# locale = "Asia/Shanghai"
# locale = "Etc/UTC"
# time.timezone(locale)
# print("Set timezone to:", time.timezone())
print("")

print("time since bootup")
print("ticks  s:", time.ticks_s())
print("ticks ms:", time.ticks_ms())
print("ticks us:", time.ticks_us())
print("now sleep 500 ms")
t = time.ticks_ms()
time.sleep_ms(500)  # sleep_us sleep_ms sleep_s sleep
print(f"sleep {time.ticks_ms() - t} ms done")
print("")

# You can also use python integrated time module
print("timestamp  s:", time_sys.time())

# FPS
t = time.ticks_s()
while (not app.need_exit()) and time.ticks_diff(t) < 5:
    time.sleep_ms(50)
    time.sleep_ms(50)
    fps = time.fps()
    print(f"fps 1: {fps}")

t = time.ticks_s()
while (not app.need_exit()) and time.ticks_diff(t) < 5:
    time.sleep_ms(50)
    time.fps_start()
    time.sleep_ms(50)
    fps = time.fps()
    print(f"fps 2: {fps}")
