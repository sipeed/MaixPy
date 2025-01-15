---
title: MaixCAM MaixPy Hand Gesture Classification Based on Hand Keypoint Detection
---

## Introduction

The `MaixCAM MaixPy Hand Gesture Classification Based on Hand Keypoint Detection` can classify various hand gestures.

The current dataset used is the `14-class static hand gesture dataset` with a total of 2850 samples divided into 14 categories.  
[Dataset Download Link (Baidu Netdisk, Password: 6urr)](https://pan.baidu.com/s/1Sd-Ad88Wzp0qjGH6Ngah0g)

![](../../assets/handposex_14class.jpg)

This app is implemented in `MaixPy/projects/app_hand_gesture_classifier/main.py`, and the main logic is as follows:

1. Load the `14-class static hand gesture dataset` processed by the **Hand Keypoint Detection** model, extracting `20` relative wrist coordinate offsets.  
2. Initially train on the first `4` classes to support basic gesture recognition.  
3. Use the **Hand Keypoint Detection** model to process the camera input and visualize classification results on the screen.  
4. Tap the top-right `class14` button to add more samples and retrain the model for full `14-class` gesture recognition.  
5. Tap the bottom-right `class4` button to remove the added samples and retrain the model back to the `4-class` mode.  
6. Tap the small area between the buttons to display the last training duration at the top of the screen.  
7. Tap the remaining large area to show the currently supported gesture classes on the left side—**green** for supported, **yellow** for unsupported.  

## Demo Video

<video playsinline controls autoplay loop muted preload src="/static/video/hand_gesture_demo.mp4" type="video/mp4">
Classifier Result Video
</video>

1. The video demonstrates the `14-class` mode after executing step `4`, recognizing gestures `1-10` (default mapped to other meanings), **OK**, **thumbs up**, **finger heart** (requires the back of the hand, hard to demonstrate in the video but can be verified), and **pinky stretch**—a total of `14` gestures.

2. Then, step `5` is executed, reverting to the `4-class` mode, where only gestures **1**, **5**, **10** (fist), and **OK** are recognizable. Other gestures fail to produce correct results. During this process, step `7` was also executed, showing the current `4-class` mode—only the first 4 gestures are green, and the remaining 10 are yellow.

3. Step `4` is executed again, restoring the `14-class` mode, and previously unrecognized gestures in the `4-class` mode are now correctly identified.

4. Finally, dual-hand recognition is demonstrated, and both hands' gestures are accurately recognized simultaneously.

## Others

The demo video captures the **maixvision** screen preview window in the top-right corner, matching the actual on-screen display.

For detailed implementation, please refer to the source code and the above analysis.

Further development or modification can be directly done based on the source code, which includes comments for guidance.

If you need additional assistance, feel free to leave a message on **MaixHub** or send an email to the official company address.
