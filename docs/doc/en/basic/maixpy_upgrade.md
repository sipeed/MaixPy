---
title: Update MaixPy.
---

There are two methods to begin with. If you are new to this and want to keep things simple, you can try using the pre-installed MaixPy firmware on the TF card that comes with the device. You can consider updating it later.

However, since we don't know when the TF card you received was manufactured, it is recommended to update the system.

## Updating the System Directly

Follow the steps in [Upgrading and Flashing the System](./os.md) to upgrade to the latest system, which already includes the newest MaixPy firmware.

## Updating Only the MaixPy Firmware

Check the latest version information and release notes in the [MaixPy repository release page](https://github.com/sipeed/MaixPy/releases). It includes details about the MaixPy firmware and the system information corresponding to each version.

If you prefer not to update the system (since system changes are usually minimal, you can check if there are any system-related changes in the MaixPy update notes before deciding whether to update the system), you can simply update the MaixPy firmware.

* Set up WiFi in the settings to connect the system to the internet.
* Click on `Update MaixPy` in the settings app to proceed with the update.


You can also execute Python code to call system command to install:
```python
import os

os.system("pip install MaixPy -U")
```

> If you are comfortable using the terminal, you can also update MaixPy by using `pip install MaixPy -U` in the terminal.



And you can download `wheel` file (`.whl`format) manually, and send to device(transfer method see [MaixVision Usage](./maixvision.md)), then install by `pip install *****.whl` command.
