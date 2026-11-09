# SPDX-FileCopyrightText: 2026 Brad Barnett
#
# SPDX-License-Identifier: MIT

"""Target-neutral C declaration intermediate representation.

The IR deliberately contains declarations only.  Target runtime policy,
argument conversion, public-export decisions, and C emission belong to later
pipeline stages.  This module has no dependency on any binding target.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Optional, Sequence, Tuple

from pycparser import c_ast, c_generator, c_parser


@dataclass(frozen=True)
class SourceLocation:
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None

    @classmethod
    def from_coord(cls, coord: Any) -> "SourceLocation":
        if coord is None:
            return cls()
        return cls(
            file=getattr(coord, "file", None),
            line=getattr(coord, "line", None),
            column=getattr(coord, "column", None),
        )


@dataclass(frozen=True)
class CType:
    """A normalized C type expression."""

    kind: str
    name: Optional[str] = None
    qualifiers: Tuple[str, ...] = ()
    target: Optional["CType"] = None
    element: Optional["CType"] = None
    dimensions: Tuple[str, ...] = ()
    return_type: Optional["CType"] = None
    parameters: Tuple["CParameter", ...] = ()
    variadic: bool = False

    def canonical(self) -> str:
        qualifiers = " ".join(self.qualifiers)
        prefix = (qualifiers + " ") if qualifiers else ""
        if self.kind in {"primitive", "identifier"}:
            return prefix + (self.name or "<anonymous>")
        if self.kind in {"struct", "union", "enum"}:
            return prefix + self.kind + " " + (self.name or "<anonymous>")
        if self.kind == "pointer":
            target = self.target.canonical() if self.target else "void"
            pointer_qualifiers = " ".join(self.qualifiers)
            suffix = " *"
            if pointer_qualifiers:
                suffix += " " + pointer_qualifiers
            return target + suffix
        if self.kind == "array":
            suffix = "".join("[" + dimension + "]" for dimension in self.dimensions)
            return (self.element.canonical() if self.element else "<unknown>") + suffix
        if self.kind == "function":
            args = ", ".join(parameter.type.canonical() for parameter in self.parameters)
            if self.variadic:
                args = (args + ", ") if args else ""
                args += "..."
            return "{} ({})".format(
                self.return_type.canonical() if self.return_type else "void",
                args,
            )
        if self.kind == "ellipsis":
            return "..."
        return prefix + (self.name or "<unknown>")


@dataclass(frozen=True)
class CParameter:
    name: Optional[str]
    type: CType
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class CField:
    name: Optional[str]
    type: CType
    location: SourceLocation = field(default_factory=SourceLocation)
    bit_width: Optional[str] = None


@dataclass(frozen=True)
class CFunction:
    name: str
    return_type: CType
    parameters: Tuple[CParameter, ...]
    variadic: bool = False
    storage: Tuple[str, ...] = ()
    function_specifiers: Tuple[str, ...] = ()
    is_definition: bool = False
    location: SourceLocation = field(default_factory=SourceLocation)

    @property
    def signature(self) -> str:
        args = ", ".join(parameter.type.canonical() for parameter in self.parameters)
        if self.variadic:
            args = (args + ", ") if args else ""
            args += "..."
        return "{} {}({})".format(self.return_type.canonical(), self.name, args)


@dataclass(frozen=True)
class CStruct:
    name: Optional[str]
    kind: str
    fields: Tuple[CField, ...] = ()
    typedef_names: Tuple[str, ...] = ()
    complete: bool = False
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class CEnum:
    name: Optional[str]
    members: Tuple[str, ...] = ()
    typedef_names: Tuple[str, ...] = ()
    complete: bool = False
    values: Tuple[Tuple[str, Optional[str]], ...] = ()
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class CTypedef:
    name: str
    type: CType
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class CVariable:
    name: str
    type: CType
    storage: Tuple[str, ...] = ()
    location: SourceLocation = field(default_factory=SourceLocation)


@dataclass(frozen=True)
class DeclarationIR:
    """All declarations from one preprocessed translation unit."""

    functions: Tuple[CFunction, ...] = ()
    structs: Tuple[CStruct, ...] = ()
    enums: Tuple[CEnum, ...] = ()
    typedefs: Tuple[CTypedef, ...] = ()
    variables: Tuple[CVariable, ...] = ()

    @property
    def functions_by_name(self) -> Mapping[str, CFunction]:
        return {function.name: function for function in self.functions}

    @property
    def typedefs_by_name(self) -> Mapping[str, CTypedef]:
        return {typedef.name: typedef for typedef in self.typedefs}

    @property
    def callback_typedefs(self) -> Mapping[str, CType]:
        return {
            typedef.name: typedef.type
            for typedef in self.typedefs
            if typedef.type.kind == "pointer"
            and typedef.type.target is not None
            and typedef.type.target.kind == "function"
        }


@dataclass(frozen=True)
class DeclarationIndex:
    """Read-only indexes and relationship queries over `DeclarationIR`."""

    ir: DeclarationIR
    functions_by_name: Mapping[str, CFunction]
    structs_by_name: Mapping[str, CStruct]
    enums_by_name: Mapping[str, CEnum]
    typedefs_by_name: Mapping[str, CTypedef]
    struct_aliases: Mapping[str, str]
    struct_tag_aliases: Mapping[str, str]
    module_prefix: str = "lv"

    @classmethod
    def from_ir(cls, ir: DeclarationIR, module_prefix: str = "lv") -> "DeclarationIndex":
        structs = {}
        aliases = {}
        tag_aliases = {}
        for struct in ir.structs:
            if struct.name:
                structs[struct.name] = struct
            for alias in struct.typedef_names:
                structs[alias] = struct
                if struct.name:
                    aliases[alias] = struct.name
                    tag_aliases.setdefault(struct.name, alias)
        enums = {}
        for enum in ir.enums:
            if enum.name:
                enums[enum.name] = enum
            for alias in enum.typedef_names:
                enums[alias] = enum
        return cls(
            ir=ir,
            functions_by_name={function.name: function for function in ir.functions},
            structs_by_name=structs,
            enums_by_name=enums,
            typedefs_by_name={typedef.name: typedef for typedef in ir.typedefs},
            struct_aliases=aliases,
            struct_tag_aliases=tag_aliases,
            module_prefix=module_prefix,
        )

    @staticmethod
    def _without_qualifiers(type_: CType) -> str:
        if type_.kind in {"identifier", "primitive", "struct", "union", "enum"}:
            return type_.name or type_.canonical()
        if type_.kind == "pointer":
            target = (
                DeclarationIndex._without_qualifiers(type_.target)
                if type_.target is not None
                else "void"
            )
            return target + " *"
        if type_.kind == "array":
            element = (
                DeclarationIndex._without_qualifiers(type_.element)
                if type_.element is not None
                else "<unknown>"
            )
            return element + "".join("[" + dim + "]" for dim in type_.dimensions)
        return type_.canonical()

    @classmethod
    def _first_argument_type_name(cls, type_: CType) -> Optional[str]:
        # Inspect one pointer/array layer, but
        # retain a second pointer layer (T ** is not a T struct receiver).
        if type_.kind in {"pointer", "array"}:
            type_ = type_.target or type_.element
        if type_ is None:
            return None
        return cls._without_qualifiers(type_)

    def first_argument_type_name(self, function_name: str) -> Optional[str]:
        function = self.functions_by_name.get(function_name)
        if function is None or not function.parameters:
            return None
        name = self._first_argument_type_name(function.parameters[0].type)
        return self.struct_tag_aliases.get(name, name)

    def _struct_identity(self, name: Optional[str]) -> Optional[str]:
        if not name:
            return None
        struct = self.structs_by_name.get(name)
        if struct is not None and struct.name:
            return struct.name
        return self.struct_aliases.get(name, name)

    @staticmethod
    def _struct_stems(name: Optional[str]) -> Tuple[str, ...]:
        if not name:
            return ()
        names = {name}
        if name.endswith("_t"):
            names.add(name[:-2])
        return tuple(names)

    def is_struct_function(self, function_name: str, struct_name: str) -> bool:
        if struct_name not in self.structs_by_name:
            return False
        first_type = self.first_argument_type_name(function_name)
        if self._struct_identity(first_type) != self._struct_identity(struct_name):
            return False
        # Preserve the established relationship rule: a common identifier
        # prefix is enough, even when the first argument's struct tag has a
        # longer suffix (for example lv_obj_class_t/lv_obj_event_base).
        function_name = self._simplify(function_name)
        struct_name = self._simplify(struct_name)
        common_length = 0
        for left, right in zip(function_name, struct_name):
            if left != right:
                break
            common_length += 1
        if common_length == 0:
            return False
        index = common_length - 1
        while index > 0 and function_name[index] != "_":
            index -= 1
        return function_name[index + 1 :] != function_name

    def _simplify(self, name: str) -> str:
        prefix = self.module_prefix + "_"
        return name[len(prefix) :] if name.startswith(prefix) else name

    def struct_functions(self, struct_name: str) -> Tuple[CFunction, ...]:
        return tuple(
            function
            for function in self.ir.functions
            if self.is_struct_function(function.name, struct_name)
        )


class _Converter:
    def __init__(self) -> None:
        self.generator = c_generator.CGenerator()

    def location(self, node: Any) -> SourceLocation:
        return SourceLocation.from_coord(getattr(node, "coord", None))

    def expression(self, node: Any) -> str:
        if node is None:
            return ""
        return self.generator.visit(node)

    def type(self, node: Any) -> CType:
        if isinstance(node, c_ast.TypeDecl):
            result = self.type(node.type)
            if node.quals:
                result = CType(
                    kind=result.kind,
                    name=result.name,
                    qualifiers=tuple(node.quals) + result.qualifiers,
                    target=result.target,
                    element=result.element,
                    dimensions=result.dimensions,
                    return_type=result.return_type,
                    parameters=result.parameters,
                    variadic=result.variadic,
                )
            return result
        if isinstance(node, c_ast.IdentifierType):
            names = tuple(node.names)
            primitive_names = {
                "_Bool",
                "bool",
                "char",
                "double",
                "float",
                "int",
                "long",
                "short",
                "signed",
                "unsigned",
                "void",
            }
            kind = "primitive" if set(names) <= primitive_names else "identifier"
            return CType(kind=kind, name=" ".join(names))
        if isinstance(node, c_ast.PtrDecl):
            return CType(
                kind="pointer",
                qualifiers=tuple(node.quals or ()),
                target=self.type(node.type),
            )
        if isinstance(node, c_ast.ArrayDecl):
            dimension = self.expression(node.dim)
            return CType(
                kind="array",
                element=self.type(node.type),
                dimensions=(dimension,),
            )
        if isinstance(node, c_ast.FuncDecl):
            parameters, variadic = self.parameters(node.args)
            return CType(
                kind="function",
                return_type=self.type(node.type),
                parameters=parameters,
                variadic=variadic,
            )
        if isinstance(node, c_ast.Struct):
            return CType(kind="struct", name=node.name)
        if isinstance(node, c_ast.Union):
            return CType(kind="union", name=node.name)
        if isinstance(node, c_ast.Enum):
            return CType(kind="enum", name=node.name)
        if isinstance(node, c_ast.EllipsisParam):
            return CType(kind="ellipsis", name="...")
        if isinstance(node, c_ast.Typename):
            return self.type(node.type)
        return CType(kind="unknown", name=self.generator.visit(node))

    def parameter(self, node: Any) -> CParameter:
        if isinstance(node, c_ast.EllipsisParam):
            return CParameter(name=None, type=CType(kind="ellipsis", name="..."))
        return CParameter(
            name=getattr(node, "name", None),
            type=self.type(node.type),
            location=self.location(node),
        )

    def parameters(self, node: Any) -> Tuple[Tuple[CParameter, ...], bool]:
        if node is None or not node.params:
            return (), False
        variadic = any(isinstance(parameter, c_ast.EllipsisParam) for parameter in node.params)
        parameters = tuple(
            self.parameter(parameter)
            for parameter in node.params
            if not isinstance(parameter, c_ast.EllipsisParam)
        )
        # In a C prototype, ``(void)`` means no parameters.  pycparser keeps
        # the ``void`` Typename node, so normalize it here rather than making
        # every target backend special-case a phantom argument.
        if (
            not variadic
            and len(parameters) == 1
            and parameters[0].name is None
            and parameters[0].type.kind == "primitive"
            and parameters[0].type.name == "void"
            and not parameters[0].type.qualifiers
        ):
            parameters = ()
        return parameters, variadic

    def fields(self, node: Any) -> Tuple[CField, ...]:
        if not node.decls:
            return ()
        result = []
        for declaration in node.decls:
            result.append(
                CField(
                    name=declaration.name,
                    type=self.type(declaration.type),
                    location=self.location(declaration),
                    bit_width=self.expression(declaration.bitsize)
                    if declaration.bitsize is not None
                    else None,
                )
            )
        return tuple(result)

    def struct(self, node: Any, typedef_names: Sequence[str] = ()) -> CStruct:
        kind = "union" if isinstance(node, c_ast.Union) else "struct"
        return CStruct(
            name=node.name,
            kind=kind,
            fields=self.fields(node),
            typedef_names=tuple(typedef_names),
            complete=node.decls is not None,
            location=self.location(node),
        )

    def enum(self, node: c_ast.Enum, typedef_names: Sequence[str] = ()) -> CEnum:
        members = ()
        values = ()
        if node.values is not None:
            enumerators = node.values.enumerators or ()
            members = tuple(enumerator.name for enumerator in enumerators)
            values = tuple(
                (
                    enumerator.name,
                    self.expression(enumerator.value)
                    if enumerator.value is not None
                    else None,
                )
                for enumerator in enumerators
            )
        return CEnum(
            name=node.name,
            members=members,
            typedef_names=tuple(typedef_names),
            complete=node.values is not None,
            values=values,
            location=self.location(node),
        )


def _function_from_decl(converter: _Converter, declaration: Any, is_definition=False):
    function_type = declaration.type
    parameters, variadic = converter.parameters(function_type.args)
    return CFunction(
        name=declaration.name,
        return_type=converter.type(function_type.type),
        parameters=parameters,
        variadic=variadic,
        storage=tuple(declaration.storage or ()),
        function_specifiers=tuple(declaration.funcspec or ()),
        is_definition=is_definition,
        location=converter.location(declaration),
    )


def parse_ast(ast: c_ast.FileAST) -> DeclarationIR:
    """Convert a pycparser AST to target-neutral declarations."""

    converter = _Converter()
    functions = []
    structs = []
    enums = []
    typedefs = []
    variables = []
    struct_positions = {}
    enum_positions = {}

    def add_struct(node, typedef_names=()):
        kind = "union" if isinstance(node, c_ast.Union) else "struct"
        key = (kind, node.name) if node.name else (kind, id(node))
        declaration = converter.struct(node, typedef_names)
        if key not in struct_positions:
            struct_positions[key] = len(structs)
            structs.append(declaration)
            return
        position = struct_positions[key]
        previous = structs[position]
        typedefs = tuple(dict.fromkeys(previous.typedef_names + declaration.typedef_names))
        complete = previous.complete or declaration.complete
        fields = declaration.fields if declaration.complete else previous.fields
        location = (
            declaration.location
            if declaration.complete and not previous.complete
            else previous.location
        )
        structs[position] = CStruct(
            name=previous.name or declaration.name,
            kind=previous.kind,
            fields=fields,
            typedef_names=typedefs,
            complete=complete,
            location=location,
        )

    def add_enum(node, typedef_names=()):
        key = ("named", node.name) if node.name else ("anonymous", id(node))
        declaration = converter.enum(node, typedef_names)
        if key not in enum_positions:
            enum_positions[key] = len(enums)
            enums.append(declaration)
            return
        position = enum_positions[key]
        previous = enums[position]
        typedefs = tuple(dict.fromkeys(previous.typedef_names + declaration.typedef_names))
        complete = previous.complete or declaration.complete
        members = declaration.members if declaration.complete else previous.members
        values = declaration.values if declaration.complete else previous.values
        location = (
            declaration.location
            if declaration.complete and not previous.complete
            else previous.location
        )
        enums[position] = CEnum(
            name=previous.name or declaration.name,
            members=members,
            typedef_names=typedefs,
            complete=complete,
            values=values,
            location=location,
        )

    def typedef_composite(node):
        """Return a composite directly named by a typedef, if present."""

        if isinstance(node, c_ast.TypeDecl) and isinstance(
            node.type, (c_ast.Struct, c_ast.Union, c_ast.Enum)
        ):
            return node.type
        return None

    for external in ast.ext:
        if isinstance(external, c_ast.FuncDef):
            functions.append(_function_from_decl(converter, external.decl, True))
            continue
        if isinstance(external, c_ast.Typedef):
            typedefs.append(
                CTypedef(
                    name=external.name,
                    type=converter.type(external.type),
                    location=converter.location(external),
                )
            )
            composite = typedef_composite(external.type)
            if isinstance(composite, (c_ast.Struct, c_ast.Union)):
                add_struct(composite, (external.name,))
            elif isinstance(composite, c_ast.Enum):
                add_enum(composite, (external.name,))
            continue
        if not isinstance(external, c_ast.Decl):
            continue
        if isinstance(external.type, c_ast.FuncDecl):
            functions.append(_function_from_decl(converter, external))
        elif isinstance(external.type, (c_ast.Struct, c_ast.Union)):
            add_struct(external.type)
            if external.name:
                variables.append(
                    CVariable(
                        name=external.name,
                        type=converter.type(external.type),
                        storage=tuple(external.storage or ()),
                        location=converter.location(external),
                    )
                )
        elif isinstance(external.type, c_ast.Enum):
            add_enum(external.type)
        elif external.name:
            variables.append(
                CVariable(
                    name=external.name,
                    type=converter.type(external.type),
                    storage=tuple(external.storage or ()),
                    location=converter.location(external),
                )
            )

    unique_functions = []
    function_positions = {}
    for function in functions:
        previous_position = function_positions.get(function.name)
        if previous_position is None:
            function_positions[function.name] = len(unique_functions)
            unique_functions.append(function)
            continue
        previous = unique_functions[previous_position]
        if previous.signature != function.signature:
            raise ValueError(
                "conflicting declarations for %s: %s / %s"
                % (function.name, previous.signature, function.signature)
            )
        if function.is_definition and not previous.is_definition:
            unique_functions[previous_position] = function

    return DeclarationIR(
        functions=tuple(unique_functions),
        structs=tuple(structs),
        enums=tuple(enums),
        typedefs=tuple(typedefs),
        variables=tuple(variables),
    )


def parse_source(source: str, filename: str = "<none>", parser=None) -> DeclarationIR:
    """Parse C source and return a target-neutral declaration IR."""

    parser = parser or c_parser.CParser()
    return parse_ast(parser.parse(source, filename=filename))
