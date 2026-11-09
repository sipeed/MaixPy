# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Select the canonical module-function surface for native registration."""

from __future__ import print_function

# C function names (parser names, not simplified Python names)
# LV_USE_TJPGD is 0 on every target (lv_conf.h): the JPEG decoder is jpegio's,
# registered through lv_image_decoder_create by displayif, the CircuitPython
# port and the CPython port.
RUNTIME_SKIP_MODULE_FUNCS = {
    "micropython": frozenset(
        {
            "lv_tjpgd_init",
            "lv_tjpgd_deinit",
        }
    ),
    "circuitpython": frozenset(
        {
            "lv_tjpgd_init",
            "lv_tjpgd_deinit",
        }
    ),
    "cpython": frozenset(
        {
            "lv_tjpgd_init",
            "lv_tjpgd_deinit",
            "mp_lv_init_gc",
            "mp_lv_deinit_gc",
            "mp_lv_get_roots",
        }
    ),
}

LIFECYCLE_MODULE_FUNCS = frozenset({"lv_init", "lv_deinit"})


def skip_module_func(func_name, target):
    return func_name in RUNTIME_SKIP_MODULE_FUNCS.get(target, frozenset())


def filter_module_funcs_for_target(module_funcs, target, api_model=None):
    """Return public canonical module functions available on ``target``.

    Native lowering discovers functions while generating wrappers.
    Registration follows the canonical API roles so a struct or
    object method can never leak into one target's module namespace.
    """
    if api_model is None:
        return [
            func
            for func in module_funcs
            if not skip_module_func(func.name, target)
        ]
    public = {
        function.c_name
        for function in api_model.functions
        if function.visibility == "public"
        and function.role == "module"
        and target in function.available_on
    }
    return [func for func in module_funcs if func.name in public]


def filter_registration_module_funcs(module_funcs):
    """Exclude lifecycle functions supplied by each target's module glue."""
    return [func for func in module_funcs if func.name not in LIFECYCLE_MODULE_FUNCS]
