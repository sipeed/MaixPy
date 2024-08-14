from maix.v1 import lcd, sensor
from maix import time

lcd.init()
sensor.reset()
# sensor.set_hmirror(0)
# sensor.set_vflip(0)
# sensor.set_brightness(1)
# sensor.set_contrast(10)
# sensor.set_saturation(80)
sensor.set_framesize(sensor.VGA)
sensor.run(1)
sensor.skip_frames(1)
# sensor.set_colorbar(1)

print('sensor width:', sensor.width())
print('sensor height:', sensor.height())

while True:
    img = sensor.snapshot()
    lcd.display(img)
    time.sleep_ms(30)
