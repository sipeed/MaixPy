from .version import __version__

# import all _maix module's members to maix, e.g. maix._maix.err -> maix.err
from ._maix.peripheral.key import add_default_listener
from . import _maix

add_default_listener()

del add_default_listener

import inspect

new_members = {}
members = inspect.getmembers(_maix)
for m in members:
    if m[0].startswith("__"):
        continue
    new_members["maix." + m[0]] = m[1]

members = inspect.getmembers(_maix.peripheral)
for m in members:
    if m[0].startswith("__"):
        continue
    new_members["maix." + m[0]] = m[1]

# clear all temp vars
del m, members, inspect

import sys
for k, v in new_members.items():
    sys.modules[k] = v

del k, v, new_members
