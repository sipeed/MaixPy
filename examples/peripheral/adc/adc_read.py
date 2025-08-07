from maix.peripheral import adc
from maix import time, sys

device_id = sys.device_id()
if device_id == "maixcam2":
    raise Exception("MaixCAM2 don't have ADC")
else:
    pin_name = "A19"


a = adc.ADC(0, adc.RES_BIT_12)

while True:
    raw_data = a.read()
    print(f"ADC raw data:{raw_data}")

    time.sleep_ms(50)

    vol = a.read_vol()
    print(f"ADC vol:{vol}")