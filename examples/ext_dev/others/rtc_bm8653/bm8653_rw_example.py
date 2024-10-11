from maix import ext_dev, pinmap, err, time

### Enable I2C
# ret = pinmap.set_pin_function("PIN_NAME", "I2Cx_SCL")
# if ret != err.Err.ERR_NONE:
#     print("Failed in function pinmap...")
#     exit(-1)
# ret = pinmap.set_pin_function("PIN_NAME", "I2Cx_SDA")
# if ret != err.Err.ERR_NONE:
#     print("Failed in function pinmap...")
#     exit(-1)

BM8653_I2CBUS_NUM = 4

rtc = ext_dev.bm8563.BM8563(BM8653_I2CBUS_NUM)

### 2020-12-31 23:59:45
t = [2020, 12, 31, 23, 59, 45]

# Set time
rtc.datetime(t)

while True:
    rtc_now = rtc.datetime()
    if rtc_now == []:
        print("Read failed, continue")
        continue
    print(f"{rtc_now[0]}-{rtc_now[1]}-{rtc_now[2]} {rtc_now[3]}:{rtc_now[4]}:{rtc_now[5]}")
    time.sleep(1)


