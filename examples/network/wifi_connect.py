from maix import network, err

w = network.wifi.Wifi()
print("ip:", w.get_ip())

SSID = "Sipeed_Guest"
PASSWORD = "qwert123"
print("connect to", SSID)

e = w.connect(SSID, PASSWORD, wait=True, timeout=60)
err.check_raise(e, "connect wifi failed")
print("ip:", w.get_ip())

