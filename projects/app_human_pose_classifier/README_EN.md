## 1. Introduction

This is a real-time human pose detection and classification system based on YOLO vision, which can identify human body keypoints through a camera, automatically analyze and classify current posture types. The system uses the YOLO11 pose detection model to display detection results, posture classification, and scoring information in real-time.

## 2. Main Features

- **Real-time Pose Detection**: Captures video feed through camera and identifies human postures in real-time
- **Keypoint Annotation**: Marks keypoints on detected human bodies (such as head, shoulders, elbows, wrists, hips, knees, ankles, etc.)
- **Intelligent Pose Classification**: Automatically recognizes and classifies current postures (such as standing, sitting, squatting, lying down, etc.)
- **Pose Evaluation**: Performs quality scoring and normative analysis on detected postures
- **Detection Box Display**: Marks detected human body areas with red rectangular boxes
- **Confidence Display**: Shows detection result accuracy in real-time
- **Touch Return**: Supports touchscreen operation, tap the return button to exit the program

## 3. User Guide

### 3.1 Starting the Program
- After running the program, the system will automatically start the camera
- The screen will display the camera feed in real-time

### 3.2 Pose Detection and Classification
- Position your body completely within the camera's field of view
- Maintain an appropriate distance to ensure your full body can be captured
- The system will automatically detect and display on the screen:
  - **Red Rectangular Box**: Marks the detected human body position
  - **Keypoint Connections**: Displays the human skeletal structure
  - **Confidence Score**: Shows detection accuracy (value between 0-1)
  - **Pose Classification Result**: Displays the current posture type (such as "Standing", "Sitting", "Deep Squat", etc.)

![](./assets/image.png)

## 4. Precautions

- **Lighting Conditions**: Please use in well-lit environments for better detection and classification results
- **Camera Distance**: Recommended distance of 1.5-3 meters from the camera to ensure full body is in frame
- **Background Environment**: Choose a simple background to avoid complex backgrounds interfering with detection
- **Clothing Recommendations**: Wearing fitted or high-contrast clothing helps improve detection accuracy
- **Occlusion Issues**: Avoid blocking key body parts to prevent affecting detection and classification results
- **Pose Stability**: Maintain posture for 1-2 seconds to help the system accurately classify
- **Multi-person Detection**: The system can detect and classify multiple people simultaneously, but single-person use is recommended for optimal experience

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_human_pose_classifier)

[MaixCAM MaixPy Body Keypoint Pose Detection](https://wiki.sipeed.com/maixpy/doc/eh/vision/body_key_points.html)
