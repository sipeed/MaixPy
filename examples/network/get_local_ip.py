import socket
import psutil

def get_ips(ignores = ["127.0.0.1"]):
    ip_addresses = []
    for interface, snics in psutil.net_if_addrs().items():
        for snic in snics:
            if snic.family == socket.AF_INET:
                if snic.address in ignores:
                    continue
                ip_addresses.append(snic.address)
    return ip_addresses


if __name__ == "__main__":
    ips = get_ips()
    for ip in ips:
        print(f"IP Address: {ip}")
