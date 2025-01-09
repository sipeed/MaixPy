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

QMI8658_I2CBUS_NUM = 4

imu = ext_dev.qmi8658.QMI8658(QMI8658_I2CBUS_NUM,
                              mode=ext_dev.imu.Mode.DUAL,
                              acc_scale=ext_dev.imu.AccScale.ACC_SCALE_2G,
                              acc_odr=ext_dev.imu.AccOdr.ACC_ODR_8000,
                              gyro_scale=ext_dev.imu.GyroScale.GYRO_SCALE_16DPS,
                              gyro_odr=ext_dev.imu.GyroOdr.GYRO_ODR_8000)

while True:
    data = imu.read()
    print("\n-------------------")
    print(f"acc x: {data[0]}")
    print(f"acc y: {data[1]}")
    print(f"acc z: {data[2]}")
    print(f"gyro x: {data[3]}")
    print(f"gyro y: {data[4]}")
    print(f"gyro z: {data[5]}")
    print(f"temp: {data[6]}")
    print("-------------------\n")

