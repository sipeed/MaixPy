# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Shared identifier sanitization, LVGL patterns, and export_name helpers."""
from __future__ import print_function

import collections

from pycparser import c_ast

from . import runtime
from .parse import get_name, get_type
from .util import memoize

# Prevent identifier names which are Python reserved words (add underscore in such case)
def export_name(name, kind):
    """Delegate to `binding.naming` for Python export identifiers."""
    from .naming import export_name as _export_name

    return _export_name(name, kind)


def sanitize(
    id,
    kwlist=[
        "False",
        "None",
        "True",
        "and",
        "as",
        "assert",
        "break",
        "class",
        "continue",
        "def",
        "del",
        "elif",
        "else",
        "except",
        "finally",
        "for",
        "from",
        "global",
        "if",
        "import",
        "in",
        "is",
        "lambda",
        "nonlocal",
        "not",
        "or",
        "pass",
        "raise",
        "return",
        "try",
        "while",
        "with",
        "yield",
    ],
):
    if id in kwlist:
        result = "_%s" % id
    else:
        result = id
    result = result.strip()
    result = result.replace(" ", "_")
    result = result.replace("*", "_ptr")
    return result


@memoize
def simplify_identifier(id):
    match_result = runtime.current_context().lv_func_pattern.match(id)
    return match_result.group(1) if match_result else id


def obj_name_from_ext_name(ext_name):
    return runtime.current_context().lv_ext_pattern.match(ext_name).group(1)


def obj_name_from_func_name(func_name):
    return runtime.current_context().lv_obj_pattern.match(func_name).group(1)


def ctor_name_from_obj_name(obj_name):
    return "{prefix}_{obj}_create".format(
        prefix=runtime.current_context().module_prefix, obj=obj_name
    )


def is_method_of(func_name, obj_name):
    return func_name.lower().startswith(
        "{prefix}_{obj}_".format(
            prefix=runtime.current_context().module_prefix, obj=obj_name
        ).lower()
    )


def method_name_from_func_name(func_name):
    res = runtime.current_context().lv_method_pattern.match(func_name).group(1)
    return res if res != "del" else "delete"  # del is a reserved name, don't use it


def get_enum_name(enum):
    match_result = runtime.current_context().lv_enum_name_pattern.match(enum)
    return match_result.group(3) if match_result else enum


# C enum names that are nested on widget types (e.g. obj.FLAG) and also lv.OBJ_FLAG.
MODULE_LEVEL_DUPLEX_ENUMS = frozenset({"LV_OBJ_FLAG"})


def is_widget_scoped_only_enum(enum_name):
    """True when enum must not appear on the module (widget nested only)."""
    return enum_name not in MODULE_LEVEL_DUPLEX_ENUMS


def collect_enum_referenced(enums, obj_names):
    """Return enum names attached to widget types in the shared API contract."""
    enum_referenced = collections.OrderedDict()
    for obj_name in obj_names:
        for enum_name in enums.keys():
            if is_method_of(enum_name, obj_name) and is_widget_scoped_only_enum(enum_name):
                enum_referenced[enum_name] = True
    return enum_referenced


def str_enum_to_str(str_enum):
    ctx = runtime.current_context()
    res = ctx.lv_str_enum_pattern.match(str_enum).group(1)
    return ("%s_" % ctx.module_prefix.upper()) + res


def is_obj_ctor(func):
    ctx = runtime.current_context()
    # ctor name must match pattern
    if not ctx.create_obj_pattern.match(func.name):
        return False
    # ctor must return a base_obj type
    if not ctx.lv_base_obj_pattern.match(get_type(func.type.type, remove_quals=True)):
        return False
    # ctor must receive (at least) one base obj parameters
    args = func.type.args.params
    if len(args) < 1:
        return False
    if not ctx.lv_base_obj_pattern.match(get_type(args[0].type, remove_quals=True)):
        return False
    return True


def is_global_callback(arg_type):
    ctx = runtime.current_context()
    arg_type_str = get_name(arg_type.type)
    # print('/* --> is_global_callback %s: %s */' % (lv_global_callback_pattern.match(arg_type_str), arg_type_str))
    result = ctx.lv_global_callback_pattern.match(arg_type_str)
    return result


#
# Initialization, data structures, helper functions
#


# We consider union as a struct, for simplicity
def is_struct(type):
    return isinstance(type, c_ast.Struct) or isinstance(type, c_ast.Union)
