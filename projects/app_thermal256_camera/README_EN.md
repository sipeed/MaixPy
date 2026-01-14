## 1. Introduction
This APP is a thermal imaging data processing application specifically developed for the **MaixCAM2 device**. It enables real-time preview, high-definition enhancement, temperature data extraction, and visualization of thermal imaging frames. It also supports local saving of thermal images and raw data for subsequent analysis. The tool features multiple built-in image enhancement models and supports resolution switching to meet thermal observation needs across different scenarios.

## 2. Key Features
1.  **Real-Time Thermal Preview:** Displays thermal images in a heatmap format to clearly show temperature distribution. It supports the COLORMAP_MAGMA pseudo-color mapping to enhance the visibility of temperature differences.
2.  **Automatic Temperature Extraction:** Automatically identifies and annotates the Center Temperature, Maximum Temperature (H), and Minimum Temperature (L) in the frame, accurate to one decimal place.
3.  **Image Resolution Enhancement:** Supports switching between Lo-Res (Original Resolution) and Hi-Res (Enhanced Resolution) modes. The Hi-Res mode utilizes a pre-trained image enhancement model to improve overall detail and clarity.
4.  **Multi-Format Data Saving:** Supports capturing and saving thermal images (JPG), raw grayscale data, and enhanced grayscale data (NPY format), facilitating data review and professional analysis.
5.  **HUD Toggle:** Allows showing or hiding the Heads-Up Display (HUD) to either view the full thermal frame or use the interface for quick operational guidance.
6.  **Safe Exit Mechanism:** Provides a secure exit process that automatically restores the device's original NPU configuration to prevent interference with subsequent usage.

## 3. User Guide
### 3.1 Prerequisites
Ensure the device is a **MaixCAM2** and that hardware wiring is complete (Thermal module pins correctly mapped to MaixCAM2's I2C/SPI pins). Ensure the tool has been successfully deployed and launched on the device.
![alt text](./assets/images.png)
### 3.2 Startup and Initial Interface
1.  Upon startup, the tool automatically initializes (including pin configuration, I2C/SPI setup, thermal module startup, and model loading). The initial screen displays the thermal heatmap preview along with the full HUD.
2.  If errors occur during initialization, check that the hardware wiring and device model meet the requirements.

### 3.3 Core Operations (Touchscreen)
All operations are performed via the touchscreen:
1.  **Exit Tool:** Long-press the top-left corner (Area: 0≤x≤80, 0≤y≤40) for approximately 1-2 seconds. When the text color changes, the exit process is triggered, restoring the device configuration and closing the tool.
2.  **Capture & Save Data:** Tap the top-right corner (Area: Screen_Width-120≤x≤Screen_Width, 0≤y≤40) to capture the current frame and data.
    *   **Save Path:** `/maixapp/share/picture/thermal/`
    *   **Saved Files:** Includes a JPG heatmap, raw grayscale data (NPY), and enhanced grayscale data (NPY, if in Hi-Res mode). Filenames include timestamps and frame numbers for easy differentiation.
3.  **Switch Resolution Mode:**
    *   **Switch to Lo-Res:** Tap the bottom-left corner (Area: 0≤x≤120, Screen_Height-40≤y≤Screen_Height).
    *   **Switch to Hi-Res:** Tap the bottom-right corner (Area: Screen_Width-120≤x≤Screen_Width, Screen_Height-40≤y≤Screen_Height). The corresponding enhancement model will load automatically.
4.  **Toggle HUD:**
    *   **Hide HUD:** Tap the top-middle area (Area: Screen_Width//2-60≤x≤Screen_Width//2+60, 0≤y≤40) to hide all prompts and view only the thermal image.
    *   **Show HUD:** Tap the bottom-middle area (Area: Screen_Width//2-60≤x≤Screen_Width//2+60, Screen_Height-40≤y≤Screen_Height) to restore the interface.

### 3.4 Viewing the Image
1.  **Annotations:** The **Center Temperature** is marked by a green cross (+ circle), the **Maximum Temperature** by a white cross, and the **Minimum Temperature** by a blue cross. The corresponding temperature value is displayed below each cross.
2.  **Modes:** The Hi-Res mode offers clearer details, suitable for observing minute temperature differences. The Lo-Res mode runs more smoothly, suitable for fast real-time observation.

## 4. Notes
1.  **Compatibility:** This tool supports only the **MaixCAM2**. Running it on other models will result in errors.
2.  **Wiring:** Ensure correct pin connections (A8/I2C7_SCL, A9/I2C7_SDA, B21/SPI2_CS1, etc.). Incorrect wiring causes initialization failure or data acquisition errors.
3.  **Model Files:** Hi-Res mode relies on pre-trained models (`espcn_x3.mud`, `sr3_ir_32.mud`, etc.). Ensure these files are placed in the `/root/models/` directory; missing files will disable Hi-Res functionality.
4.  **Storage:** Captured data consumes storage space. Regularly clear old files in `/maixapp/share/picture/thermal/` to prevent running out of space.
5.  **Exit Protocol:** Always exit via the long-press top-left method. Do not force power off or kill the process, as this may fail to restore the NPU configuration.
6.  **Performance:** Hi-Res mode involves model inference, resulting in slightly higher latency compared to Lo-Res mode. This is normal.
7.  **Temperature Calibration:** Displayed temperatures are calculated based on raw sensor data (Formula: Raw_Value/64 - 273.15). For higher precision measurements, the thermal module requires individual calibration.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_thermal256_camera)