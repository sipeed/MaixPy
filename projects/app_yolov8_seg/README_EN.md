## 1. Introduction
This tool is an efficient visual detection application based on the YOLO11n_seg model. It is capable of performing object recognition, scoring, and segmentation mask rendering directly on the device without relying on external servers. Featuring a simple interface, smooth operation, and strong real-time performance, it is suitable for various on-site visual inspection and simple object recognition scenarios.

## 2. Main Features
1.  **Real-time Image Acquisition:** Automatically captures real-time frames via the device camera without manual triggering.
2.  **Object Recognition & Scoring:** Precisely identifies target objects in the frame, labels their categories, and outputs a confidence score between 0 and 1 (rounded to 2 decimal places).
3.  **Segmentation Mask Rendering:** Processes recognized targets with segmentation and renders dedicated masks to clearly distinguish the target from the background.
4.  **Bounding Box Annotation:** Marks the position of recognized targets with red rectangular boxes for intuitive understanding.
5.  **Quick Exit:** Provides a dedicated back button that supports touch input to quickly exit the application.

## 3. User Guide
![alt text](./assets/image.png)
1.  **Launch the Application:** After deploying the device, run the application. It will automatically initialize the camera, display module, YOLO11 recognition model, and touchscreen.
2.  **View Results in Real-time:** Once launched, the camera captures frames automatically, and the device screen displays:
    *   The original captured frame.
    *   Recognized targets annotated with red rectangular boxes.
    *   Text labels above targets in the format "Class: Confidence".
    *   Segmentation masks corresponding to the target areas.
    *   A back button icon in the top-left corner of the screen.
3.  **Exit the Application:** Directly touch the back button icon in the top-left corner of the screen. The application will receive the exit command and close automatically, returning to the device's main menu or initial state.
4.  **View Errors:** If a fault occurs during operation, the screen will automatically switch to a black background displaying white error logs for troubleshooting.

## 4. Notes
1.  **Shooting Environment Requirements:**
    *   Use in well-lit environments with sufficient light. Avoid backlighting or dark conditions, as this will reduce recognition accuracy and segmentation quality.
    *   Maintain an appropriate distance between the camera and the target object; avoid being too close or too far to prevent recognition failure.
    *   Minimize irrelevant background objects and avoid overlapping targets to improve recognition efficiency.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_yolo_obb)

[MaixCAM MaixPy Image Segmentation](https://wiki.sipeed.com/maixpy/doc/en/vision/segmentation.html)