import os, sys, app

cmd_restart = "/usr/bin/usb_util stop && /usr/bin/usb_util start"
device_id = sys.device_id()

def usb_devive(device_list):
    if device_id == "maixcam": # old config way
        if os.path.exists("/boot/usb.host"):
            os.remove("/boot/usb.host")
        with open("/boot/usb.dev", "w") as f:
            pass

        for device in device_list:
            if device.startswith("hid_"):
                device[0] = device[0][4:]
            dev_path = f"/boot/usb.{device[0]}"
            if device[1]:
                with open(dev_path, "w") as f:
                    pass
            else:
                if os.path.exists(dev_path):
                    os.remove(dev_path)
    else: # new config way
        app.set_sys_config_kv("usb", "mode", "device", True)
        for device in device_list:
            app.set_sys_config_kv("usb", device[0], "1" if device[1] else "0", True)

    ret = os.system(cmd_restart)
    if ret != 0:
        raise Exception("set device mode failed")


def usb_host():
    if device_id == "maixcam": # old config way
        if os.path.exists("/boot/usb.dev"):
            os.remove("/boot/usb.dev")
        with open("/boot/usb.host", "w") as f:
            pass
    else: # new config way
        app.set_sys_config_kv("usb", "mode", "host", True)
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

    # device mode functions, set your need to True and others to False. only support 4 devices for MaixCAM.
    device_list = [
        ["ncm", True],        # NCM virtual network card, faster trhan RNDIS but need manual install driver on windows <=10.
        ["rndis", True],      # RNDIS virtual network card, compatible for Windows and Linux but MacOS not suppot.
        ["hid_keyboard", False],  # Simulate USB HID keyboard input, then use maix.hid module.
        ["hid_mouse", False],     # Simulate USB HID mouse input, then use maix.hid module.
        ["hid_touchpad", False]   # Simulate USB HID touchpad input, then use maix.hid module.
    ]

    if mode == "device":
        usb_devive(device_list)
    else:
        usb_host()
        print("USB devices:")
        list_usb_devices()

