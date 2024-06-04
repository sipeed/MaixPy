from .version import __version__

# import all _maix module's members to maix, e.g. maix._maix.err -> maix.err
from ._maix.peripheral.key import add_default_listener
from .__signal_handle__ import register_signal_handle
from ._maix.util import register_atexit
from . import _maix

register_signal_handle()
del register_signal_handle

register_atexit()
del register_atexit

add_default_listener()
del add_default_listener

import inspect

new_members = {}
members = inspect.getmembers(_maix)
for m in members:
    if m[0].startswith("__"):
        continue
    new_members["maix." + m[0]] = m

members = inspect.getmembers(_maix.peripheral)
for m in members:
    if m[0].startswith("__"):
        continue
    new_members["maix." + m[0]] = m

# clear all temp vars
del m, members, inspect

__all__ = []

import sys
for k, v in new_members.items():
    sys.modules[k] = v[1]
    __all__.append(v[0])

del k, v, new_members, sys


from ._maix import *
from ._maix.peripheral import *
