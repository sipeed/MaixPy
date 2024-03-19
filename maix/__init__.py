from .version import __version__

# import all _maix module's members to maix, e.g. maix._maix.err -> maix.err
from ._maix import *
from ._maix.peripheral import *
from ._maix.peripheral.key import add_default_listener

add_default_listener()

del add_default_listener

import sys
new_members = []
# find all maix._maix members
for k in sys.modules:
    if k.startswith('maix._maix.'):
        # add all maix._maix members to maix, then we can use `from maix import err`
        new_members.append(("maix" + k[10:], sys.modules[k]))
        # add all maix._maix.peripheral members to maix, then we can use `from maix import adc`
        if k.startswith('maix._maix.peripheral.'):
            v = ('maix' + k[21:], sys.modules[k])
            new_members.append(v)

# add all new members to maix
for k, v in new_members:
    sys.modules[k] = v

# clear all temp vars
del k, v, new_members
