## 1. Introduction
This application is a hand keypoint detection tool developed based on Maix series hardware. It can real-time identify hands in the frame and locate hand keypoints, while visually displaying detection results, keypoint trajectories, and hand angles. It is suitable for scenarios such as hand motion analysis and simple gesture interaction.

## 2. Main Features
1.  **Real-time Hand Detection**: The camera captures frames in real-time, automatically identifies hand targets in the frame, and labels the hand category along with confidence scores.
2.  **Keypoint Visualization**: Precisely draws hand keypoints and bone connections to intuitively display hand morphology.
3.  **Trajectory Tracking**: Records the positions of hand keypoints from the last 10 frames to draw movement trajectories. Supports trajectory lines between the fingertips of both hands.
4.  **Angle Display**: Displays the real-time detected hand angle (in degrees) within the hand region.
5.  **Model Switching**: Supports quick switching between different hand detection models to adapt to varying hardware performance requirements.
6.  **Quick Exit**: Provides a one-click exit function for convenient operation.

## 3. User Guide
### 3.1 Starting the Application
After deploying the application to the MaixCam device, simply run the program to start it. Once started, the camera turns on automatically and enters the real-time detection interface.

### 3.2 Interface Element Description
*   **Exit Application**: Touch the back icon area in the upper left corner of the screen to immediately exit the application.
*   **Switch Detection Model**: Touch the "model: X" rectangular area on the lower left of the screen to cycle through available hand detection models. A "switching model ..." prompt will appear during the switch, and detection will resume automatically upon completion.
*   **Hand Labeling**: When a hand is recognized, the hand category and confidence score are displayed (Red/Green text distinguishes between different hands).
*   **Keypoints & Bones**: Lines connect hand keypoints to form a hand bone contour, and a rectangular box labels the hand region.
*   **Angle Value**: The number displayed in the hand region is the currently detected hand angle.
*   **Trajectory Lines**: Red/Green lines represent the movement trajectory of a single hand; yellow lines represent the connection between the fingertips of both hands.
*   **Model Indicator**: "model: X" is displayed at the bottom of the screen, where X is the number of the currently used model.

## 4. Notes
1.  **Detection Range**: Please place your hand in the central area of the camera frame, ideally 30-80cm away from the camera, to ensure detection accuracy.
2.  **Environmental Requirements**: Avoid environments with direct strong light or excessive darkness, as this may reduce detection accuracy.
3.  **Trajectory Clearing**: If a hand is not detected for more than 3 seconds, its corresponding trajectory will be automatically cleared.
4.  **Model Description**: The built-in hand detection models are optimized for MaixCam hardware. Different model versions (such as bf16 format) have different focuses on detection speed and precision and can be switched according to actual needs.
5.  **Adjustable Parameters**: Parameters in the code (such as detection confidence threshold, trajectory recording length, etc.) can be modified according to usage scenarios to adapt to different detection requirements.
6.  **Expandability**: This application can serve as a basic module for hand interaction and can be extended to implement advanced functions such as gesture control, hand motion recognition, and touchless operation.
7.  **Performance Optimization**: If the detection frame rate is low, prioritize switching to a model in bf16 format (MaixCam/Pro only) or lower the camera resolution to improve speed.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_hand_landmarks)

[MaixPy MaixCAM Hand 21 Keypoint 3D Coordinate Detection](https://wiki.sipeed.com/maixpy/doc/en/vision/hand_landmarks.html)