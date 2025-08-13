'''
    Mahony AHRS get device euler angle demo.
    Full Application code see:
    https://github.com/sipeed/MaixPy/tree/main/projects/app_imu_ahrs
'''

from maix import ahrs, app, time
from maix.ext_dev import imu

# P of PI controller, a larger P (proportional gain) leads to faster response,
# but it increases the risk of overshoot and oscillation.
kp = 2

# I of PI controller, a larger I (integral gain) helps to eliminate steady-state errors more quickly,
# but it can accumulate error over time, potentially causing instability or slow drift.
ki = 0.01

# Force calibrate first
calibrate_first = False


# default config: acc +-2g 1KHz, gyro +-256rad/s 8KHz
sensor = imu.IMU("", mode=imu.Mode.DUAL,
                                    acc_scale=imu.AccScale.ACC_SCALE_2G,
                                    acc_odr=imu.AccOdr.ACC_ODR_1000,
                                    gyro_scale=imu.GyroScale.GYRO_SCALE_256DPS,
                                    gyro_odr=imu.GyroOdr.GYRO_ODR_8000)
ahrs_filter = ahrs.MahonyAHRS(kp, ki)

# for gyro have bias, we need to calibrate first
if calibrate_first or not sensor.calib_gyro_exists():
    print("\n\nNeed calibrate fisrt")
    print("now calibrate, please !! don't move !! device, wait for 10 seconds")
    # calib_gyro will auto calculate and save bias,
    # the next time use load_calib_gyro load
    sensor.calib_gyro(10000)
else:
    sensor.load_calib_gyro()

# time.sleep(3)
last_time = time.ticks_s()
while not app.need_exit():
    # get imu data
    data = sensor.read_all(calib_gryo = True, radian = True)

    # calculate angles
    t = time.ticks_s()
    dt = t - last_time
    last_time = t
    # print(f"{data.mag.x:8.2f}, {data.mag.y:8.2f}, {data.mag.z:8.2f}, {data.gyro.z:8.2f}")
    angle = ahrs_filter.get_angle(data.acc, data.gyro, data.mag, dt, radian = False)

    #  ^z  / y(front)
    #  |  /
    #  | /
    #  . ————————> x(right)
    # this demo's axis

    # x axis same with camera
    # angle.y -= 90

    print(f"pitch: {angle.x:8.2f}, roll: {angle.y:8.2f}, yaw: {angle.z:8.2f}, dt: {int(dt*1000):3d}ms, temp: {data.temp:.1f}")

    # time.sleep_ms(1)
