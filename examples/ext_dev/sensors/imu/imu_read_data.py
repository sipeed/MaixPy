from maix.ext_dev import imu

# Force calibrate first
calibrate_first = False

# default config: acc +-2g 1KHz, gyro +-256rad/s 8KHz
sensor = imu.IMU("qmi8658", mode=imu.Mode.DUAL,
                              acc_scale=imu.AccScale.ACC_SCALE_2G,
                              acc_odr=imu.AccOdr.ACC_ODR_1000,
                              gyro_scale=imu.GyroScale.GYRO_SCALE_256DPS,
                              gyro_odr=imu.GyroOdr.GYRO_ODR_8000)

# for gyro have bias, we need to calibrate first
if calibrate_first or not sensor.calib_gyro_exists():
    print("\n\nNeed calibrate fisrt")
    print("now calibrate, please !! don't move !! device, wait for 10 seconds")
    # calib_gyro will auto calculate and save bias,
    # the next time use load_calib_gyro load
    sensor.calib_gyro(10000)
else:
    sensor.load_calib_gyro()

while True:
    data = sensor.read_all(calib_gryo = True, radian = False)
    msg = "acc: {:10.4f}, {:10.4f}, {:10.4f}, gyro: {:10.4f}, {:10.4f}, {:10.4f}, temp: {:4.1f}".format(
        data.acc.x, data.acc.y, data.acc.z,
        data.gyro.x, data.gyro.y, data.gyro.z,
        data.temp
    )
    print(msg)
