# Thermal160 History Recorder

This is a standalone MaixCam2 app package for long-running Thermal160 temperature logging.

## Features

- Reads Thermal160 UART frames from MaixCam2 `/dev/ttyS2`.
- Samples temperature history once per second for 24-hour observation.
- Continuously writes `output/history_*.csv` so data is not lost if the run is interrupted.
- Shows live preview, current temperature values, and a rolling 30-minute trend.
- Tap `SAVE` to save a full-history PNG trend chart.
- Saves one more PNG on exit when enough samples are available.
- Sends one Thermal160 software reset pulse through MaixCAM2 `A9` / `GPIOA9` before opening UART.

## Software Reset

When MaixCAM2 is powered from battery, Thermal160 may not automatically enter a usable powered/reset state. On startup, the app does:

1. `pinmap.set_pin_function("A9", "GPIOA9")`
2. Release `GPIOA9` high by default
3. Pull it low for about `120ms`
4. Release it high and wait about `400ms`

The current implementation assumes an active-low reset. If your hardware reset is active-high, swap these constants:

```python
THERMAL_RESET_IDLE_LEVEL = 0
THERMAL_RESET_ACTIVE_LEVEL = 1
```

## Output

- MaixCam2 installed app output directory: `/maixapp/apps/thermal160_camera_history/output/`
- CSV: `/maixapp/apps/thermal160_camera_history/output/history_YYYYmmdd_HHMMSS.csv`
- PNG: `/maixapp/apps/thermal160_camera_history/output/trend_YYYYmmdd_HHMMSS.png`

## Frame Format

The app uses the current Thermal160 monitor frame format:

- Header: `0xFF`
- Pixels: `160 * 120 = 19200` bytes
- Telemetry: 30 bytes
- Total size: `1 + 19200 + 30 = 19231` bytes

## Notes

- This is a history recorder app, not a replacement for the live thermal camera app.
- A9 reset, UART, touchscreen, and PNG saving still need validation on MaixCam2 hardware.
- If no valid frame is received after 3 seconds, the UI shows `thermal160 device not found`.
- A9 is only a reset control signal. Do not power Thermal160 directly from a MaixCAM2 GPIO.
