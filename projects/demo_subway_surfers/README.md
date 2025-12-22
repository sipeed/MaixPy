# README

通过视觉检测到姿态变化, 来完成地铁跑酷需要的动作. 支持maixcam/maixcam2, 以下统称为设备

## 使用方法

### 配置游戏环境


1. 将设备的usb接口连接到电脑
2. 打设备的HID Mouse功能, 打开方法是在设置应用->USB设置->选择device->勾选HID Mouse->点击确定
3. 在电脑上打开地铁跑酷游戏. 可以点击[这里](https://subtlexp.github.io/Subway-Surfers)用浏览器玩地铁跑酷

### 开始游戏

1. 打开应用后, 确保画面中存在玩家的膝盖到头部的区域
2. 玩家初始时需要站直, 肩膀保持自然水平, 裁判将设备对准玩家后点击BOOT键进行校准, 校准完成后设备会立即检测玩家姿态并操作鼠标.这时候在电脑上点击游戏开始
3. 玩家的操作方式是:
    - 向左旋转肩膀, 表示左移一次
    - 向右旋转肩膀, 表示右转一次
    - 跳跃, 表示跳跃一次
    - 蹲下, 表示蹲下一次
注意:
1. 判断左移和右移的标准是肩膀向左或者向右旋转的角度, 一般旋转角度超过10度后认为有效. 旋转后需要立马回正
2. 跳越和蹲下时由于身体需要一定时间反映, 因此有一定延时, 需要提前做预判动作


Complete the actions required for Subway Surfers by detecting posture changes through visual detection. Supports maixcam/maixcam2, collectively referred to as the device below.

## Usage
### Setting Up the Game Environment
1. Connect the device's USB interface to the computer.
2. Enable the HID Mouse function of the device. To do this, go to the Settings app -> USB Settings -> Select device -> Check HID Mouse -> Click OK.
3. Open the Subway Surfers game on the computer. You can click [here](https://subtlexp.github.io/Subway-Surfers) to play Subway Surfers in your browser.

### Starting the Game
1. After opening the application, ensure that the area from the player's knees to the head is visible in the frame.
2. The player should initially stand straight with their shoulders naturally level. The referee should aim the device at the player and press the BOOT key to calibrate. Once calibration is complete, the device will immediately detect the player's posture and control the mouse. At this point, click to start the game on the computer.
3. The player's controls are as follows:
- Rotate the shoulders to the left to move left once.
- Rotate the shoulders to the right to move right once.
- Jump to perform a jump.
- Crouch to perform a crouch.

Note:
1. The criteria for determining left and right movement are the angles of shoulder rotation to the left or right. Generally, a rotation angle exceeding 10 degrees is considered valid. After rotating, return to the original position immediately.
2. Due to the time required for the body to react, there is a certain delay when jumping and crouching. Preemptive actions are necessary.