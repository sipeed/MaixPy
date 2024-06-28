---
title: MaixPy MaixCAM 网络设置 WiFi 设置
---


## 简介

要让 MaixCAM 能够使用网络，首先需要使用 WiFi 连接到网络。
MaixCAM 提供了几种方法连接 WiFi 热点。

## 使用内置设置应用连接

开及后进入`设置`应用，选择`WiFi`功能，可以通过手机分享`WiFi 二维码`或者再[maixhub.com/wifi](https://maixhub.com/wifi) 生成二维码，然后扫码连接。
也可以手动扫描`WiFi`热点，然后输入密码进行连接。

连接成功等待 DHCP 获得 IP 后界面会显示 IP。


## 通过 MaixPy 连接

```python
from maix import network, err

w = network.wifi.Wifi()
print("ip:", w.get_ip())

SSID = "Sipeed_Guest"
PASSWORD = "qwert123"
print("connect to", SSID)

e = w.connect(SSID, PASSWORD, wait=True, timeout=60)
err.check_raise(e, "connect wifi failed")
print("ip:", w.get_ip())
```

## DNS 服务器设置

实际使用时发现有些用户的路由器 DNS 解析可能解析不到某些域名，所以默认系统中在`/boot/resolv.conf`文件设置了 DNS 服务器

```shell
nameserver 114.114.114.114 # China
nameserver 223.5.5.5 # aliyun China
nameserver 8.8.4.4 # google
nameserver 8.8.8.8 # google
nameserver 223.6.6.6 # aliyun China
```

一般不需要修改，如果你的 DNS 解析遇到了问题可以修改这个文件。

实际系统用的配置文件路径是`/etc/resolv.conf`， 这个文件在开机时会被自动拷贝到`/etc/resolv.conf`，所以修改后直接重启最简单。

不想重启的话需要同时修改这两个文件。





