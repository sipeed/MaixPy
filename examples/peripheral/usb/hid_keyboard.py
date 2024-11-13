from maix import hid, time

keyboard = None
try:
    keyboard = hid.Hid(hid.DeviceType.DEVICE_KEYBOARD)
except Exception as e:
    print(e)
    print('The HID device is not enabled')
    print('Try: Use the application Settings -> USB Settings -> HID Keyboard, then click Confirm, and restart the system.')
    print('You can also use examples/tools/maixcam_switch_usb_mode.py to enable the HID Keyboard, then restart the system.')
    exit(0)

def press(keyboard, key):
    keyboard.write([0, 0, key, 0, 0, 0, 0, 0])
    time.sleep_ms(50)
    keyboard.write([0, 0, 0, 0, 0, 0, 0, 0])        #  key=0, means release

# Refer to the "Universal Serial Bus HID Usage Tables" section of the official documentation(https://www.usb.org).
press(keyboard, 21)                 # press 'r'
press(keyboard, 22)                 # press 's'
press(keyboard, 23)                 # press 't'
press(keyboard, 24)                 # press 'u'
press(keyboard, 25)                 # press 'v'

print('OK')