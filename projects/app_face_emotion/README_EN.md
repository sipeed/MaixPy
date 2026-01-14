## Introduction
This program implements real-time face capture and emotional state determination based on the YOLOv8 face detection model and a dedicated facial emotion classification model. It requires no complex additional configuration and is ready to use out of the box, making it suitable for rapid verification of facial emotion scenarios, auxiliary simple human-computer interaction, and other use cases.

## Key Features
1.  **Real-time Face Detection**: Using the lightweight YOLOv8 face detection model, it can quickly identify and locate face regions from real-time images captured by the camera, supporting simultaneous detection of multiple faces.
2.  **Facial Emotion Classification**: After cropping and preprocessing the detected faces, the dedicated emotion classification model completes emotion determination and outputs corresponding emotion labels along with confidence scores.
3.  **Detailed Result Display**:
    -  For the first detected face, it displays a visual progress bar of all emotion categories and their corresponding confidence levels, intuitively presenting the judgment probability of each emotion type.
    -  For all detected faces, it marks the face bounding box, the optimal matching emotion label, and the confidence level, with color differentiation (green for high confidence and red for low confidence).
4.  **Simple Human-Computer Interaction**: It supports touch screen operation and provides functions of return/exit and model switching to meet the usage requirements in different scenarios.
5.  **Interface Auxiliary Elements**: Built-in return icon and model status display make the interface concise and easy to understand, allowing users to view results without professional operation experience.

## Usage Instructions
![](./assets/face_emotion_neutral.jpg)
1.  **Launch the Program**: After launching, the program will automatically initialize the camera, display screen, and model, and enter the real-time detection interface.
2.  **View Results**:
    -  Align the camera with the face region; the program will automatically detect the face and perform emotion classification, refreshing the results on the display screen in real time.
    -  View the detailed full emotion confidence of the first face, as well as the quick annotation results of all faces. Results with confidence reaching the set threshold will be displayed with green annotations, while those below the threshold will be displayed with red annotations (for reference only and not representing valid emotion determination).
3.  **Touch Screen Operation**:
    -  **Model Switching**: Click the rectangular area at the bottom of the display screen that shows the current model name. The program will prompt "switching model ...", and refresh the detection results after completing the model switching (7-category emotion model is currently supported).
    -  **Exit the Program**: Click the return icon in the upper left corner of the display screen to trigger the program exit process and close the application.

## Notes
1.  **Usage Environment Requirements**:
    -  It is recommended to use the program in well-lit and stable environments. Dim light, direct strong light, or severe jitter will reduce the accuracy of face detection and the effect of emotion classification.
    -  The face should be facing the camera directly at a moderate distance. Excessive occlusion (such as masks and sunglasses) will affect the detection and classification results.
2.  **Confidence Threshold Explanation**: The program has built-in detection confidence and emotion confidence thresholds. Results below the thresholds will be marked in red, which are for reference only and do not represent valid emotion determination.

## More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_face_emotion)
[MaixCAM MaixPy Facial Expression Recognition, Gender, Mask, Age, and More](https://wiki.sipeed.com/maixpy/doc/eh/vision/face_emotion.html)