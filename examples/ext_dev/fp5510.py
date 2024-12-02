from maix import app, time
from maix.ext_dev import fp5510

fp = fp5510.FP5510()

value = 0
while not app.need_exit():
    fp.set_pos(value)
    print(f'set pos to {fp.get_pos()}')

    value += 100
    if value > 1023:
        value = 0
    time.sleep_ms(100)
