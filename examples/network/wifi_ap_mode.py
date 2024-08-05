from maix import network, err
import platform

def start_ap(ssid, password):
    w = network.wifi.Wifi()
    e = w.start_ap(ssid, password)
    err.check_raise(e, "start wifi ap failed")
    print("Start AP success, ip:", w.get_ip())

SSID = platform.node()
PASSWORD = "88888888"

print("Start AP, SSID:", SSID)
print("")
start_ap(SSID, PASSWORD)

