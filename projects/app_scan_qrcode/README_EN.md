## 1. Introduction
This tool is a visual recognition application running on the MaixCam device. It enables real-time recognition and data reporting of barcodes, QR codes, and AprilTags (TAG36H11). The application features an intuitive touch interface, and recognition results are sent via the device's default communication module (UART by default), facilitating subsequent data integration and processing.

## 2. Main Features
1.  **Multi-type Visual Code Recognition:** Supports three formats: Barcode, QR Code, and AprilTag (TAG36H11).
2.  **Real-time Visual Feedback:** During recognition, the target position is marked on the screen, detailed results are displayed, and dynamic prompts for the recognition area are provided.
3.  **Touch-based Mode Switching:** Quickly switch between the three recognition modes using the touch buttons at the bottom of the screen.
4.  **Data Communication Reporting:** Upon successful identification of a valid target, the result is automatically reported via the communication module (default UART).
5.  **Quick Exit Function:** Provides a quick exit entry at the top of the screen to easily terminate the application.

## 3. User Guide

### 3.1 Running the Program
Open the program to start scanning automatically.

![](./assets/image.png)

### 3.2 Switching Recognition Modes
The program defaults to QR Code recognition mode. You can switch modes using the three touch buttons at the bottom of the screen:
1.  **Left Button:** Switch to Barcode recognition mode.
2.  **Middle Button:** Switch to QR Code recognition mode.
3.  **Right Button:** Switch to AprilTag (TAG36H11) recognition mode.
4.  The selected button will be highlighted in dark color, and a corresponding prompt will appear at the top of the screen.

### 3.3 Performing Target Recognition
1.  After switching to the desired mode, place the Barcode/QR Code/AprilTag within the blue boxed recognition area in the center of the screen.
2.  The device captures images in real-time. Upon success, the target is marked with a red rectangle (or corner lines), and details are displayed (content for Barcodes/QR Codes; ID, Family, and Coordinates for AprilTags).
3.  *Scan the qrcode in camera screen and send the result of the qrcode from the communication module(Default is uart).*

### 3.4 Viewing Reported Data
1.  After successful recognition, the result is sent via the communication module. The default protocol is UART with a baud rate of 115200.
2.  Use `app.get_sys_config_kv("comm", "method")` to check the current communication protocol.
3.  **Example:**
    1.  Put the qrcode in the camera, and you will see the qrcode is marked by a rectangle.
    2.  Check the data sent by the communication module.
    ```shell
    # uart data
    AA CA AC BB 0D 00 00 00 E1 05 31 32 33 34 35 36 37 38 39 1A 15
    # 31 32 33 34 35 36 37 38 39： means the qrcode is "123456789"
    ```
4.  Barcode data is reported in a similar format, while AprilTag reports structured data including family, ID, and coordinates.

### 3.5 Exiting the Program
1.  Click the exit icon at the top of the screen; the icon will highlight, and a countdown begins.
2.  After a short wait (count exceeds 2 frames), the program automatically terminates, clears the screen, and exits.

## 4. Notes
1.  Keep the device stable during scanning. Maintain an appropriate distance from the target; avoid being too close, too far, or at an extreme angle.
2.  Barcode recognition has an optimized ROI (Region of Interest). For best results, place barcodes within this specific area.
3.  Avoid strong direct light or excessively dark environments, as poor lighting affects accuracy and speed.
4.  The AprilTag function defaults to the TAG36H11 family. To support others, modify the `image.ApriltagFamilies` parameter in the code and redeploy.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/dev/projects/app_scan_qrcode)

[MaixCAM MaixPy QR Code Recognition](https://wiki.sipeed.com/maixpy/doc/en/vision/qrcode.html)