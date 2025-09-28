from maix import hid, time

mouse = None
try:
    mouse = hid.Hid(hid.DeviceType.DEVICE_MOUSE)
except Exception as e:
    print(e)
    print('The HID evice is not enabled')
    print('Try: Use the application Settings -> USB Settings -> HID Mouse, then click Confirm, and restart the system.')
    print('You can also use examples/tools/maixcam_switch_usb_mode.py to enable the HID Mouse, then restart the system.')
    exit(0)

button = 0
x_oft = 5
y_oft = 5
wheel_move = 0

count = 0
while True:
    mouse.write([button, x_oft, y_oft, wheel_move])
    time.sleep_ms(100)
    count += 1
    if count > 50:
        break
    elif count > 25:
        x_oft = -5
        y_oft = -5

print('OK')