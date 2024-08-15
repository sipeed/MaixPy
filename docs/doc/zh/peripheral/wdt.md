---
title: MaixCAM MaixPy 使用看门狗定时器
---

## 简介

为了防止程序出现问题，常常会用到看门狗定时器（WDT), 在程序出问题时自动重启系统。

原理就是有一个倒计时计数器，我们需要在程序的逻辑中定期地去设置这个倒计时时间（也叫喂狗），如果我们的程序在哪儿卡住了导致没有定期去设置倒计时，倒计时到 0 后硬件就会出发系统重启。


## MaixPy 中使用 WDT

```python
from maix import wdt, app, time

w = wdt.WDT(0, 1000)

while not app.need_exit():
    w.feed()
    # here sleep op is our operation
    # 200 ms is normal, if > 1000ms will cause system reset
    time.sleep_ms(200)

```




