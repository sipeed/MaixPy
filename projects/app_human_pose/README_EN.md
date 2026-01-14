## Introduction
This application runs on MaixPy and implements human pose detection based on **YOLOv8-Pose** / **YOLO11-Pose**, capable of detecting 17 human key points. It can capture camera frames in real-time to identify and display human pose key points. With its simple operation and high efficiency, it is suitable for scenarios such as rapid human pose capture and basic motion analysis.

## Main Features
![](./assets/body_keypoints.jpg)
1.  **Device Compatibility:** Developed specifically for the MaixCam series. The **MaixCam2** utilizes the YOLO11 model, while the **MaixCam/Pro** utilizes the YOLOv8 model.
2.  **Real-time Camera Capture:** Automatically invokes the device camera to acquire high-definition real-time frames, with resolution automatically adapted to meet the requirements of the pose detection model.
3.  **Human Pose Detection & Recognition:** Based on the preloaded pose detection model, it automatically identifies human targets in the frame and filters results based on confidence thresholds.
4.  **Visualization of Results:** Annotates the real-time frame with bounding boxes, class labels, confidence scores, and draws connecting lines between key body points.
5.  **Automatic Detection of 17 Key Points:**
    ```
    1.  Nose
    2.  Left Eye
    3.  Right Eye
    4.  Left Ear
    5.  Right Ear
    6.  Left Shoulder
    7.  Right Shoulder
    8.  Left Elbow
    9.  Right Elbow
    10. Left Wrist
    11. Right Wrist
    12. Left Hip
    13. Right Hip
    14. Left Knee
    15. Right Knee
    16. Left Ankle
    17. Right Ankle
    ```

## More
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_human_pose)
[MaixCAM MaixPy Human Pose Keypoint Detection](https://wiki.sipeed.com/maixpy/doc/en/vision/body_key_points.html)