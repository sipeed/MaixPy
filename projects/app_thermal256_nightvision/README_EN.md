## 1. Overview
This system is a thermal imaging and visible light image fusion application running on the **MaixCAM2 device**. It enables thermal imaging data acquisition, temperature visualization, image super-resolution enhancement, and image fusion display in multiple modes, with touchscreen interactive parameter configuration. It can be widely used in scenarios such as equipment temperature measurement, scene inspection, and abnormal heat source troubleshooting.

## 2. Key Features
1.  **Four Working Mode Switching**: Supports Visible Light Mode (Vis), Pure Thermal Imaging Mode (Therm), Adaptive Hybrid Fusion Mode (Mix), and Edge-Enhanced Fusion Mode (Edge) to meet observation needs in different scenarios.
2.  **Thermal Imaging Enhancement**: Built-in Super-Resolution (SR) model to improve the clarity of thermal imaging images, with manual on/off control for this function.
3.  **Thermal Imaging Pseudocolor Switching**: Provides five pseudocolor mapping schemes (Hot, Cool, Magma, Turbo, Night) to help users distinguish temperature differences more clearly.
4.  **Flexible Parameter Configuration**: Supports touchscreen adjustment of image scaling ratio and offset (X/Y axes). Configuration parameters are automatically saved, eliminating the need for re-adjustment at the next startup.
5.  **Temperature Difference Visualization**: Real-time calculation and display of temperature differences in thermal imaging images. The edge enhancement function is automatically triggered based on temperature differences to highlight abnormal high/low temperature areas.
6.  **HUD Interface Hide/Display**: Supports hiding the operation interface to obtain a pure observation screen, which can be restored with a single tap again.

## 3. User Instructions
### 3.1 System Startup
1.  Ensure the device is MaixCAM2 with relevant drivers and dependency environments deployed.
2.  Correctly connect the thermal imaging module to the corresponding I2C/SPI pins of MaixCAM2 (pin configuration is preset in the code, no additional modification required).
3.  Upload the application program and related files (super-resolution model `sr2.5_ir32_npu1.mud`, font file, configuration file) to the specified path of the device.
4.  Run the application program. The system will automatically complete initialization (camera, thermal imaging module, model loading), which takes about 8 seconds. The screen displays the prompt "Initializing (Wait 8s)...".
5.  After initialization is completed, the system enters Pure Thermal Imaging Mode (Therm) by default, and you can start using it immediately.
![alt text](./assets/image.png)
### 3.2 Touchscreen Operation Guide
#### 3.2.1 Basic Operations
- **Mode Switching**: Tap the top left corner of the screen (area from (0,0) to (150,80)) to cycle through the four working modes: Vis/Therm/Mix/Edge.
- **HUD Interface Switching**: Tap the bottom left corner of the screen (area from (0, h-80) to (120, h), where h is the screen height) to hide/display the operation interface (only a green dot prompt remains after hiding, and tapping this area again restores the interface).

#### 3.2.2 Exclusive Operations for Pure Thermal Imaging Mode (Therm)
- **Super-Resolution (SR) Switch**: Tap the middle left of the screen (area from (0, h/2-40) to (100, h/2+40)) to turn on/off the thermal imaging image super-resolution enhancement function (the image becomes clearer when enabled, displayed in green for on and red for off).
- **Pseudocolor Switching**: Tap the middle right of the screen (area from (w-120, h/2-40) to (w, h/2+40), where w is the screen width) to cycle through the five pseudocolor mapping schemes. The current pseudocolor name is displayed in the middle right of the screen.

#### 3.2.3 Exclusive Operations for Hybrid/Edge Fusion Modes (Mix/Edge)
- Inherits the **Super-Resolution Switch** and **Pseudocolor Switching** functions of the Pure Thermal Imaging Mode (the super-resolution of the Mix mode is independently configured and does not affect the Therm mode).
- **Scaling Ratio Adjustment**: Tap the upper right of the screen (area from (w-180, 50) to (w-80, 130)) to decrease the scaling ratio (minimum 0.1), and tap the area from (w-80, 50) to (w, 130) to increase the scaling ratio. The current scaling ratio is displayed in the top right of the screen.
- **Image Offset Adjustment**: Tap the bottom right of the screen (area from (w-160, h-160) to (w, h)) and adjust the image X/Y axis offset by sliding:
  - Left/right sliding: Adjust the X-axis offset (< for left offset, > for right offset)
  - Up/down sliding: Adjust the Y-axis offset (^ for upward offset, v for downward offset)
  - The offset is displayed in real-time in the bottom right of the screen.

