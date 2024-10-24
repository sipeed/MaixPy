---
title: Using the RTC Module with MaixCAM MaixPy
---

The MaixCAM-Pro has an onboard RTC module, which will automatically synchronize the system time upon power-on and also sync time from the network. It will automatically re-sync when there are changes in network status.

Therefore, under normal circumstances, you don’t need to manually operate the RTC; you can directly use the system’s time API to get the current time.

If you do need to manually operate the RTC, please refer to [bm8653 RTC Module Usage](./bm8653.md). Before manually operating the RTC, you can disable automatic synchronization by deleting the RTC and NTP-related services in the system’s `/etc/init.d` directory.

> MaixCAM does not have an onboard RTC.



