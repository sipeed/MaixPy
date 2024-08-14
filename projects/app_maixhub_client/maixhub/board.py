
def get_board_name():
    '''
        @return None or (series, cpu_name, board_name)
    '''
    try:
        with open("/etc/hostname", "r") as f:
            if f.read().lower().find("maixcam") >= 0:
                return "maixcam"
    except Exception:
        pass
    return None

def get_ip(ifname = "wlan0"):
    import socket
    import fcntl
    import struct
    ifname = ifname.encode()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ip = socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
        return ip
    except Exception as e:
        pass
    return None

def is_support_model_platform(platform):
    # return platform == "maixcam"
    return True

if __name__ == "__main__":
    print(get_board_name())

