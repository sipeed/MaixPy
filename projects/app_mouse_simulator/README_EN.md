## 1. Introduction
This tool utilizes the device's touchscreen to simulate various computer mouse operations. It enables remote control of computers and other devices supporting the HID mouse protocol without the need for an additional physical mouse. It is suitable for simple operations in scenarios without a physical mouse, embedded device control, and similar applications.

## 2. Main Features
1.  **Touchpad Movement**: Achieve precise mouse cursor movement via the core touch area, with optimized sensitivity adapted to the screen ratio.
2.  **Mouse Button Simulation**: Supports the pressing and releasing of the left and right mouse buttons, enabling basic functions such as file selection and context menu invocation.
3.  **Scroll Wheel Simulation**: A dedicated wheel area supports vertical sliding to replicate the scrolling effect of a computer mouse wheel, useful for page turning and zooming.
4.  **Quick Exit**: Features a dedicated exit area to terminate the application with one click for convenient operation.
5.  **Visual Interaction**: Real-time display of touch points and button states during operation provides intuitive feedback on the current actions.

## 3. User Guide
![alt text](./assets/image.png)
1.  **Preparation**
    *   Ensure the device's HID Mouse function is enabled (Path: Settings -> USB Settings -> HID Mouse, check the box, confirm, and restart the device).
    *   Connect the Maix device to the computer (or other HID-supporting device) via a USB cable and ensure the device is recognized correctly.
2.  **Interface Area Identification**
    *   **Touchpad Area (TOUCHPAD)**: The large white-bordered rectangle occupying most of the screen, labeled "TOUCHPAD". This is the core area for moving the mouse cursor.
    *   **Wheel Area (WHEEL)**: The white-bordered rectangle to the right of the touchpad, labeled "WHEEL". Used to simulate the mouse scroll wheel.
    *   **Exit Area (EXIT)**: The white-bordered rectangle at the bottom right corner of the interface, labeled "EXIT". Used to quit the application.
    *   **Left Key Area (LEFT KEY)**: The white-bordered rectangle at the bottom left of the screen, labeled "LEFT KEY". Corresponds to the left mouse button.
    *   **Right Key Area (RIGHT KEY)**: The white-bordered rectangle at the bottom right of the screen, labeled "RIGHT KEY". Corresponds to the right mouse button.
3.  **Specific Operation Steps**
    *   **Moving the Mouse Cursor**: Lightly touch and slide your finger within the Touchpad Area (TOUCHPAD). A red dot on the screen will follow your finger, and the computer's mouse cursor will move synchronously. The sliding distance determines the cursor movement distance.
    *   **Left Mouse Button Operation**: Touch the Left Key Area (LEFT KEY) at the bottom left; the area will fill with white, corresponding to a left button press. Release your finger, and the area reverts to a border state, corresponding to a left button release. A quick tap (light touch followed by immediate release without significant sliding) within the Touchpad Area simulates a left mouse button click.
    *   **Right Mouse Button Operation**: Touch the Right Key Area (RIGHT KEY) at the bottom right; the area will fill with white, corresponding to a right button press. Release your finger, and the area reverts to a border state, corresponding to a right button release.
    *   **Scroll Wheel Operation**: Slide your finger up or down within the Wheel Area (WHEEL) to simulate mouse wheel scrolling, allowing you to turn pages or zoom content on the computer.
    *   **Exiting the Application**: Touch the Exit Area (EXIT) at the bottom right to immediately terminate the tool and exit the application interface.

## 4. Notes
1.  **HID Function Mandatory**: The HID Mouse function must be enabled in the device settings and the device restarted before use. Otherwise, the application will not work correctly and may display an error indicating the function is not enabled.
2.  **USB Connection Stability**: Ensure the USB cable connection is secure. Loose connections can cause interruptions in mouse control or unresponsive operations.
3.  **Distinguishing Operation Areas**: Each functional area is clearly defined. Please operate within the corresponding areas as much as possible to avoid accidental touches (e.g., accidentally triggering the exit area and closing the application).
4.  **Touch Sensitivity**: The sensitivity for cursor movement and scrolling has been optimized. If adjustments are needed, they can be modified through relevant device settings. Avoid excessive sliding, which may cause the cursor to drift significantly.
5.  **Device Compatibility**: This tool is primarily designed for devices supporting the HID mouse protocol (such as Windows and Linux computers). Some specialized devices may have compatibility issues and may not recognize or respond to operations correctly.

## 5. More Information
[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_usb_hand_touch)

[Introduction to Using MaixCAM MaixPy USB HID (as device)](https://wiki.sipeed.com/maixpy/doc/en/peripheral/hid.html)