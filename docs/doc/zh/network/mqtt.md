---
title: MaixPy MaixCAM 使用 MQTT 订阅发布消息
---

## MQTT 简介

使用 MQTT 可以快速简单地使用 订阅-发布 模型来进行实时通信。

系统组成：
* MQTT 服务器（broker），负责转发消息。
* MQTT 客户端，从服务器订阅主题，并且接收消息，以及像服务器特定的主题发布消息。

通信过程：
* 客户端连接 MQTT 服务器。
* 客户端订阅自己感兴趣的主题，比如`topic1`。
* 有其它客户端或者服务器发布`topic1`这个主题的信息时，会被实时推送到客户端。
* 客户端也可以主动向特定的主题推送消息，其它订阅了这个主题的客户端都会收到，比如向自己订阅了的`topic1`推送消息自己也会收到。


## MaixPy MaixCAM 中使用 MQTT

使用 `paho-mqtt` 这个模块即可，具体用法可以自行搜索`paho-mqtt`的用法，也可以参考[MaixPy/examples](https://github.com/sipeed/MaixPy/tree/main/examples/network)中的例程。


如果你使用了早期的系统，可能需要手动安装一下`paho-mqtt`这个包，安装方法见[添加额外的 Python 软件包](../basic/python_pkgs.md)。




