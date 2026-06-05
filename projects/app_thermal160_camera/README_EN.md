# MaixCAM Thermal160 Real-time Thermal Imaging

This is a MaixPy v4 Thermal160 live-view app for MaixCAM2. It receives 160x120 thermal frames over UART, parses the tail telemetry, and renders pseudo-color live video with center temperature, min/max markers, and NUC status.

## Hardware Requirements

* Device: MaixCAM2.
* Sensor: Thermal160 / TN160 160x120 thermal imaging module.
* Connections:
  * UART: MaixCAM2 uses `/dev/ttyS2` by default.
  * Baud rate: starts at `2,000,000`, then switches to `4,000,000` after sending the `0x44` handshake.
  * Reset: MaixCAM2 `A9` is configured as `GPIOA9` and used as the Thermal160 software reset pin.

## Startup Behavior

When MaixCAM2 is powered from battery, Thermal160 may not automatically enter a usable powered/reset state. Before opening UART, the app sends one A9 reset pulse:

1. `pinmap.set_pin_function("A9", "GPIOA9")`
2. Release `GPIOA9` high by default
3. Pull it low for about `120ms`
4. Release it high and wait about `400ms`

The current implementation assumes an active-low reset. If your hardware reset is active-high, swap these constants:

```python
THERMAL_RESET_IDLE_LEVEL = 0
THERMAL_RESET_ACTIVE_LEVEL = 1
```

During startup, the UI shows `Initializing thermal160` with a progress bar for 3 seconds. It only shows `thermal160 device not found` if no valid frame is received after that grace period.

## Configuration

Adjust the following constants at the top of the code as needed:

* `SKIP_COUNT = 10`: Initial frames skipped after startup.
* `STARTUP_GRACE_SEC = 3.0`: Delay before showing `Device not found`.
* `THERMAL_RESET_ASSERT_SEC = 0.12`: A9 reset assert time.
* `THERMAL_RESET_RELEASE_DELAY_SEC = 0.40`: Delay after releasing reset.

## Protocol Overview

The expected UART data format is:

* Header: `0xFF`
* Pixels: `160 * 120 = 19200` bytes of 8-bit temperature-linear grayscale data
* Telemetry: 30 bytes, including `VTEMP / t_lo / t_hi / anchor / smooth / mean_diff / NTC / NUC` runtime state
* Total size: `1 + 19200 + 30 = 19231` bytes

Note: valid pixel data may contain `0xFF`. The parser must not resync only because `0xFF` appears in the pixel payload. It validates frame alignment using telemetry plausibility and the next-frame header position.

## History Recorder App

The 24-hour temperature history recorder is a separate app package:

```text
../maix-thermal160_camera_history/
```

It records one temperature sample per second to CSV and supports one-tap full-history PNG export.

## Notes

* A9 is only a reset control signal. Do not power Thermal160 directly from a MaixCAM2 GPIO.
* Reset polarity and timing still need validation on real hardware.
* UART resources are released in the `finally` block on exit.
