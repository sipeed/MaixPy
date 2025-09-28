---
title: MaixPy MaixCAM 内存使用说明
---

## MaixPy MaixCAM 内存简介

MaixPy 基于 Python 语言，而 Python 语言跑在 Linux 系统上，摄像头、图像、模型、应用都需要大量内存，因为内存有限，掌握内存使用和管理方法十分重要。

我们可以通过很多种方式来获取当前的内存使用状态，使用 MaixPy 内置方法活着 Linux 通用方法即可，比如使用 Python:
```python
from maix import sys
print(sys.memory_info())
```
输出类似如下内容：

```json
{'cma_total': 0, 'cma_used': 0, 'cmm_total': 2147483648, 'cmm_used': 177512448, 'hw_total': 4294967296, 'total': 2060726272, 'used': 339562496}
```

或者

```python
import psutil

# 获取虚拟内存信息
mem = psutil.virtual_memory()

print(f"总内存: {mem.total / (1024 ** 3):.2f} GB")
print(f"已用内存: {mem.used / (1024 ** 3):.2f} GB")
print(f"空闲内存: {mem.available / (1024 ** 3):.2f} GB")
print(f"内存使用率: {mem.percent}%")
```

或者命令行使用`cat /proc/meminfo` 或者使用`free`命令都可以看到。

从这里的 `total` `used`可以看到全部可用内存和已经使用的内存。

不过需要注意的是，这里看到的内存是 Linux 用户空间能使用的内存，小于实际内存，比如对于 4GiB 内存的 MaixCAM2，默认这里 是 1GiB，至于为什么这样，且看下文。


## MaixPy MaixCAM 内存划分

由于使用了 Linux 系统，我们将内存根据用途划分几个区域：

| 区域 |  作用 | 大小 |
|---- | ---- | --- |
| 保留 | 底层驱动和特殊用途，不同设备和厂商不一样 | 不同设备不同，一般比较小 |
| 内核预留 | 给 Linux 内核专用的内存 | 根据物理内存大小和内核驱动调整，比如 MaixCAM2 大约 80MiB |
| 用户内存 | Linux 用户空间程序使用 | 根据物理内存大小和应用程序内存用量调整，比如 MaixCAM2 为 1.92GiB 左右 |
| CMA 内存 | Contiguous Memory Allocator, 连续内存分配区域，Linux 显卡/图像等使用 | 根据图像相关应用配置 |
| CMM 内存 | Contiguous Memory Management, 厂商或用户自定义连续内存分配区域，注意这不是 Linux 标准，一般作用和 CMA 类似，为了和CMA区分这里我们姑且称之为 CMM ， 比如 MaixCAM 图像都不用标准 CMA 内存，而是自定义了一块区域给 摄像头/NPU 等硬件驱动使用 | 根据应用使用情况分配，比如 MaixCAM2 默认 1GiB， MaixCAM 默认 128MiB |

这里我们最需要关注的是两种内存：
* **Linux 用户空间内存**：这是我们代码和应用程序能用到的总内存，比如分配数组、创建对象，加载程序都需要用到这部分内存。
* **CMM内存/CMA内存**： 对于 MaixCAM 系列，没有显卡的情况下，一般 CMA 为 0 即不使用，芯片厂商都喜欢自己定义一套规范，比如 MaixCAM 和 MaixCAM2 都使用了自定义的内存区域用来给 摄像头/NPU 等需要频繁使用大内存的驱动和应用使用，以提高运行效率和减少内存碎片化。比如：
  * **摄像头读取一帧图像**：先将图像读取到这部分内存中，在 Linux 用户空间如果要查看图像，再将这部分内存直接映射或者拷贝到用户空间。所以一般来说应用设置摄像头分辨率越大，就需要占用更多的内存。
  * **NPU 跑模型**：加载模型时不是加载在用户空间内存的，是加载在自定义内存，比如 LLM 模型有 1.5GiB，那么需要保证这部分内存大于 1.5GiB 才能正常加载模型。

## 不同设备默认值

| 设备 | 硬件内存大小 | Linux 内核 + 用户空间 | CMM | CMA |
| --- | ----------- | ------------------ | --- | -- |
| MaixCAM  | 256MiB | 151MiB     | 105MiB | 0MiB |
| MaixCAM2 | 4GiB   | 1GiB       | 3GiB   | 0MiB |
| MaixCAM2 | 1GiB   | 512MiB     | 512MiB | 0MiB |


## 调整内存分配

如上所说，一般应用用默认值就足够了，如果你想调整大小，比如让 CMM 内存更多以加载更大的模型，则可以自己修改分配。

由于一般 CMM 是 CPU 厂商设计的，所以不同设备修改方法：
* MaixCAM: MaixCAM 的 CMM 厂商实际叫作 ION 内存，修改比较麻烦，必须重新编译系统，参考[github 修改](https://github.com/sipeed/LicheeRV-Nano-Build/commit/713161599e1b590249b1cd8a9e7f2a7f68d8d52d)。
* MaixCAM2: MaixCAM 的 CMM 厂商就叫作 CMM 内存，MaixCAM2 镜像做了优化，只需要修改 `/boot/configs` 中的 `maix_memory_cmm=2048` 修改为想要的大小就好了，单位是 MiB， 默认值是 -1 代表使用默认值。





