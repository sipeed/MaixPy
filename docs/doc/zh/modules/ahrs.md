---
title: MaixCAM MaixPy 读取 IMU 加速度计和角速度计进行姿态解算
update:
  - date: 2025-07-08
    author: neucrack
    version: 1.0.0
    content: 增加姿态解算代码支持和文档
---


## IMU 简介

IMU（Inertial Measurement Unit），即 惯性测量单元，通常由几部分组成：
* 加速度计：测量线性加速度，包括重力加速度。
* 陀螺仪：测量角速度（绕轴的转动）。
* 磁力计（可选）：测量磁场方向，用于辅助航向角（Yaw）计算。

利用这几个传感器的数据，我们可以计算出设备的姿态，沿着设备三个轴旋转的角度，也叫欧拉角。
比如我们的设备如下图， `z`轴朝上， `y`轴朝前， `x`轴朝右，这是一个右手坐标系：

```
 ^z  / y(front)
 |  /
 | /
 . ————————> x(right)
```
这里以`x`为轴心旋转的角度就叫`俯仰角`（`pitch`）。
这里以`y`为轴心旋转的角度就叫`横滚角`（`roll`）。
这里以`z`为轴心旋转的角度就叫`偏航角`（`yaw`）。

这样一个传感器+读取+姿态解算+输出的系统我们可以称为`AHRS`(	Attitude and Heading Reference System/ 姿态与航向参考系统)。


得到这三个角就知道了我们的设备先在是什么姿态了，就可以用在很多场景，比如：
* 无人机
* 平衡车
* 机器人
* 体感控制
* 防抖
* 方向检测，震动检测
* 动作判断，手势识别，行为分析（还可以结合AI模型使用）



## 硬件支持

部分设备内置了 IMU，如下：

| 设备名 | 传感器型号 | 加速度计 | 陀螺仪 | 磁力计 | 接口 | 特点 |
| ----- | ----- | ------- | ----- | ---- | ---- | ---  |
| MaixCAM-Pro | QMI8658 | ✅ | ✅ | ❌ | IIC4<br>地址 0x6B | 低功耗<br>高稳定性<br>高灵敏度 |
| MaixCAM | 无板载 ❌ | ❌ | ❌ | ❌ | |  |  |
| MaixCAM2 | LSM6DSOWTR | ✅ | ✅ | ❌ | 内置驱动 | 低功耗<br>高稳定性<br>高灵敏度 |

除了使用内置的，你也可以自己外接一个 IMU 传感器，比如经典的`MPU6050/MPU9150`等，可自行查找最新和合适的传感器。

MaixPy 中姿态解算和 IMU 驱动是分开的，所以你可以自己外接传感器驱动，仍然可以调用姿态解算算法。



## MaixPy 读取 IMU 数据

以 MaixCAM-Pro 为例，使用 `maix.imu.IMU` 读取：

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

这里构造了一个`IMU`对象，然后调用`read_all`读取数据，再打印。
由于板载IMU没有 磁力计，这里没有打印。



不过这里有一点需要注意，那就是校准数据，下面进行说明。

## 数据校准

### 陀螺仪校准

为什么需要校准陀螺仪：
如果不校准， 设备静止时我们认为陀螺仪未转动，几 `gyro` `x, y, z` 三个轴均应该为`0`，但是实际我们会发现有误差，即使静止也会有值。这也叫`零飘`。

上面的代码可以看到，第一次需要进行一次`calib_gyro`，这是对陀螺仪数据进行一次校准，原理很简单：
所以我们连续采集多次求平均值，并记录下来（这里`calib_gyro(10000)`采集了`10s`并且将计算过后的值保存到了`/maixapp/share/misc`目录下。
下次我们用`load_calib_gyro`方法就会从这个文件加载了，而不用每次都校准。

然后在读取数据时`read_all(calib_gryo = True)`，内部会读取数据后自动减去偏差值再返回，当然你也可以是设置`calib_gyro = False`然后自己手动减。


### 加速度校准

理论加速度也是需要校准的，但是影响不如陀螺仪那么大，本文不进行说明，可自行搜索学习。

### 磁力计校准

同样，磁力计也需要校准，比如常见的椭球校准法，本文不进行说明，可自行搜索学习。


## 姿态解算

得到传感器数值后，通过一个姿态解算算法就能得到设备的姿态角度（欧拉角）。

### 解算原理简介

* 理论上我们用陀螺仪即可知道相对上一时刻旋转了多少度，即 `角速度 * 时间dt = 旋转角度`。不过只能短时间信任，由于陀螺仪精度问题，时间长了会累积误差。
* 加速度计的原理其实是测量重力G，由于重力可以认为方向和大小恒定，当设备静止或者匀速时，通过加速度计我们可以知道设备的相对于大地坐标系的绝对旋转角度。
  所以我们利用这个特性，长时间上用加速度测量的角度作为基准，短时间相信陀螺仪，他们互补。
* 但是当设备沿着垂直于重力的方向旋转，加速度计就无法检测到了，所以只能靠陀螺仪，时间长了可能就会有误差（漂移）。
* 所以一般可以利用磁力计，因为磁力计指向地球南北，刚好弥补了加速计的问题。


### 姿态解算算法

算法有很多，MaixPy 内置了一个 **Mahony 互补滤波** 算法，精简快速， 使用方法：
完整代码在 [MaixPy/examples/ext_dev/sensors/imu/imu_ahrs_mahony.py](https://github.com/sipeed/MaixPy/tree/main/examples/ext_dev/sensors/imu) 中
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

可以看到，通过`get_angle`函数，将原始数据传入即可得到欧拉角，磁力计没有默认全为 0 即可。

这里可能你也注意到了有一个 `PI` 控制器，用来调节灵敏度，可以自己尝试不同值看效果（可以自行学习 PID 概念和参数确定方法）：
* `kp`: PI 控制器的 P。值越大响应越快，不过容易超调。
* `ki`: PI 控制器的 I。值越大响应越快，不过太大会导致不稳定和漂移。

以及初始化时其它参数，比如陀螺仪测量范围默认是`[-256degree/s, 256degree/s]`，如果你旋转速度过大超过这个范围就会出现转了 100度但是只检测到转了 60度这种情况。
所以参数都要根据你际应用场景进行修改，另外不同参数可能灵敏度和噪声也会不同。

## API 文档

有关 IMU API 的详细说明请看 [IMU API 文档](../../../api/maix/ext_dev/imu.md)。
有关 AHRS API 的详细说明请看 [AHRS 文档](../../../api/maix/ahrs.md)。




