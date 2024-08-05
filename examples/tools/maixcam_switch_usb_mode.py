import os

cmd_restart = "/etc/init.d/S03usbdev stop &&/etc/init.d/S03usbdev start"

def usb_devive():
    if os.path.exists("/boot/usb.host"):
        os.remove("/boot/usb.host")
    with open("/boot/usb.dev", "w") as f:
        pass
    ret = os.system(cmd_restart)
    if ret != 0:
        raise Exception("set device mode failed")


def usb_host():
    if os.path.exists("/boot/usb.dev"):
        os.remove("/boot/usb.dev")
    with open("/boot/usb.host", "w") as f:
        pass
    ret = os.system(cmd_restart)
    if ret != 0:
        raise Exception("set device mode failed")

def list_usb_devices():
    cmd = "lsusb"
    os.system(cmd)


if __name__ == "__main__":
    # Attention:
    #          switch USB to host mode will make USB RNDIS disabled,
    #          if you connect with USB RNDIS's IP, connection will disconnect.

    mode = "device" # MaixCAM as device
    # mode = "host"     # MaixCAM as host, you can plugin devices to MaixCAM's USB like USB camera.

    if mode == "device":
        usb_devive()
    else:
        usb_host()
        print("USB devices:")
        list_usb_devices()

