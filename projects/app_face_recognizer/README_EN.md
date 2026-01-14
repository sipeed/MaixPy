## Introduction
This application is a face recognition tool designed for Maix devices (supporting MaixCam2, etc.). It integrates high-performance face detection and feature extraction models to achieve real-time face recognition, face information enrollment, and data clearing. The operation is concise and intuitive, allowing for quick use without complex configuration.

## Key Features
1.  **Real-time Face Detection & Recognition**: Captures real-time video through the device camera, automatically detects faces in the frame, performs identity matching, and displays the recognition results along with the confidence level.
2.  **Face Information Enrollment (Learning)**: Supports enrolling new/unknown faces into the system, generating a unique identity identifier for precise recognition in subsequent sessions.
3.  **Clear Enrolled Faces**: One-click clearing of all enrolled face information to restore the application to its initial state.
4.  **Quick Return/Exit**: Supports quickly exiting the current face recognition function and returning to the previous application interface.
5.  **Temporary Preview of Enrolled Faces**: After enrolling a new face, a temporary preview of the enrolled image is displayed in the upper-left corner to facilitate confirmation of the enrollment quality.

## User Guide
### Application Startup
After launching the application, the screen will first display a "loading ..." prompt while initializing the model, camera, and touchscreen hardware. Once loaded, it automatically enters the real-time face recognition interface, showing the live camera feed and three operation buttons.

### Interface Button Description
The application interface contains three core operation buttons, all supporting touch input:
1.  **< back Button** (Top-left): Return button, used to exit the current face recognition interface.
2.  **learn Button** (Bottom-left): Learn/Enroll button, used to register new face information.
3.  **clear Button** (Bottom-right): Clear button, used to erase all enrolled face information.
![](./assets/face_recognize.jpg)

### Specific Operation Steps
1.  **Real-time Face Recognition**: After the application loads, point the camera at the face to be recognized. The system will automatically frame the detected face, labeling it as a known identity (enrolled) or "Unknown," along with a matching confidence score (values closer to 1 indicate higher accuracy).
2.  **Enrolling a New Face**:
    *   Ensure the face to be enrolled is in the camera frame and successfully detected (a bounding box appears around the face).
    *   Click the "learn" button at the bottom-left of the touchscreen. The system automatically extracts the current facial features and completes the enrollment, generating a unique identifier in the format "id_XXX".
    *   Upon successful enrollment, a temporary preview of the face will appear in the upper-left corner (lasting 5 seconds). Subsequent appearances of this face in the frame will be automatically recognized and labeled with the corresponding "id_XXX".
    *   Repeat the above steps to enroll multiple faces; the system will automatically increment the identity identifier.
3.  **Clearing Enrolled Faces**: Directly click the "clear" button at the bottom-right. The system will automatically clear all enrolled face information, reverting to the initial state where only detection (not identification) is supported.
4.  **Exiting the Application**: Click the "< back" button at the top-left to exit the current interface and return to the previous application page.

## Notes
1.  Before starting the application, ensure the device camera is unobstructed and the touchscreen is functioning properly; otherwise, face detection and button operations may fail.
2.  When enrolling a face, please keep the face facing the camera directly with sufficient lighting and no strong backlighting. Avoid obstructions (such as masks or sunglasses) to improve the accuracy of enrollment and subsequent recognition.
3.  After enrollment, the system automatically saves face information to the device file "/root/faces.bin". Manual backup is not required, and the application will automatically load this data upon restarting (the relevant loading logic is reserved in the code and enables data persistence when activated).

## More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_face_recognizer)
[MaixCAM MaixPy Face Recognition](https://wiki.sipeed.com/maixpy/doc/en/vision/face_recognition.html)