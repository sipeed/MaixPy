---
title: MaixCAM MaixPy 使用 RTC 模块
---


MaixCAM-Pro 板载了一个 RTC 模块，默认上电会自动同步系统时间，以及从网络同步时间，网络状态变化后也会自动同步。

所以一般情况不需要手动操作 RTC，直接使用系统的时间 API 获取时间即可。

如果一定要手动操作 RTC，请看[bm8653 RTC 模块使用](./bm8653.md)（手动操作前可以在系统 `/etc/init.d`目录下把 RTC 和 NTP 相关服务删掉以禁用自动同步。

> MaixCAM 无板载 RTC。

