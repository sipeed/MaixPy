## 1. Introduction
This application is a speech-to-text tool developed for the MaixCAM2 hardware. It utilizes the SenseVoice speech recognition model to support voice recording via a long-press button and converts the recorded audio into text. It features simple operation and an intuitive interface.

## 2. Main Features
- **Voice Recording**: Start audio recording by long-pressing the designated button and stop by releasing it.
- **Speech-to-Text**: Automatically invokes the speech recognition model after recording stops to convert the audio content into text.
- **Interactive Interface**: Provides a visual interface that clearly displays the recording status, transcription results, and an exit button.
- **Hardware Compatibility Check**: Automatically detects the device memory specifications at startup. Only the 4GB version of the MaixCAM2 is supported.

## 3. Usage Instructions
### 3.1 Starting the Application
After deploying the application to the MaixCAM2 device, simply run the program to start it. During startup, the screen will sequentially display loading prompts such as "Init touchscreen," "Loading sensevoice module," and "Init asr model." Wait for the loading to complete to enter the main interface.

### 3.2 Core Operations
1.  **Record Voice**: Long-press the recording icon in the center of the screen (the 96x96 `record.png` icon). After holding for more than 100ms, the text area on the screen will display "Recording..", indicating that recording has started.
2.  **Stop Recording & Transcribe**: Release the recording icon. The text area will display "Transcribing ..." as the application automatically converts the audio to text. Once complete, the recognized text will appear in the text area.
3.  **Exit Application**: Click the exit icon in the upper-left corner of the screen (the 40x40 `exit.jpg` icon) to close the application.

### 3.3 Interface Description
- **Top-Left Corner**: Exit button; click to close the app.
- **Center Area**: Recording button + "Long press me" prompt text. Long-press to start recording.
- **Bottom Text Area**: Displays the recording status, transcription status, and final speech-to-text results. Initially displays "No text."

## 4. Notes
1.  **Model Loading**: Initializing the ASR model at startup may take a long time. The screen will display a loading progress (1-8). Please be patient and wait for it to finish; there is no need to exit midway.
2.  **Recording Operation**: The recording requires a long press of more than 100ms to trigger. A short tap will not start recording, which helps prevent accidental triggers.
3.  **File Dependencies**: The application relies on the model file located at a specific path (`/root/models/sensevoice-maixcam2/model.mud`). If this file is missing, the application will not run correctly.
4.  **Audio Parameters**: The recording sample rate is fixed at 16000Hz, mono. No manual setup is required. Modifying these parameters may cause transcription failure.
5.  **Recognition Language**: The application is set to recognize English (`en`) by default. This can be adjusted by modifying `self.language = 'en'` in the code to other supported languages (model compatibility required).
6.  **Audio Caching**: Audio data is temporarily stored in memory during recording and automatically cleared after transcription. Recording very long audio clips may consume significant memory; it is recommended to keep recordings under 1 minute.
7.  **Exception Handling**: The application automatically stops the ASR model and releases resources upon exit to prevent resource leaks caused by forced termination. If an exit signal (`app.need_exit()`) is triggered during operation, resources will also be cleaned up automatically.
8.  **Interaction Optimization**: Touch detection supports a 20px offset tolerance. Even if you do not click the icon area precisely, a slight offset will still trigger the operation, improving usability.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_speech)

[Running SenseVoice Model on MaixPy MaixCAM](https://wiki.sipeed.com/maixpy/doc/en/mllm/asr_sensevoice.html)

[Running Whisper Model on MaixPy MaixCAM](https://wiki.sipeed.com/maixpy/doc/en/mllm/asr_whisper.html)