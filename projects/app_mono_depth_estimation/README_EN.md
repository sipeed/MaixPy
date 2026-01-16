## 1. Introduction
This tool is a real-time depth image detection application developed based on the Maix hardware platform. It captures real-time frames through the device camera and utilizes the `DepthAnything` model to rapidly process and generate corresponding depth-visualized images. It intuitively presents the distance information within a scene through color coding. With its simple operation and efficient performance, it is suitable for various scenarios requiring quick acquisition of scene depth information.

## 2. Main Features
1.  **Real-time Camera Capture:** Automatically invokes the device camera to acquire high-definition real-time scene frames without requiring manual configuration of camera parameters.
2.  **Depth Image Generation:** Relies on the `DepthAnything v2` model to process captured frames in real-time, generating depth-visualized images using a TURBO color map, where color differences correspond to the varying distances of objects in the scene.
3.  **Convenient Exit Function:** Provides a visualized back button that supports touch operation for quick application exit, eliminating the need for complex command input.
4.  **Exception Fault Tolerance:** The application includes a built-in exception capture and display mechanism. If issues arise during operation, error messages are automatically printed and displayed on the device screen to facilitate troubleshooting.

## 3. User Guide
1.  **Application Startup:** After powering on the pre-configured device, the application loads and runs automatically; no manual startup of additional programs is required.
2.  **Viewing Depth Images:** Once running, the device screen displays the depth-visualized image corresponding to the scene in real-time. You can intuitively distinguish the distance of objects by observing the image colors.
3.  **Exiting the Application:** A back button icon is displayed in the upper-left corner of the screen. Touching this icon area allows you to quickly exit the application and return to the device's initial interface.
![alt text](./assets/image.png)

## 4. Notes
1.  **Hardware Environment:** This tool is designed exclusively for dedicated hardware devices supporting the `maix` series libraries. It does not support running on regular computers or other non-compatible embedded devices.
2.  **Model File:** The model file `depth_anything_v2_vits.mud` must exist in the device's `/root/models/` directory. If missing, it can be downloaded separately.
3.  **Runtime Environment:** To avoid damaging configuration or model files, please refrain from powering off or force-restarting the device while the application is running.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_mono_depth_estimation)

[MaixCAM2 MaixPy Using Depth-Anything for Monocular Depth Estimation](https://wiki.sipeed.com/maixpy/doc/en/vision/depth_anything.html)

