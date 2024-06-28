---
title: Network Settings for MaixPy MaixCAM WiFi Configuration
---

## Introduction

To enable MaixCAM to use the network, it first needs to connect to the network via WiFi. MaixCAM provides several methods to connect to a WiFi hotspot.

## Using the Built-in Settings Application

After powering on, enter the `Settings` application and select the `WiFi` function. You can connect by sharing a `WiFi QR code` from your phone or by generating a QR code at [maixhub.com/wifi](https://maixhub.com/wifi) and scanning it. Alternatively, you can manually scan for `WiFi` hotspots and enter the password to connect.

Once connected successfully and the DHCP assigns an IP address, the IP will be displayed on the screen.

## Connecting via MaixPy

```python
from maix import network, err

w = network.wifi.Wifi()
print("IP:", w.get_ip())

SSID = "Sipeed_Guest"
PASSWORD = "qwert123"
print("Connecting to", SSID)

e = w.connect(SSID, PASSWORD, wait=True, timeout=60)
err.check_raise(e, "Failed to connect to WiFi")
print("IP:", w.get_ip())
```

## DNS Server Configuration

In practice, some users may find that their router's DNS resolution cannot resolve certain domain names. Therefore, the default system sets the DNS servers in the `/boot/resolv.conf` file:

```shell
nameserver 114.114.114.114 # China
nameserver 223.5.5.5 # Aliyun China
nameserver 8.8.4.4 # Google
nameserver 8.8.8.8 # Google
nameserver 223.6.6.6 # Aliyun China
```

Generally, there is no need to modify this file. If you encounter DNS resolution issues, you can modify this file.

The actual configuration file used by the system is located at `/etc/resolv.conf`. This file is automatically copied from `/boot/resolv.conf` at startup. Therefore, the simplest solution after modification is to reboot.

If you prefer not to reboot, you need to modify both files simultaneously.

