---
title: MaixCAM MaixPy 视频流 UVC 推流 / 化身 UVC 摄像头显示自定义内容
update:
  - date: 2024-12-20
    author: taorye
    version: 1.0.0
    content: 初版文档
---

## 简介

`MaixCAM` 化身 `UVC 摄像头`, `UVC` 全称为：USB video(device) class，这里提供两种方法供显示自定义内容:

- 通过 `maix.uvc.UvcStreamer` 的 `show` 方法来刷新目标图片（支持 YUYV 和 MJPEG），
- 通过 `maix.uvc.UvcServer` 注册自定义刷图回调函数来刷新目标图片（仅支持 MJPEG），区别于上一个方法的顺序逻辑，使用有一定的难度

## 参考例程

首先需要在 `Settings` APP 的 `USB settings` 栏内启用 `UVC` 功能。

连接 usb 线缆后：

- Windows 用户可在`设置-蓝牙和设备-摄像头`内，看到 UVC Camera设备，点进去即可预览到一张静态小猫图。
- Linux 用户，需要下载软件 `guvcview`，并选择分辨率为 320x240，格式为 MJPG，会看到两个小猫中间隔着乱码（原因是该小猫图片实际分辨率为 224x224，该软件自动拼了下一张过来，实际使用时使用正常的分辨率即可）

注意： 当前 Ubuntu 22 及更早系统版本使用的 guvcview 软件版本为 2.0.7，已知现象是显示色彩不对，严重偏绿。请换用更高版本即可正常显示，作者当前使用的版本号是 2.2.1。Ubuntu/Debian 用户可以尝试寻找相关的 PPA（个人包档案）来安装较新的 guvcview 版本。

注意： `UVC` 功能启用后，因为 Linux 的 `UVC Gadget` 实现，仍需一个用户程序处理 `UVC` 设备的事件，
否则整个 `USB` 功能会暂停等待，影响同时启用的其它 `Gadget` 功能，包括 `Rndis` 和 `NCM`，导致断网。
故对于其它 `USB` 功能有需求的用户，在基于 `MaixPy` 开发 UVC 显示功能时建议采用 `UvcStreamer` 的实现。
否则请保证 `MaixCAM` 设备有其它联网途径如 `WIFI` 以确保能正常开发调试。

<video controls autoplay src="../../assets/maixcam-pro_uvcdemo.mp4" type="video/mp4"> 您的浏览器不支持视频播放 </video>

### UvcStreamer

该方法不影响常态下 USB 功能，原理是分了两个进程。官方默认实现了一个 `server` 进程进行`UVC` 设备的事件处理，并封装了易用统一的刷图接口 `show(img)` 供用户使用，当成一个 `display` 线性逻辑操作即可。

参考示例源码路径： `MaixPy/examples/vision/streaming/uvc_stream.py`

示例分析（使用方法）：

1. 初始化 UvcStreamer 对象

```python
uvcs = uvc.UvcStreamer()
```

- （可选）切换成 MJPEG 模式，默认 YUYV

```python
uvcs.use_mjpg(1)
```

2. 刷图（自动处理格式，MJPEG 中等性能损耗，YUYV 高损耗）

```python
uvcs.show(img)
```


### UvcServer

高性能单进程实现，但仅在运行时 USB 全部功能才可用，故停止该进程时需要注意仍启用的 `Rndis` 和 `NCM` 会暂时失效，断开网络链接。

参考示例源码路径：`MaixPy/examples/vision/streaming/uvc_server.py`

另有封装成 APP 的源码路径：`MaixCDK/projects/app_uvc_camera/main/src/main.cpp`

示例分析（使用方法）：

1. 初始化 UvcServer 对象，需提供刷图回调函数实现

提供了 helper 函数 `helper_fill_mjpg_image` 帮助将更通用的 `Image` 对象刷入 `UVC` 的缓冲区。

```python
cam = camera.Camera(640, 360, fps=60)   # Manually set resolution
                                        # | 手动设置分辨率

def fill_mjpg_img_cb(buf, size):
    img = cam.read()
    return uvc.helper_fill_mjpg_image(buf, size, img)

uvcs = uvc.UvcServer(fill_mjpg_img_cb)
```
`fill_mjpg_img_cb` 参考实现仅当返回 `0` 时，才会正常触发缓冲区刷新。
故推荐在最后一行使用 helper 函数即可：
`return uvc.helper_fill_mjpg_image(buf, size, img)`

2. 启动 uvc，后台启动线程，非阻塞

```python
uvcs.run()
```

3. 停止 uvc，不再使用时需要调用，可恢复 `UvcStreamer` 方法实现中的后台进程，保证 `USB` 功能正常

目前有 BUG，MaixPy 框架在退出时会强制终止进程，导致并不能执行完 `while not app.need_exit():` 循环后的函数调用，即该 `stop()` 很难得到执行。
故对 **保证 `USB` 功能正常** 有需求的用户可以换用 `UvcStreamer` 方法或是移步 `MaixCDK` 的原始 C++ API，参考例程：`MaixCDK/examples/uvc_demo/main/src/main.cpp`。

```python
uvcs.stop()
```
