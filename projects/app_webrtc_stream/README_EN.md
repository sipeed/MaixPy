# Streaming Configuration and Broadcasting Tool User Manual

## 1. Introduction
This tool is a visual streaming configuration and broadcasting application running on the **MaixCam** device. It provides a simple touch-based interface that allows you to configure WebRTC streaming parameters and start broadcasting without requiring command-line input. Additionally, it integrates the **Tailscale** networking tool for quick management, enabling users to access the video stream across different networks with minimal setup.

## 2. Key Features
1.  **Visual Streaming Configuration**: Intuitively switch and select core streaming parameters via touch controls without manually editing configuration files.
2.  **Tailscale Network Management**: Quickly start or stop the Tailscale service, check device status (Online/Offline) and IP address, and complete login authorization to achieve cross-network device communication.
3.  **WebRTC Streaming**: Start the streaming service based on configured parameters, generate accessible playback URLs, and support real-time preview of the stream.
4.  **Stream URL Display**: Toggle the visibility of the playback URL during streaming to easily retrieve it and access the stream from other devices.

## 3. User Guide

### 3.1 Configuration Page & Operations
After launching the tool, you will enter the **Stream Settings** main page. This page contains four core configuration items (Encoder, Bitrate, Rate Control, Resolution) and a functional operation area at the bottom.

**1. Parameter Configuration (Tap the corresponding area to cycle options)**
*   **Encoder**: Tap to cycle between **H.264** and **H.265** encoding formats.
*   **Bitrate**: Tap to cycle between options from **1 Mbps to 64 Mbps**. Higher values provide clearer image quality but require higher network bandwidth.
*   **RC Type (Rate Control)**: Tap to switch between **CBR (Constant Bitrate)** and **VBR (Variable Bitrate)**.
*   **Resolution**: Tap to cycle between resolutions from **720 P to 4 K**, depending on the capabilities of the device's camera sensor.

**2. Bottom Function Buttons**
*   **Start Streaming**: Tap the blue button to start the WebRTC streaming service with the currently selected parameters and automatically enter the streaming preview page.
*   **Tailscale (Network Management, Optional)**: If Tailscale is installed on the device, a green button will appear. Tap to enter the management page where you can view the device status (ONLINE/OFFLINE) and IP address. You can perform **Start** (launch service/login), **Stop** (stop service), and **Logout** operations. Tap the icon in the top-left corner to return to the configuration page.
*   **Exit**: Tap the red button to exit the tool and return to the device desktop.

### 3.2 Streaming Preview & Operations
1.  Once entering the streaming page, the screen will display the real-time camera feed, which is the content currently being streamed.
2.  **Exit Icon (Top-left)**: Tap this icon to stop the current stream and return to the Stream Settings main page.
3.  **Eye Icon (Show/Hide URL)**: Tap this icon to toggle the visibility of the playback URL. When visible, the accessible WebRTC playback address will be displayed on the right side of the screen. You can copy this address to open in a browser or a WebRTC-compatible player on another device to watch the stream.
4.  Ensure the device has a stable network connection during streaming. To stop the stream, simply tap the Exit icon in the top-left corner.

## 4. Notes
1.  **Network Requirements**: Streaming requires a stable network environment. When selecting high bitrates or high resolutions, ensure the device's upload bandwidth meets the requirements to avoid buffering or visual artifacts.
2.  **Hardware Compatibility**: 4K resolution is only supported on MaixCam devices equipped with a 4K camera sensor.

## 5. More Information
[MaixCAM MaixPy Video Stream JPEG Streaming / Sending Images to Server](https://wiki.sipeed.com/maixpy/doc/en/video/jpeg_streaming.html)

[Source Code](https://github.com/sipeed/MaixPy/tree/main/projects/app_webrtc_stream)