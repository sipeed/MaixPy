from maix import hid, time

touchpad = None
try:
    touchpad = hid.Hid(hid.DeviceType.DEVICE_TOUCHPAD)
except Exception as e:
    print(e)
    print('The HID evice is not enabled')
    print('Try: Use the application Settings -> USB Settings -> HID Touchpad, then click Confirm, and restart the system.')
    print('You can also use examples/tools/maixcam_switch_usb_mode.py to enable the HID Touchpad, then restart the system.')
    exit(0)

def touchpad_set(button, x_oft, y_oft, wheel_move):
    touchpad.write([button,
                    x_oft & 0xff, (x_oft >> 8) & 0xff,
                    y_oft & 0xff, (y_oft >> 8) & 0xff, 
                    wheel_move])
button = 0
x_oft = 0
y_oft = 0
wheel_move = 0

count = 0
direction = 0
while True:
    if direction == 0:
        x_oft += 150
        y_oft += 150
        if x_oft > 0x7fff:
            x_oft = 0x7fff
            y_oft = 0x7fff
            direction = 1
    else:
        x_oft -= 150
        y_oft -= 150
        if x_oft < 0:
            x_oft = 0
            y_oft = 0
            direction = 0
    print(x_oft, y_oft)
    touchpad_set(button, x_oft, y_oft, wheel_move)
    time.sleep_ms(10)
    count += 1
    if count > 500:
        break

print('OK')