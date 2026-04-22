# MaixCAM Thermal 160 Real-time Thermal Imaging Monitoring

This is a real-time thermal imaging monitoring application developed based on the MaixPy v4 framework, specifically designed for MaixCAM2 (and future supported models). The application receives raw thermal imaging data at 160x120 resolution via UART and renders it as a real-time video stream with Ironbow pseudo-color mapping.

## Hardware Requirements

* Device: MaixCAM2, code can be ported to other platforms that support UART peripherals
* Sensor: Thermal imaging module with PMOD interface or UART output supporting 160x120 pixels.
* Connection method:
  * MaixCAM2 defaults to /dev/ttyS2.
  * Baud rate: Initial 2,000,000, can jump to up to 4,000,000 after handshake.

## Configuration

Adjust the following constants at the top of the code as needed:

* CMAP = True: Set to True to display color thermal imaging, False to display original grayscale (zero-copy, higher performance).
* SKIP_COUNT = 10: Number of initial frames to skip on startup, used to stabilize sensor data.

## Protocol Overview

The expected UART data format is:

* Header: 0xFF
* Payload: 19,200 bytes (160 * 120) of single-byte grayscale data.
* Checksum: Payload does not contain 0xFF.
* Total packet size: 19201 bytes

## Notes

* MaixCAM2 Compatibility: The program includes baud rate switching commands (0x44) specifically for MaixCAM2. When using other UART devices, please modify the HardwareHAL class according to the actual communication protocol.
* Resource Release: The program ensures safe UART resource release on exit through the finally block.

