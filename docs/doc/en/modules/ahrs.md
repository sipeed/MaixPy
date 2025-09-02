---
title: MaixCAM MaixPy Read IMU Accelerometer and Gyroscope for Attitude Estimation
update:
  - date: 2025-07-08
    author: neucrack
    version: 1.0.0
    content: Added attitude estimation code support and documentatio
---


## IMU Introduction

IMU (Inertial Measurement Unit) typically consists of several parts:

* Accelerometer: Measures linear acceleration, including gravitational acceleration.
* Gyroscope: Measures angular velocity (rotation around an axis).
* Magnetometer (optional): Measures magnetic field direction, used to assist in yaw calculation.

Using data from these sensors, we can calculate the device's attitude, the angles of rotation along its three axes, also known as Euler angles.
For example, in the following diagram, the `z` axis is up, the `y` axis is forward, and the `x` axis is right. This is a right-handed coordinate system:

```
 ^z  / y(front)
 |  /
 | /
 . ————————> x(right)
```

The rotation angle around the `x` axis is called `pitch`.
The rotation angle around the `y` axis is called `roll`.
The rotation angle around the `z` axis is called `yaw`.

A system of sensor + reading + attitude estimation + output can be called `AHRS` (Attitude and Heading Reference System).

With these three angles, we can determine the current orientation of our device, which can be used in many scenarios, such as:

* Drones
* Self-balancing vehicles
* Robots
* Motion control
* Anti-shake
* Direction and vibration detection
* Motion judgment, gesture recognition, behavior analysis (can be combined with AI models)

## Hardware Support

Some devices have a built-in IMU, as shown below:

| Device Name | Sensor Model | Accelerometer | Gyroscope | Magnetometer | Interface            | Features                                        |
| ----------- | ------------ | ------------- | --------- | ------------ | -------------------- | ----------------------------------------------- |
| MaixCAM-Pro | QMI8658      | ✅             | ✅         | ❌            | IIC4<br>Address 0x6B | Low power<br>High stability<br>High sensitivity |
| MaixCAM     | None ❌      | ❌             | ❌         | ❌            |                      |                                                 |
| MaixCAM2    | LSM6DSOWTR   | ✅             | ✅         | ❌            | Built-in driver      | Low power<br>High stability<br>High sensitivity |

Besides using the built-in IMU, you can also connect an external IMU sensor, such as the classic `MPU6050/MPU9150`. Search for the latest and suitable sensors yourself.

In MaixPy, attitude estimation and IMU drivers are separated, so you can use your own driver for external sensors and still call the attitude estimation algorithm.

## MaixPy Read IMU Data

Using MaixCAM-Pro as an example, use `maix.imu.IMU` to read:

```python
from maix.ext_dev import imu

# Force calibrate first
calibrate_first = False

# default config: acc +-2g 1KHz, gyro +-256rad/s 8KHz
sensor = imu.IMU("default", mode=imu.Mode.DUAL,
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
```

Here, an `IMU` object is constructed, then `read_all` is called to read and print the data.
Since the onboard IMU has no magnetometer, it's not printed.

However, note that calibration is needed, as explained below.

## Data Calibration

### Gyroscope Calibration

Why gyroscope calibration is needed:
If not calibrated, we assume the gyroscope reads `x, y, z = 0` when stationary, but in practice, there's an offset—known as "zero drift".

As shown in the code, we need to perform `calib_gyro` once, which calibrates the gyroscope data.
The principle is simple: collect multiple samples over time and average them.
Here, `calib_gyro(10000)` samples for 10s and saves the result in `/maixapp/share/misc`.
Next time, use `load_calib_gyro` to load the file, skipping recalibration.

When reading data, `read_all(calib_gryo = True)` will subtract the bias automatically. You can also set `calib_gyro = False` and handle it manually.

### Accelerometer Calibration

In theory, the accelerometer should also be calibrated, but its effect is less significant than the gyroscope. Not covered here—please refer to other resources.

### Magnetometer Calibration

Similarly, magnetometers need calibration, such as the common ellipsoid calibration. Not covered here—please search and learn.

## Attitude Estimation

Once we have sensor values, we can use an attitude estimation algorithm to obtain Euler angles.

### Basic Principles

* Theoretically, gyroscopes can tell how much rotation occurred since the last moment: `angular velocity * dt = rotation angle`. But due to drift, this is only reliable short-term.
* Accelerometers measure gravity. Since gravity is constant, when the device is still or moving at constant speed, we can use this to determine absolute orientation relative to the Earth.
  So we trust the accelerometer long-term and gyroscope short-term—they complement each other.
* However, if the device rotates around an axis perpendicular to gravity, the accelerometer can't detect it. In this case, only the gyroscope helps, but drift may occur over time.
* The magnetometer helps here since it points to Earth's magnetic north, making up for the accelerometer's blind spot.

### Attitude Estimation Algorithm

There are many algorithms. MaixPy includes the **Mahony complementary filter**—lightweight and fast.
Full code in [MaixPy/examples/ext\_dev/sensors/imu/imu\_ahrs\_mahony.py](https://github.com/sipeed/MaixPy/tree/main/examples/ext_dev/sensors/imu)

```python
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
```

As shown, use `get_angle` to input raw sensor data and get Euler angles. If there's no magnetometer, set it to all zero.

You may have noticed the use of a `PI` controller to adjust sensitivity. You can experiment with different values (learn about PID tuning):

* `kp`: Proportional gain. Higher values respond faster but risk overshoot.
* `ki`: Integral gain. Higher values eliminate errors faster but may cause instability or drift.

Other parameters, such as the gyroscope's default range of `[-256degree/s, 256degree/s]`, must be tuned for your scenario.
Exceeding the range (e.g., rotating 100° but detecting only 60°) causes errors.
Also, different settings affect sensitivity and noise levels.

## API Documentation

For details on IMU APIs, see [IMU API Documentation](../../../api/maix/ext_dev/imu.md).
For details on AHRS APIs, see [AHRS Documentation](../../../api/maix/ahrs.md).
