import abc
from ast import *
from collections.abc import Iterable

from qchecker.descriptions import get_description
from qchecker.match import Match, TextRange

from ._utils import nodes_of_class, is_compliment, compliment_bools, \
    assign_types, assigning_to_same_target, get_assign_target, dirty_compare, \
    match_ends


class Substructure(abc.ABC):
    @classmethod
    @property
    @abc.abstractmethod
    def name(cls) -> str:
        """Name of the substructure"""

    @classmethod
    @property
    @abc.abstractmethod
    def technical_description(cls) -> str:
        """Compact description of the substructure as it is detected"""

    @classmethod
    @property
    def description(cls):
        return get_description(cls.__name__)

    @classmethod
    def match(cls, from_node, to_node):
        return Match(
            cls.__name__,
            cls.description,
            TextRange(
                from_node.lineno,
                from_node.col_offset,
                to_node.end_lineno,
                to_node.end_col_offset,
            ),
        )

    @classmethod
    @abc.abstractmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        """Iterates over all matching substructures in the given module"""


class UnnecessaryElif(Substructure):
    name = "Unnecessary Elif"
    technical_description = "If(cond)[..] Elif(!cond)[..]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(test=t1, orelse=[If(test=t2)]) if is_compliment(t1, t2):
                    yield cls.match(node, node)


class IfElseReturnBool(Substructure):
    name = "If/Else Return Bool"
    technical_description = "If(..)[Return bool] Else[Return !bool]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Return(Constant(r1))],
                    orelse=[Return(Constant(r2))]
                ) if compliment_bools(r1, r2):
                    yield cls.match(node, node)


class IfReturnBool(Substructure):
    name = "If Return Bool"
    technical_description = "If(..)[Return bool], Return !bool"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, FunctionDef):
            match node:
                case FunctionDef(
                    body=[
                        *_,
                        If(body=[Return(Constant(v1))]) as n1,
                        Return(Constant(v2)) as n2,
                    ]
                ) if compliment_bools(v1, v2):
                    yield cls.match(n1, n2)


class IfElseAssignReturn(Substructure):
    name = "If/Else Assign Return"
    technical_description = "If(..)[name=..] Else[name=..], Return name"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        # ToDo - Make this better
        for node in nodes_of_class(module, FunctionDef):
            match node:
                case FunctionDef(
                    body=[*_,
                          If(body=[a1], orelse=[a2]) as n1,
                          Return(Name() as v1) as n2]
                ) if (
                        isinstance(a1, assign_types)
                        and isinstance(a2, assign_types)
                        and assigning_to_same_target(a1, a2)
                        and [a.id for a in get_assign_target(a1)] == [v1.id]
                ):
                    yield cls.match(n1, n2)


class IfElseAssignBoolReturn(Substructure):
    name = "If/Else Assign Bool Return"
    technical_description = "If(..)[name=bool] Else[name=!bool], Return name"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, FunctionDef):
            match node:
                case FunctionDef(
                    body=[
                        *_,
                        If(body=[Assign([t1], Constant(b1))],
                           orelse=[Assign([t2], Constant(b2))]) as n1,
                        Return(Name(t3)) as n2
                    ]
                ) if (
                        compliment_bools(b1, b2)
                        and dirty_compare(t1, t2)
                        and t1.id == t3
                ):
                    yield cls.match(n1, n2)


class IfElseAssignBool(Substructure):
    name = "If/Else Assign Bool"
    technical_description = "If(..)[name=bool] Else[name=!bool]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Assign([t1], Constant(b1))],
                    orelse=[Assign([t2], Constant(b2))]
                ) if (
                        compliment_bools(b1, b2)
                        and dirty_compare(t1, t2)
                ):
                    yield cls.match(node, node)


class EmptyIfBody(Substructure):
    name = "Empty If Body"
    technical_description = "If(..)[Pass|Constant|name=name]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                # ToDo - Check name=name
                case If(body=[Expr(Constant()) | Pass()]):
                    yield cls.match(node, node)


class EmptyElseBody(Substructure):
    name = "Empty Else Body"
    technical_description = "If(..)[..] Else[Pass|Constant|name=name]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                # ToDo - Check name=name
                case If(orelse=[Expr(Constant()) | Pass()]):
                    yield cls.match(node, node)


class NestedIf(Substructure):
    name = "Nested If"
    technical_description = "If(..)[If(..)[..]]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[If()]):
                    yield cls.match(node, node)


class ConfusingElse(Substructure):
    name = "Confusing Else"
    technical_description = "If(..)[..] Else[If(..)[..] Else[..]]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(orelse=[If(orelse=orselse) as inner]) if len(orselse):
                    yield cls.match(inner, inner)


class UnnecessaryElse(Substructure):
    name = "Unnecessary Else"
    technical_description = "If(..)[*.., stmt] Else[stmt]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[*_, _, s1], orelse=[s2]) if dirty_compare(s1, s2):
                    yield cls.match(node, node)


class DuplicateIfElseStatement(Substructure):
    name = "Duplicate If/Else Statement"
    technical_description = "If(..)[.., stmt] Else[.., stmt]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[*_, _, s1],
                    orelse=[*_, _, s2]
                ) if dirty_compare(s1, s2):
                    yield cls.match(node, node)


class SeveralDuplicateIfElseStatements(Substructure):
    name = "Several Duplicate If/Else Statements"
    technical_description = "If(..)[.., *stmts] Else[.., *stmts]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if match_ends(b1, b2) > 1:
                    yield cls.match(node, node)


class DuplicateIfElseBody(Substructure):
    name = "Duplicate If/Else Body"
    technical_description = "If(..)[body] Else[body]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if dirty_compare(b1, b2):
                    yield cls.match(node, node)


class DeclarationAssignmentDivision(Substructure):
    name = "Declaration/Assignment Division"
    technical_description = "name: type, name=.."

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        # ToDo - Make this better
        declared_names = set()
        for ann_assign in nodes_of_class(module, AnnAssign):
            if ann_assign.simple == 1 and isinstance(ann_assign.target, Name):
                declared_names.add(ann_assign.target.id)
        for name in nodes_of_class(module, Name):
            if name.id in declared_names and isinstance(name.ctx, Store):
                yield cls.match(name, name)


# ToDo – One of these days the API will be stable! I'm sure of it
__all__ = [
    'Substructure',
    *(cls.__name__ for cls in Substructure.__subclasses__())
]
