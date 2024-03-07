from maix import time

t = time.time()
print("time:", t)
print("time_ms:", time.time_ms())
print("time_us:", time.time_us())

time.sleep(1)
time.sleep_ms(200)

print("time_diff:", time.time_diff(t))

datetime = time.gmtime(t)
print(datetime.strftime("%Y-%m-%d %H:%M:%S %z"), datetime.timestamp(), t)
datetime = time.now()
print(datetime.strftime("%Y-%m-%d %H:%M:%S %z"), datetime.timestamp())

datetime = time.localtime()
print(datetime.strftime("%Y-%m-%d %H:%M:%S %z"), datetime.timestamp())

datetime = time.strptime("2023-03-19 00:00:00", "%Y-%m-%d %H:%M:%S")
print(datetime.strftime("%Y-%m-%d %H:%M:%S %z"), datetime.timestamp())


