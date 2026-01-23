## 1. Introduction
This tool utilizes the YOLO11 OBB (Oriented Bounding Box) algorithm model to perform precise recognition, confidence assessment, and angle detection of objects within the camera's view. It features a simple operational interface and can be launched quickly without complex configurations.

## 2. Main Features
![alt text](./assets/images.png)
1. **Real-time Image Acquisition:** Automatically captures real-time scene frames through the device camera without manual triggering.
2. **Oriented Object Detection:** Uses the YOLO11n_obb model to detect objects and output oriented bounding boxes with angles. Compared to standard rectangular boxes, these fit irregular or rotated objects much more accurately.
3. **Detection Information Visualization:** Real-time display of object class, confidence score (2 decimal places), and object rotation angle (1 decimal place). The oriented bounding box is drawn with red lines.
4. **One-Click Exit:** Provides a visual back button that supports touch operation to quickly exit the application, improving user convenience.
5. **Exception Handling:** If an exception occurs during operation, it is automatically caught and detailed error information is displayed to facilitate troubleshooting.

## 3. User Guide
1. **Launch Application:** Run the application directly without additional parameters. The app will automatically initialize the camera, display, YOLO11 detector, and touchscreen.
2. **View Detection Results:** After launching, the camera automatically captures frames. The display shows the original feed along with detection results, including the oriented bounding box, class, confidence, and angle information.
3. **Exit Application:** Locate the back icon in the top-left corner of the display and tap the icon area to quickly exit and terminate the application.

## 4. Notes
**Detection Parameters:** The application defaults to a confidence threshold of 0.5, an IOU threshold of 0.45, and a keypoint threshold of 0.5. Objects falling below these thresholds will not be detected or displayed. Modifying the internal application parameters is required to adjust these values.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_yolo_obb)

[Oriented Detection (OBB)](https://wiki.sipeed.com/maixpy/doc/en/vision/detect_obb.html)