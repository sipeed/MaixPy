from maix.peripheral import adc
from maix import time

a = adc.ADC(0, adc.RES_BIT_12, 5.0062)

while True:
    raw_data = a.read()
    print(f"ADC raw data:{raw_data}")

    time.sleep_ms(50)

    vol = a.read_vol()
    print(f"ADC vol:{vol}")