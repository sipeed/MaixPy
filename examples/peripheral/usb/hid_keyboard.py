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

def press2(keyboard, key0 = 0, key1 = 0, key2 = 0, key3 = 0, key4 = 0, key5 = 0):
    keyboard.write([0, 0, key0, key1, key2, key3, key4, key5])
    time.sleep_ms(50)
    keyboard.write([0, 0, 0, 0, 0, 0, 0, 0])        #  key=0, means release

# key0: 0x1:left-ctrl 0x2:left-shift 0x4:left-alt 0x8:left-windows
#       0x10:right-ctrl 0x20:right-shift 0x40:right-alt 0x80:right-windows
def press3(keyboard, key0, key1):
    keyboard.write([key0, 0, key1, 0, 0, 0, 0, 0])
    time.sleep_ms(50)
    keyboard.write([0, 0, 0, 0, 0, 0, 0, 0])        #  key=0, means release

# Refer to the "Universal Serial Bus HID Usage Tables" section of the official documentation(https://www.usb.org).
press(keyboard, 21)                 # press 'r'
press2(keyboard, 23, 24)            # press 'tu'
press3(keyboard, 0x2, 25)           # press 'left-shift + v'

print('OK')