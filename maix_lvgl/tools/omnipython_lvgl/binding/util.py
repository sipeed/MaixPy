# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Small utilities: memoize and stderr logging for analyze/emit."""
from __future__ import print_function

import re
import sys
from functools import lru_cache


_MEMOIZED_FUNCTIONS = []


def memoize(func):
    @lru_cache(maxsize=1000000)
    def memoized(*args, **kwargs):
        return func(*args, **kwargs)

    _MEMOIZED_FUNCTIONS.append(memoized)
    return memoized


def clear_memoized():
    """Clear caches whose values may refer to a previous translation unit."""
    for memoized in _MEMOIZED_FUNCTIONS:
        memoized.cache_clear()


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


_MONTSERRAT_FONT = re.compile(r"lv_font_montserrat_(\d+)$")


def config_guard(global_name):
    """Return the ``lv_conf.h`` switch a generated global depends on, or None.

    A build can turn a built-in Montserrat size off (``-DLV_FONT_MONTSERRAT_40=0``)
    without regenerating the binding, so the font's wrapper and its module entry
    are emitted inside ``#if`` on that switch.
    """
    match = _MONTSERRAT_FONT.match(global_name)
    if match is None:
        return None
    return "LV_FONT_MONTSERRAT_%s" % match.group(1)


def guarded(text, global_name, indent=""):
    """Wrap ``text`` in ``#if``/``#endif`` on `config_guard` when it has one.

    ``indent`` goes before ``text`` and ``#endif``, for a line that the caller's
    template has already indented.
    """
    guard = config_guard(global_name)
    if guard is None:
        return text
    return "#if %s\n%s%s\n%s#endif" % (guard, indent, text, indent)
