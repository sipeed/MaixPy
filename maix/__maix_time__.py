from . import _maix
import time

def sleep_ms(ms : int):
    time.sleep(ms * 0.001)

def sleep_us(us: int):
    time.sleep(us * 0.000001)

_maix.time.sleep = time.sleep
_maix.time.sleep_ms = sleep_ms
_maix.time.sleep_us = sleep_us
