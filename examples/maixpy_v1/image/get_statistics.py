#!/usr/bin/env python

from maix.v1 import lcd, sensor
from maix import time

lcd.init()
sensor.reset()
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

thresholds = [[0, 80, 40, 80, 10, 80]]      # red

while True:
    img = sensor.snapshot()

    statistics = img.get_statistics(thresholds)
    print("L: mean {}, median {}, mode {}, std_dev {}, min {}, max {}, lq {}, uq {}\r\n",
                statistics.l_mean(), statistics.l_median(), statistics.l_mode(), statistics.l_std_dev(),
                statistics.l_min(), statistics.l_max(), statistics.l_lq(), statistics.l_uq())
    print("A: mean {}, median {}, mode {}, std_dev {}, min {}, max {}, lq {}, uq {}\r\n",
                statistics.a_mean(), statistics.a_median(), statistics.a_mode(), statistics.a_std_dev(),
                statistics.a_min(), statistics.a_max(), statistics.a_lq(), statistics.a_uq())
    print("B: mean {}, median {}, mode {}, std_dev {}, min {}, max {}, lq {}, uq {}\r\n",
                statistics.b_mean(), statistics.b_median(), statistics.b_mode(), statistics.b_std_dev(),
                statistics.b_min(), statistics.b_max(), statistics.b_lq(), statistics.b_uq())

    lcd.display(img)
