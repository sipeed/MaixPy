from datetime import datetime
from maix import time

locale = "Asia/Shanghai"
# locale = "Etc/UTC"

timezones = time.list_timezones()
print("All regions:", timezones.keys())
print("All city in Asia:", timezones["Asia"])

print("\nCurrent timezone:", time.timezone())
print("Before set:", datetime.now())
time.timezone(locale)
print("Set timezone to:", time.timezone())

# timezone change will not affect this process, will only take effect for later process.

