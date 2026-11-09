# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Shared setup for target C-lowering runs.

The individual emitters own VM-specific C output.  This module owns only the
target-neutral Python-side state needed before a lowering run begins.
"""

from __future__ import annotations

import collections
import os
from dataclasses import dataclass

from pycparser import c_ast

from . import runtime


_EMIT_DEFAULTS = (
    "generated_struct_functions",
    "struct_aliases",
    "callbacks_used_on_structs",
    "generated_callbacks",
    "generated_funcs",
    "enum_referenced",
    "generated_obj_names",
    "generated_globals",
    "module_funcs",
    "functions_not_generated",
)


@dataclass(frozen=True)
class FunctionReturnLowering:
    """C and metadata fragments for one exported function return value."""

    build_result: str
    build_return_value: str
    metadata_return_type: str


@dataclass(frozen=True)
class CallbackReturnLowering:
    """C fragments for one callback result through the MP compatibility API."""

    result_assignment: str
    return_value: str


@dataclass(frozen=True)
class TargetLoweringProfile:
    """The small, explicit set of VM constraints visible to shared lowering."""

    target: str
    supports_dynamic_function_pointer: bool


@dataclass(frozen=True)
class EnumNamespacePlan:
    """Target-neutral contents and nesting for one exported enum namespace."""

    name: str
    members: tuple[str, ...]
    nested_names: tuple[str, ...]
    widget_scoped_nested_names: tuple[str, ...]


@dataclass(frozen=True)
class ModuleRegistrationPlan:
    """Target-neutral declarations exported from the module at one phase.

    Backends use different C APIs to publish these objects, but must expose
    the same declaration set and retain declaration order.  This plan keeps
    the selection policy independent from those VM-specific C APIs.
    """

    int_constants: tuple[str, ...]
    generated_globals: tuple[str, ...]
    enum_names: tuple[str, ...]
    struct_names: tuple[str, ...]
    struct_alias_names: tuple[str, ...]
    object_names: tuple[str, ...]
    module_functions: tuple[object, ...]


@dataclass
class TypeDiscovery:
    """Shared recursive discovery of C-to-Python conversion requirements.

    Backends provide only native C emission hooks for arrays, structs, and
    function pointers. Typedef traversal, aliases, pointer fallbacks, enum
    conversion, and conversion-map updates are common policy.
    """

    get_name: object
    get_type: object
    structs: dict
    typedefs: list
    struct_aliases: dict
    mp_to_lv: dict
    lv_to_mp: dict
    lv_mp_type: dict
    lv_to_mp_byref: dict
    lv_to_mp_funcptr: dict
    generated_funcptr_helpers: dict
    try_generate_struct: object
    try_generate_array: object
    emit_function_pointer: object
    missing_conversion: type
    report_error: object

    def typedef_name(self, node):
        if isinstance(node, (c_ast.PtrDecl, c_ast.FuncDecl)):
            return self.typedef_name(node.type)
        if hasattr(node, "declname"):
            return node.declname
        if hasattr(node, "name"):
            return node.name
        return "unnamed_arg"

    def generate(self, type_ast):
        if isinstance(type_ast, str):
            raise SyntaxError("Internal error! try_generate_type argument is a string.")
        if isinstance(type_ast, c_ast.TypeDecl):
            return self.generate(type_ast.type)

        type_name = self.get_name(type_ast)
        if isinstance(type_ast, c_ast.Enum):
            self.mp_to_lv[type_name] = self.mp_to_lv["int"]
            self.mp_to_lv["%s *" % type_name] = self.mp_to_lv["int *"]
            self.lv_to_mp[type_name] = self.lv_to_mp["int"]
            self.lv_to_mp["%s *" % type_name] = self.lv_to_mp["int *"]
            self.lv_mp_type[type_name] = self.lv_mp_type["int"]
            self.lv_mp_type["%s *" % type_name] = self.lv_mp_type["int *"]
            return self.mp_to_lv[type_name]
        if type_name in self.mp_to_lv:
            return self.mp_to_lv[type_name]
        if isinstance(type_ast, c_ast.ArrayDecl) and self.try_generate_array(type_ast):
            return self.mp_to_lv[type_name]

        if isinstance(type_ast, (c_ast.PtrDecl, c_ast.ArrayDecl)):
            pointee_name = self.get_name(type_ast.type.type)
            ptr_type = self.get_type(type_ast, remove_quals=True)
            if pointee_name in self.structs:
                self.try_generate_struct(pointee_name, self.structs[pointee_name])
            if (
                isinstance(type_ast.type, c_ast.TypeDecl)
                and isinstance(type_ast.type.type, c_ast.Struct)
                and type_ast.type.type.name in self.structs
            ):
                self.try_generate_struct(
                    pointee_name, self.structs[type_ast.type.type.name]
                )
            if isinstance(type_ast.type, c_ast.FuncDecl):
                self._generate_function_pointer(type_ast, ptr_type, pointee_name)
            self.mp_to_lv.setdefault(ptr_type, self.mp_to_lv["void *"])
            self.lv_to_mp.setdefault(ptr_type, self.lv_to_mp["void *"])
            self.lv_mp_type.setdefault(ptr_type, "void*")
            return self.mp_to_lv[ptr_type]

        if type_name in self.structs:
            if self.try_generate_struct(type_name, self.structs[type_name]):
                return self.mp_to_lv[type_name]
        for new_type_ast in [
            item for item in self.typedefs if self.typedef_name(item) == type_name
        ]:
            new_type = self.get_type(new_type_ast, remove_quals=True)
            if (
                isinstance(new_type_ast, c_ast.TypeDecl)
                and isinstance(new_type_ast.type, c_ast.Struct)
                and not new_type_ast.type.decls
            ):
                explicit_name = new_type_ast.type.name
            else:
                explicit_name = new_type
            if type_name == explicit_name:
                continue
            if explicit_name in self.structs:
                if self.try_generate_struct(new_type, self.structs[explicit_name]):
                    if explicit_name == new_type:
                        self.struct_aliases[new_type] = type_name
            if type_name != new_type and self.generate(new_type_ast):
                self._copy_typedef_conversions(type_name, new_type)
                return self.mp_to_lv[type_name]
        return None

    def _generate_function_pointer(self, type_ast, ptr_type, pointee_name):
        if ptr_type in self.lv_to_mp_funcptr:
            existing = self.lv_to_mp_funcptr[ptr_type]
            self.lv_to_mp.setdefault(ptr_type, "mp_lv_%s" % existing)
            self.mp_to_lv.setdefault(ptr_type, self.mp_to_lv["void *"])
            self.lv_mp_type.setdefault(ptr_type, "function pointer")
            return
        if isinstance(type_ast.type.type.type, c_ast.TypeDecl):
            pointee_name = type_ast.type.type.type.declname
        helper_name = "funcptr_%s" % pointee_name
        suffix = 1
        while helper_name in self.generated_funcptr_helpers:
            helper_name = "funcptr_%s_%d" % (pointee_name, suffix)
            suffix += 1
        self.generated_funcptr_helpers[helper_name] = True
        func = c_ast.Decl(
            name=helper_name,
            quals=[],
            align=[],
            storage=[],
            funcspec=[],
            type=type_ast.type,
            init=None,
            bitsize=None,
        )
        try:
            generated = self.emit_function_pointer(helper_name, func)
            if generated:
                self.lv_to_mp_funcptr[ptr_type] = helper_name
                self.lv_to_mp[ptr_type] = "mp_lv_%s" % helper_name
                self.lv_mp_type[ptr_type] = "function pointer"
            else:
                self.lv_to_mp[ptr_type] = self.lv_to_mp["void *"]
                self.lv_mp_type[ptr_type] = "void*"
        except self.missing_conversion as exp:
            self.report_error(func, exp)

    def _copy_typedef_conversions(self, type_name, new_type):
        self.mp_to_lv[type_name] = self.mp_to_lv[new_type]
        type_ptr = "%s *" % type_name
        new_type_ptr = "%s *" % new_type
        if new_type_ptr in self.mp_to_lv:
            self.mp_to_lv[type_ptr] = self.mp_to_lv[new_type_ptr]
        if new_type in self.lv_to_mp:
            self.lv_to_mp[type_name] = self.lv_to_mp[new_type]
            self.lv_mp_type[type_name] = self.lv_mp_type[new_type]
            if new_type in self.lv_to_mp_funcptr:
                self.lv_to_mp_funcptr[type_name] = self.lv_to_mp_funcptr[new_type]
            if new_type in self.lv_to_mp_byref:
                self.lv_to_mp_byref[type_name] = self.lv_to_mp_byref[new_type]
            if new_type_ptr in self.lv_to_mp:
                self.lv_to_mp[type_ptr] = self.lv_to_mp[new_type_ptr]
            if new_type_ptr in self.lv_mp_type:
                self.lv_mp_type[type_ptr] = self.lv_mp_type[new_type_ptr]


def object_generation_order(obj_names, parent_obj_names):
    """Return objects once each, with every known parent before its child."""
    ordered = []
    emitted = set()
    visiting = set()

    def add(name):
        if name is None or name in emitted:
            return
        if name in visiting:
            raise ValueError("object inheritance cycle at %s" % name)
        visiting.add(name)
        add(parent_obj_names.get(name))
        visiting.remove(name)
        emitted.add(name)
        ordered.append(name)

    for obj_name in obj_names:
        add(obj_name)
    return tuple(ordered)


def failed_generation(
    *, method, problem, funcs, render_method, api_model=None, target=None
):
    """Build the common diagnostic and remove one failed declaration."""
    name = getattr(method, "name", None)
    function = next(
        (
            item
            for item in getattr(api_model, "functions", ())
            if item.c_name == name
        ),
        None,
    )
    if (
        function is not None
        and function.visibility == "public"
        and target in function.available_on
    ):
        raise RuntimeError(
            "unsupported public function for %s: %s: %s"
            % (target, name, problem)
        )
    remaining = list(funcs)
    try:
        remaining.remove(method)
    except ValueError:
        pass
    return (
        """
