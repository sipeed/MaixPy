---
title: RTC usage
---

The MaixCAM-Pro has an onboard RTC module, which will automatically synchronize the system time upon power-on and also sync time from the network. It will automatically re-sync when there are changes in network status.

Therefore, under normal circumstances, you don’t need to manually operate the RTC; you can directly use the system’s time API to get the current time.

If you need to control the RTC manually, see [Using the BM8563 RTC](./bm8653.md). Disable the system's automatic RTC and NTP synchronization services first so they do not change the time at the same time as your program.

> MaixCAM does not have an onboard RTC.

