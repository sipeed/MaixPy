## 1. Introduction
This program is applicable to Maix series hardware devices such as Maixcam/Pro/2. It captures images via the camera and identifies hand movements using a hand keypoint detection model, converting the recognized hand position and pressing actions into HID touchpad commands to achieve contactless gesture control of a computer/device touchpad.

## 2. Main Features
- **Hand Position Tracking**: Real-time recognition of hand position in the frame, mapping it to absolute coordinates of the touchpad. Moving the hand synchronously controls the movement of the touchpad cursor.
- **Gesture Press Simulation**: Recognizes the closing/separation action of the thumb and middle finger to simulate the left-click press/release operation of the touchpad (press is triggered when the thumb and middle finger are close, and release when separated).
- **Automatic Reset**: Automatically cancels the press state if no hand is detected within 3 seconds to avoid misoperation.
- **Visual Feedback**: Displays the camera frame and hand keypoint detection results in real time for easy confirmation of recognition status.

## 3. Usage Instructions
### 3.1 Preparations
1. **USB HID Mode Settings**:
   - Enter the device's "Settings -> USB Settings -> HID Touchpad" and click Confirm to enable it;
2. **Model File Confirmation**: Ensure that the hand keypoint detection model file `hand_landmarks.mud` (or `hand_landmarks_bf16.mud`) exists in the `/root/models/` directory of the device.

### 3.2 Running the Program
1. Upload the program file to the device and execute it;
2. After the program starts, the camera will turn on automatically, and the frame will display hand detection results in real time;
3. Control Methods (the camera needs to be aimed at the user):
   - Moving the Hand: Move the hand within the detection area of the camera frame (10%~90% of the frame width, 10%~80% of the frame height), and the touchpad cursor will move synchronously;
   - Simulating a Click: Bring the thumb and middle finger together (the distance between the two points in the frame is less than the threshold) to trigger the left-click press of the touchpad; separate the fingers to release the press.

### 3.3 Exiting the Program
- Press the physical button of the device to exit, or terminate the program process through the device management interface.

## 4. Notes
1. **Environmental Requirements**: Ensure sufficient light during use and avoid strong/backlight, otherwise the hand recognition accuracy will be reduced;
2. **Recognition Range**: The hand must be within the detection area of the camera frame (10%~90% of the frame width, 10%~80% of the frame height); recognition may fail if out of this range;
3. **USB Connection**: The device must be connected to a computer/target device via a USB cable, and the HID Touchpad mode must be enabled correctly; otherwise, the program will prompt that HID is not ready, and an error will be reported if not connected to a computer;
4. **Model Compatibility**: Maixcam-pro uses the bf16 format model, while the regular Maixcam uses the default model. The program will adapt automatically, but ensure the corresponding model file exists;
5. **Misoperation Prevention**: If not in use for a long time, it is recommended to exit the program to prevent unnecessary touchpad operations triggered by the hand accidentally entering the detection area;
6. **Adjustable Parameters**:
   - `SHOW_IMG`: Controls whether to display the camera frame (enabled by default);
   - `DEBUG_MODE`: Forces frame display when enabled, facilitating debugging;
   - `detect_roi`: Adjusts the hand detection area (in percentage units), which can be optimized according to usage scenarios;
   - `target_screen_roi`: Adjusts the screen area mapped by touchpad coordinates to adapt to different display devices;
7. **Extended Functions**: The program reserves a keyboard key sending interface (`send_keys` function), which can extend more gesture commands (such as sliding, scrolling, shortcut keys, etc.) based on hand keypoint recognition;
8. **Image Quality Adjustment**: The `trans_img_quality` parameter can adjust the frame transmission quality. A lower value results in poorer image quality but faster transmission speed, which can be adjusted according to network/device performance.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_usb_hand_touch)