/*
 * Function NOT generated:
 * {problem}
 * {method}
 */
    """.format(method=render_method(method), problem=problem),
        remaining,
    )


_TARGET_PROFILES = {
    "micropython": TargetLoweringProfile("micropython", True),
    "circuitpython": TargetLoweringProfile("circuitpython", True),
    "cpython": TargetLoweringProfile("cpython", False),
}


def prepare_target_lowering(ctx, *, target, max_phase):
    """Set common emitter state without imposing a VM-specific C contract."""
    try:
        profile = _TARGET_PROFILES[target]
    except KeyError:
        raise ValueError("unsupported target lowering profile: %s" % target)
    runtime.set_("emit_options", {"target": target, "max_phase": max_phase})
    runtime.set_("target_lowering_profile", profile)
    for name in _EMIT_DEFAULTS:
        if name not in runtime.export_names():
            continue
        if name in ("generated_globals", "module_funcs"):
            runtime.set_(name, [])
        else:
            runtime.set_(name, collections.OrderedDict())
    if not hasattr(ctx, "headers") or ctx.headers is None:
        runtime.set_("headers", list(ctx.args.input))


def require_target_lowering(target):
    """Return the configured phase after verifying an emitter's target.

    A backend entry point selects the target before handing control to its
    native emitter.  Native emitters must not retain fallback paths for other
    backends: those paths conceal ownership mistakes and make a future
    refactor unsafe.  Keep the check next to the common lowering setup so all
    emitters can adopt the same boundary.
    """
    emit_options = runtime.get("emit_options", {})
    actual_target = emit_options.get("target")
    if actual_target != target:
        raise RuntimeError(
            "{target} emitter requires target={target!r}; got {actual!r}".format(
                target=target, actual=actual_target
            )
        )
    return emit_options.get("max_phase")


def require_one_of_target_lowerings(*targets):
    """Return configured target and phase, constrained to shared emitters.

    Some C-lowering code is intentionally shared by multiple VM backends.
    That code must still require an explicitly configured target; it may not
    quietly fall back to one target when setup is missing.
    """
    if not targets:
        raise ValueError("at least one target is required")
    emit_options = runtime.get("emit_options", {})
    actual_target = emit_options.get("target")
    if actual_target not in targets:
        expected = ", ".join(repr(target) for target in targets)
        raise RuntimeError(
            "shared emitter requires one of ({expected}); got {actual!r}".format(
                expected=expected, actual=actual_target
            )
        )
    return actual_target, emit_options.get("max_phase")


def resolve_emitter_headers(inputs):
    """Return the public headers plus LVGL's private declarations.

    Every backend lowers against the same declaration surface.  LVGL's public
    umbrella header deliberately omits a few declarations used by generated
    wrappers, so each native emitter must add the paired private header.
    """
    headers = list(inputs)
    for header in headers:
        if "lvgl.h" not in header:
            continue
        path, _ = os.path.split(header)
        headers.append(
            os.path.join(path, "src", "lvgl_private.h")
            if path and path != "lvgl.h"
            else "src/lvgl_private.h"
        )
        break
    return headers


def target_banner(target, *, include):
    """Return the optional target marker for a generated-file banner."""
    return " *\n * Target: {target}\n".format(target=target) if include else ""


def enum_namespace_plan(*, enums, get_enum_members, is_method_of, is_widget_scoped):
    """Build the common enum namespace relationship plan in declaration order.

    The three targets choose different C representations for enum namespaces,
    but their public nesting and widget-scoped-reference policy is identical.
    Keeping this discovery here makes that contract explicit without imposing a
    VM-specific emitted C shape.
    """
    enum_names = tuple(enums)
    return tuple(
        EnumNamespacePlan(
            name=enum_name,
            members=tuple(get_enum_members(enum_name)),
            nested_names=tuple(
                other for other in enum_names if is_method_of(other, enum_name)
            ),
            widget_scoped_nested_names=tuple(
                other
                for other in enum_names
                if is_method_of(other, enum_name) and is_widget_scoped(other)
            ),
        )
        for enum_name in enum_names
    )


def module_registration_plan(
    *,
    max_phase,
    int_constants,
    generated_globals,
    enums,
    enum_referenced,
    generated_structs,
    struct_aliases,
    obj_names,
    module_funcs,
    public_struct_names=None,
    public_enum_names=None,
):
    """Select the shared public module surface for a completed phase.

    A declaration remains in its original discovery order.  Backends receive
    empty tuples for features not available in the requested phase, rather
    than each reimplementing phase gates and referenced-enum filtering.
    """
    return ModuleRegistrationPlan(
        int_constants=tuple(int_constants) if max_phase >= 1 else (),
        # _nesting (the binding-internal callback re-entrancy counter; see
        # analyze.py and emit_c_micropython_style.py) is deliberately kept
        # in the emitted module globals here even though the canonical API
        # model marks it private: PyDevices' display_driver.py (pydevices
        # lib/) reads it at runtime on MicroPython/CircuitPython. CPython's
        # native emitter never adds it to generated_globals in the first
        # place (it uses its own ContextVar-scoped lvpy_nesting_inc/dec
        # instead), so this is a no-op there.
        generated_globals=(
            tuple(generated_globals) if max_phase >= 1 else ()
        ),
        enum_names=(
            tuple(
                name
                for name in enums
                if name not in enum_referenced
                and (
                    public_enum_names is None
                    or name in public_enum_names
                )
            )
            if max_phase >= 2
            else ()
        ),
        struct_names=(
            tuple(
                name
                for name, generated in generated_structs.items()
                if generated
                and (
                    public_struct_names is None
                    or name in public_struct_names
                )
            )
            if max_phase >= 3
            else ()
        ),
        struct_alias_names=(
            tuple(
                name
                for name, alias in struct_aliases.items()
                if public_struct_names is None
                or alias in public_struct_names
            )
            if max_phase >= 3
            else ()
        ),
        object_names=tuple(obj_names) if max_phase >= 5 else (),
        module_functions=tuple(module_funcs) if max_phase >= 6 else (),
    )


def public_struct_c_names(api_model, target):
    """Return canonical C spellings of public structs for one target."""
    if api_model is None:
        return None
    names = {"C_Pointer"}
    for struct in api_model.structs:
        if struct.visibility != "public" or target not in struct.available_on:
            continue
        if struct.c_name:
            names.add(struct.c_name)
        names.update(struct.typedef_names)
    return frozenset(names)


def public_enum_module_names(api_model, target):
    """Return canonical module-level enum names for one target."""
    if api_model is None:
        return None
    return frozenset(
        enum.module_name
        for enum in api_model.enums
        if enum.visibility == "public"
        and target in enum.available_on
        and enum.module_name is not None
    )


def mp_obj_get_ull_to_bytes_source():
    """Return the VM-version-safe 64-bit integer conversion lowering.

    MicroPython 1.29 renamed ``mp_obj_int_to_bytes_impl`` and changed its
    signature.  CircuitPython 11.0 is built on MicroPython 1.29 and has only
    the new helper; 10.x is MicroPython 1.27 and has only the old one.  On
    CircuitPython, ``MICROPY_VERSION_MAJOR`` is CircuitPython's own major
    (genhdr/mpversion.h), not the core's, so the two are told apart by that.
    The two native emitters share this lowering, so it belongs to their
    shared backend contract rather than to either emitter's large C template.
    """
    return (
        "#if defined(CIRCUITPY) && CIRCUITPY && MICROPY_VERSION_MAJOR < 11\n"
        "    mp_obj_int_to_bytes_impl(obj, big_endian, sizeof(val), (byte*)&val);\n"
        "#elif defined(CIRCUITPY) && CIRCUITPY\n"
        "    mp_obj_int_to_bytes(obj, sizeof(val), (byte*)&val, big_endian, false, false);\n"
        "#elif defined(MICROPY_VERSION_MAJOR) && defined(MICROPY_VERSION_MINOR) && \\\n"
        "    ((MICROPY_VERSION_MAJOR > 1) || "
        "(MICROPY_VERSION_MAJOR == 1 && MICROPY_VERSION_MINOR > 28))\n"
        "    mp_obj_int_to_bytes(obj, sizeof(val), (byte*)&val, big_endian, false, false);\n"
        "#else\n"
        "    mp_obj_int_to_bytes_impl(obj, big_endian, sizeof(val), (byte*)&val);\n"
        "#endif"
    )


def function_return_lowering(
    *,
    return_type,
    qualified_return_type,
    is_pointer,
    lv_to_mp,
    lv_mp_type,
):
    """Lower a resolved LVGL function return through the shared MP surface.

    All three targets present function results through the common ``mp_obj_t``
    compatibility surface, including CPython's native backend.  Conversion
    lookup remains emitter-owned because it may trigger recursive type
    lowering; once available, this rule owns the identical void, pointer-cast,
    and API-metadata behavior.
    """
    if return_type == "void":
        return FunctionReturnLowering("", "mp_const_none", "NoneType")
    return FunctionReturnLowering(
        "%s _res = " % qualified_return_type,
        "{type}({cast}_res)".format(
            type=lv_to_mp[return_type], cast="(void*)" if is_pointer else ""
        ),
        lv_mp_type[return_type],
    )


def callback_return_lowering(*, return_type, mp_to_lv):
    """Lower a callback result after the emitter resolves its conversion.

    Callback conversion discovery stays emitter-owned because it can recurse
    into type generation.  Once that mapping exists, all native targets use
    the same ``mp_call_function_n_kw`` result storage and conversion policy.
    """
    if return_type == "void":
        return CallbackReturnLowering("", "")
    return CallbackReturnLowering(
        "mp_obj_t callback_result = ", " %s(callback_result)" % mp_to_lv[return_type]
    )


def callback_return_conversion_available(*, return_type, mp_to_lv, generate_type):
    """Ensure the conversion used by a callback return is available.

    The recursive type-generation hook remains supplied by the emitter, but
    both native backends follow the same policy: ``void`` needs no conversion;
    every other missing mapping gets exactly one generation attempt before the
    caller reports its existing target-neutral diagnostic.
    """
    return return_type == "void" or conversion_available(
        conversions=mp_to_lv, type_name=return_type, generate_type=generate_type
    )


def conversion_available(*, conversions, type_name, generate_type):
    """Ensure a target-neutral conversion mapping exists, with one retry.

    Conversion maps are populated lazily because lowering a declaration may
    expose additional types.  Native backends share the same rule: use an
    existing non-empty mapping, otherwise generate once and check again.  The
    caller retains the context-specific error text and C lowering.
    """
    if conversions.get(type_name):
        return True
    generate_type()
    return bool(conversions.get(type_name))


def function_reuse_allowed(
    *,
    function_name,
    original_name,
    original_generated,
    supports_dynamic_function_pointer,
):
    """Return whether two equivalent exported functions may share a wrapper.

    A dynamic-function-pointer wrapper can safely stand in for any equivalent
    LVGL declaration. A direct-symbol wrapper, used by the native CPython
    backend, may only reuse itself: reusing it for another symbol would call
    the wrong LVGL function. This is an implementation constraint, not a
    public-API exception.
    """
    if not original_generated:
        return False
    return supports_dynamic_function_pointer or function_name == original_name


def struct_pointer_helpers_source(
    *,
    accept_none,
    unused_qualifier,
    sanitized_struct_name,
    struct_name,
    struct_tag,
):
    """Return the common struct-pointer wrapper lowering.

    Native emitters expose LVGL structs through the same ``mp_lv_struct_t``
    representation.  The CPython compatibility fallback accepts ``None`` for
    nullable write pointers, while MicroPython/CircuitPython retain their
    historic strict conversion.  ``unused_qualifier`` preserves each VM's C
    warning policy without duplicating the conversion contract.
    """
    none_guard = "    if (self_in == mp_const_none) return NULL;\n" if accept_none else ""
    return """static inline const mp_obj_type_t *get_mp_{sanitized_struct_name}_type(void);

{unused_qualifier}static inline void* mp_write_ptr_{sanitized_struct_name}(mp_obj_t self_in)
{{
{none_guard}    mp_lv_struct_t *self = MP_OBJ_TO_PTR(cast(self_in, get_mp_{sanitized_struct_name}_type()));
    return ({struct_tag}{struct_name}*)self->data;
}}

#define mp_write_{sanitized_struct_name}(struct_obj) *(({struct_tag}{struct_name}*)mp_write_ptr_{sanitized_struct_name}(struct_obj))

{unused_qualifier}static inline mp_obj_t mp_read_ptr_{sanitized_struct_name}(void *field)
{{
    return lv_to_mp_struct(get_mp_{sanitized_struct_name}_type(), field);
}}""".format(
        none_guard=none_guard,
        unused_qualifier=unused_qualifier,
        sanitized_struct_name=sanitized_struct_name,
        struct_tag=struct_tag,
        struct_name=struct_name,
    )
