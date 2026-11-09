# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Low-level pycparser AST helpers used by analyze and emit."""
from __future__ import print_function

import copy

from pycparser import c_ast, c_generator

from .util import memoize

@memoize
def remove_declname(ast):
    if hasattr(ast, "declname"):
        ast.declname = None
    if isinstance(ast, tuple):
        remove_declname(ast[1])
        return
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        remove_declname(child)


@memoize
def add_default_declname(ast, name):
    if hasattr(ast, "declname"):
        if ast.declname == None:
            ast.declname = name
    if isinstance(ast, tuple):
        add_default_declname(ast[1], name)
        return
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        add_default_declname(child, name)


@memoize
def convert_array_to_ptr(ast):
    if hasattr(ast, "type") and isinstance(ast.type, c_ast.ArrayDecl):
        ast.type = c_ast.PtrDecl(
            ast.type.quals if hasattr(ast.type, "quals") else [], ast.type.type
        )
    if isinstance(ast, tuple):
        return convert_array_to_ptr(ast[1])
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        convert_array_to_ptr(child)


@memoize
def remove_quals(ast):
    if hasattr(ast, "quals"):
        ast.quals = []
    if hasattr(ast, "dim_quals"):
        ast.dim_quals = []
    if isinstance(ast, tuple):
        return remove_quals(ast[1])
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        if not isinstance(
            child, c_ast.FuncDecl
        ):  # Don't remove quals which change function prototype
            remove_quals(child)


from .util import memoize


def _emit():
    from . import runtime

    return runtime.current_context()


@memoize
def remove_explicit_struct(ast):
    em = _emit()
    if isinstance(ast, c_ast.TypeDecl) and isinstance(ast.type, c_ast.Struct):
        explicit_struct_name = ast.type.name
        if explicit_struct_name:
            if explicit_struct_name in em.explicit_structs:
                ast.type = c_ast.IdentifierType(
                    [em.explicit_structs[explicit_struct_name]]
                )
            elif explicit_struct_name in em.structs:
                ast.type = c_ast.IdentifierType([explicit_struct_name])
    if isinstance(ast, tuple):
        return remove_explicit_struct(ast[1])
    for i, c1 in enumerate(ast.children()):
        child = ast.children()[i]
        remove_explicit_struct(child)


@memoize
def get_type(arg, **kwargs):
    if isinstance(arg, str):
        return arg
    remove_quals_arg = "remove_quals" in kwargs and kwargs["remove_quals"]
    arg_ast = copy.deepcopy(arg)
    remove_explicit_struct(arg_ast)
    if remove_quals_arg:
        remove_quals(arg_ast)
    return _emit().gen.visit(arg_ast)


@memoize
def get_name(type):
    em = _emit()
    if isinstance(type, c_ast.Decl):
        return type.name
    if isinstance(type, c_ast.Struct) and type.name and type.name in em.explicit_structs:
        return em.explicit_structs[type.name]
    if isinstance(type, c_ast.Struct):
        return type.name
    if isinstance(type, c_ast.TypeDecl):
        return type.declname
    if isinstance(type, c_ast.IdentifierType):
        return type.names[0]
    if isinstance(type, c_ast.FuncDecl):
        return type.type.declname
    # if isinstance(type, (c_ast.PtrDecl, c_ast.ArrayDecl)) and hasattr(type.type, 'declname'):
    #     return type.type.declname
    if isinstance(type, (c_ast.PtrDecl, c_ast.ArrayDecl)):
        return get_type(type, remove_quals=True)
    else:
        return em.gen.visit(type)


@memoize
def remove_arg_names(ast):
    if isinstance(ast, c_ast.TypeDecl):
        ast.declname = None
        remove_arg_names(ast.type)
    elif isinstance(ast, c_ast.Decl):
        remove_arg_names(ast.type)
    elif isinstance(ast, c_ast.FuncDecl):
        remove_arg_names(ast.args)
    elif isinstance(ast, c_ast.ParamList):
        for param in ast.params:
            remove_arg_names(param)


# Create a function prototype AST from a function AST
@memoize
def function_prototype(func):
    bare_func = copy.deepcopy(func)
    remove_declname(bare_func)

    ptr_decl = c_ast.PtrDecl(quals=[], type=bare_func.type)

    func_proto = c_ast.Typename(name=None, quals=[], align=[], type=ptr_decl)

    return func_proto
