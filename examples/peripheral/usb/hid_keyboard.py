from maix import hid, time

keyboard = None
try:
    keyboard = hid.Hid(hid.DeviceType.DEVICE_KEYBOARD)
except Exception as e:
    print(e)
    print('The HID evice is not enabled')
    print('Try: Use the application Settings -> USB Settings -> HID Keyboard, then click Confirm, and restart the system.')
    print('You can also use examples/tools/maixcam_switch_usb_mode.py to enable the HID Keyboard, then restart the system.')
    exit(0)

# Refer to the "Universal Serial Bus HID Usage Tables" section of the official documentation(https://www.usb.org).
keys = [21, 22, 23, 24, 25, 0]    # [r, s, t, u, v, 0], 0 means release. 

for key in keys:
    keyboard.write([0, 0, key, 0, 0, 0, 0, 0])

print('OK')