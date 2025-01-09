from maix.ext_dev import imu

i = imu.IMU("qmi8658", mode=imu.Mode.DUAL,
                              acc_scale=imu.AccScale.ACC_SCALE_2G,
                              acc_odr=imu.AccOdr.ACC_ODR_8000,
                              gyro_scale=imu.GyroScale.GYRO_SCALE_16DPS,
                              gyro_odr=imu.GyroOdr.GYRO_ODR_8000)

while True:
    data = i.read()
    print("\n-------------------")
    print(f"acc x: {data[0]}")
    print(f"acc y: {data[1]}")
    print(f"acc z: {data[2]}")
    print(f"gyro x: {data[3]}")
    print(f"gyro y: {data[4]}")
    print(f"gyro z: {data[5]}")
    print(f"temp: {data[6]}")
    print("-------------------\n")
    

