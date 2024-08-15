---
title: MaixCAM MaixPy 2轴舵机云台人脸追踪
update:
  - date: 2024-06-11
    author: iawak9lkm
    version: 1.0.0
    content: 初版文档
---

阅读本文前，确保已经知晓如何开发MaixCAM，详情请阅读[快速开始](../README.md)

[源码地址](https://github.com/sipeed/MaixPy/blob/main/projects/app_face_tracking)

[APP下载地址](https://maixhub.com/app/31)

## 简介

基于 MaixCAM 和云台的人脸追踪程序。实际效果如下图所示：

![](../../assets/face_tracking1.jpg)


![](../../assets/face_tracking2.jpg)

## 如何使用例程

* 组装好您的云台和MaixCAM。

* 修改 `main.py` 中的参数。

  修改每个舵机使用的 MaixCAM 引脚，指定的引脚必须具备 PWM 功能。`servos.Servos` 会自行将该引脚配置为 PWM 功能。

  ```python
  ROLL_PWM_PIN_NAME = "A17"
  PITCH_PWM_PIN_NAME = "A16"
  ```

  修改两个舵机的初始位置。

  ```python
  init_pitch = 80         # init position, value: [0, 100], means minimum angle to maxmum angle of servo
  init_roll = 50          # 50 means middle
  ```

  修改两个舵机各自的活动范围的最小最大 PWM 占空比。请注意，某些云台结构中的舵机超出物理限制的最大活动范围时可能会造成不可预期的后果，请务必保证以下设定值对应的舵机运动范围内无阻碍。

  ```python
  PITCH_DUTY_MIN  = 3.5   # The minimum duty cycle corresponding to the range of motion of the y-axis servo.
  PITCH_DUTY_MAX  = 9.5   # Maximum duty cycle corresponding to the y-axis servo motion range.
  ROLL_DUTY_MIN   = 2.5   # Minimum duty cycle for x-axis servos.
  ROLL_DUTY_MAX   = 12.5  # Maxmum duty cycle for x-axis servos.
  ```

  选择舵机的运动方向。

  ```python
  pitch_reverse = False                   # reverse out value direction
  roll_reverse = True                     # reverse out value direction
  ```

* 最后执行代码即可。

  如果您是从 MaixHub 上安装的应用,在启动器中点击 face_tracking 即可执行本程序。

  如果您是从 Github 上获取的源码, 您可以在 [MaixVision](https://wiki.sipeed.com/maixvision) 中导入该工程的文件夹执行整个工程即可。 MaixVision详情请参考 [MaixVision说明](https://wiki.sipeed.com/maixpy/doc/zh/basic/maixvision.html)。

  当然您也可以将整个工程文件夹通过您喜欢的方式拷贝到我们的 MaixCAM 上, 然后用 python 执行。

* 想要退出程序按左上角的按钮即可。

  ![](../../../../projects/app_face_tracking/assets/exit.jpg)

## 常见问题

* 人脸跟踪效果不理想。

  不同的云台使用的 PID 参数不尽相同，您可以通过调节 PID 值来使得追踪效果更丝滑。

  ```python
  pitch_pid = [0.3, 0.0001, 0.0018, 0]    # [P I D I_max]
  roll_pid  = [0.3, 0.0001, 0.0018, 0]    # [P I D I_max]
  ```

* 在完成跟踪后，云台对着不动的人脸小幅度左右抖动一段时间。

  通常可以通过调节 PID 来使得该影响尽可能小；但是无法避免云台物理结构带来的抖动。可以尝试调节死区来减小抖动。

  ```python
  target_ignore_limit = 0.08
  # when target error < target_err_range*target_ignore_limit , set target error to 0
  ```

* 显示屏显示或终端打印 `PIN: XXX does not exist`。

  这是因为 MaixCAM 板子上引出的引脚中并不存在该引脚，请在 MaixCAM 上选择一个带 PWM 功能的引脚。

* 显示屏显示或终端打印 `Pin XXX doesn't have PWM function`。

  这是因为 MaixCAM 板子上引出的这个引脚没有 PWM 功能，请选择一个带 PWM 功能的引脚。


## 如何追踪其他物体

* 在 `main.py` 中存在一个类 `Target`，该类用于自定义需要追踪的目标。

* 在 `__init__` 中，请初始化您需要用到的对象，比如摄像头等。

* 在 `__get_target()` 中，您需要计算出被追踪物体的中心点，如果帧中不存在被追踪物体，请返回 -1,-1 以确保程序在未找到目标时暂时不做动作。同时，您也需要在返回坐标点之前调用 `self.__exit_listener(img)` 和 `self.disp.show(img)` 确保程序能够与您正常的完成交互。