#### 3.2.4 Exclusive Operations for Visible Light Mode (Vis)
Only supports **Mode Switching** and **HUD Interface Switching**, with no additional parameter configuration functions.

### 3.3 Data Saving Instructions
During the operation of the application, all configuration parameters (scaling ratio, X/Y offset, pseudocolor index, super-resolution switch status, etc.) are automatically saved to the `/root/fusion.json` file when the program exits normally. The next time the application is started, it will automatically load the last configuration without the need for repeated adjustments.

## 4. Notes
1.  **Device Compatibility**: This application only supports the **MaixCAM2 device**. Running it on other devices will directly throw an exception. Do not deploy it on non-target devices.
2.  **Initialization Requirements**:
    - Do not power off or operate the device during initialization, otherwise, the thermal imaging module configuration may fail.
    - The initialization of the thermal imaging module takes about 8 seconds (including preview stop, start, temperature preview start, etc.). Please wait patiently for the screen to switch to the working interface.
3.  **Hardware Connection**: Ensure the thermal imaging module is firmly connected to the I2C7 (A8/A9) and SPI2 (B18/B19/B20/B21) pins of MaixCAM2. Poor contact will lead to data acquisition failure (no thermal imaging image on the screen).
4.  **File Dependencies**:
    - The super-resolution model file `sr2.5_ir32_npu1.mud` must be placed in the `/root/models/` directory. Its absence will render the super-resolution function unavailable.
    - The font file `SourceHanSansCN-Regular.otf` must be placed in the `/maixapp/share/font/` directory. Its absence will result in the failure of normal display of interface text.
5.  **Performance Notes**: Enabling the super-resolution function will cause a certain drop in the system processing frame rate, which is a normal phenomenon to prioritize image clarity.
6.  **Temperature Threshold**: The default trigger threshold for the edge enhancement function is 5.0. When the temperature difference of the thermal imaging image is less than this threshold, the edge enhancement does not take effect, and only the fused image is displayed.
7.  **Normal Exit**: Please exit the application through the normal device process to avoid forced power off, otherwise, the configuration parameters cannot be automatically saved.

## 5. Further Introduction
### 5.1 Detailed Explanation of Each Working Mode
1.  **Visible Light Mode (Vis)**: Only displays the visible light image captured by the camera without thermal imaging-related information. Suitable for regular observation in normal light environments.
2.  **Pure Thermal Imaging Mode (Therm)**: Only displays the temperature image collected by the thermal imaging module, distinguishing temperature levels through pseudocolors. Suitable for environments where visible light cannot penetrate (such as darkness and smoke) or scenarios that require rapid troubleshooting of heat sources.
3.  **Adaptive Hybrid Fusion Mode (Mix)**: Adaptively fuses visible light images and thermal imaging images, and automatically adjusts the fusion weight according to the temperature difference of thermal imaging images. It not only retains scene details but also highlights abnormal heat sources, suitable for scenarios that require simultaneous observation of scene environment and temperature information.
4.  **Edge-Enhanced Fusion Mode (Edge)**: Extracts edge information from thermal imaging images and overlays it on visible light images to highlight the contours of high/low temperature areas. Suitable for scenarios that require accurate positioning of the boundaries of abnormal heat sources.

### 5.2 Configuration File Explanation
The configuration file `/root/fusion.json` is in JSON format and contains the following core fields:
- `scale`: Image scaling ratio (default 1.0)
- `x`/`y`: Image X/Y axis offset (default 0)
- `cmap_idx`: Pseudocolor index (default 0, corresponding to Hot pseudocolor)
- `sr_therm`/`sr_mix`/`sr_edge`: Super-resolution function switch status of each mode (default True/False/True)

If the configuration file is damaged or lost, the application will automatically load the default configuration without affecting normal operation.

### 5.3 Extension Instructions
1.  The edge enhancement trigger threshold can be adjusted by modifying the `EDGE_TEMP_THRESHOLD` variable in the code to adapt to the temperature detection needs of different scenarios.
2.  New pseudocolor mapping schemes can be added to the `CMAP_LIST` to expand the display effects of thermal imaging images.
3.  Supports replacing the super-resolution model. Simply replace the model file in the `/root/models/` directory and modify the model name and output layer name in the code.

[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_thermal256_nightvision)
