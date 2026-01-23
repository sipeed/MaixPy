# YOLO-World Detection Application User Guide

## 1. Introduction
This application is a YOLO-World object detection demo running on the **MaixCam2** device. It supports specifying detection targets via voice input and automatically generates the necessary model features, enabling real-time visual detection of the specified object. No manual configuration changes or additional coding are required. The operation is concise and efficient, making it suitable for quickly implementing on-site detection of custom objects.

## 2. Main Features
1.  **Real-time Object Detection**: After loading the pre-configured model, it performs real-time detection on the specified target (default is "person"), drawing bounding boxes and displaying detection confidence scores.
2.  **Voice Input for Custom Classes**: Supports recording custom detection classes via a 3-second voice input (English only), with automatic speech-to-text recognition.
3.  **Automatic Model Feature Generation**: After confirming the custom class, the application automatically runs a script to generate the corresponding label file and text feature file, eliminating the need for manual model configuration.
4.  **One-click Model Switching**: Once the feature file is generated, the application automatically loads the corresponding scale YOLO-World model and switches to the real-time detection mode for the new target.
5.  **Simple Interactive Operation**: Provides visual buttons for back/exit, class confirmation/cancellation, and learning new objects, supporting touchscreen interaction for a user-friendly experience.

## 3. Usage Instructions
![alt text](./assets/image.png)
1.  **Startup and Basic Detection**: Ensure the device camera and microphone are functional and that relevant model files are pre-installed, then run the application directly. The program automatically completes initialization (including loading the model and speech recognition tools) and enters the real-time preview interface. The camera will automatically detect the default target, marking it with a red bounding box and displaying the confidence score.
2.  **Custom Target Learning**: Click the "Learn" button at the bottom of the preview interface. When prompted, clearly speak the **English name** of the target (e.g., "car") within 3 seconds. After recording, the application transcribes the speech and displays the result. Click "Yes" to confirm, and the app will automatically generate the feature file and switch to real-time detection mode for that target. Click "No" to discard.
3.  **Exit Application**: In any interface except during learning/transcription, click the back icon in the top-left corner of the screen to close the application normally and restore device configurations.

## 4. Notes
1.  **Hardware Requirements**: This application requires the **4GB RAM version** of the MaixCam. Devices with less than 4GB RAM cannot run it properly and will exit with a hardware incompatibility message.
2.  **Voice Input Limitations**: Only English target names are supported (Chinese and other languages are not). Record in a quiet environment to avoid noise affecting transcription accuracy, and ensure the name is spoken within 3 seconds.
3.  **Interaction Instructions**: This application only supports single touchscreen clicks; long presses have no additional function. Do not close the application or restart the device during the learning process (feature file generation) to avoid file corruption.
4.  **Resource Usage**: The application utilizes hardware resources such as the camera, microphone, and NPU. It is recommended to close other unrelated applications during runtime to avoid affecting detection performance and smoothness.
5.  **Error Handling**: If an error occurs, an error message will be displayed. Tapping anywhere on the screen will exit the application. You can check the device logs to troubleshoot specific issues.
6.  **File Storage Path**: Custom target label files (`.txt`) and feature files (`.bin`) are automatically saved to the `/root/models/my_yolo_world/` directory. These can be viewed and backed up using the device's file management tools.
7.  **Detection Parameters**: The default confidence threshold (`conf_th`) is 0.5, and the IOU threshold (`iou_th`) is 0.45. To adjust detection sensitivity, modify the corresponding parameters in the code (`detector.detect(img, conf_th=0.5, iou_th=0.45)`) and rerun the application.
8.  **Extended Functionality**: To support detection of multiple classes simultaneously, modify the logic related to voice input and feature generation to create a label file containing multiple classes and load the corresponding multi-class YOLO-World model.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_yoloworld)

[Using YOLO World Model on MaixPy MaixCAM2 for Detection of Any Target Without Training](https://wiki.sipeed.com/maixpy/doc/en/vision/yolo_world.html)