import abc
from ast import *
from collections.abc import Iterable
from itertools import chain

from qchecker.descriptions import get_description
from qchecker.match import Match, TextRange

from ._utils import *

__all__ = [
    'Substructure',
    'UnnecessaryElif',
    'IfElseReturnBool',
    'IfReturnBool',
    'IfElseAssignReturn',
    'IfElseAssignBoolReturn',
    'IfElseAssignBool',
    'EmptyIfBody',
    'EmptyElseBody',
    'NestedIf',
    'ConfusingElse',
    'UnnecessaryElse',
    'DuplicateIfElseStatement',
    'SeveralDuplicateIfElseStatements',
    'DuplicateIfElseBody',
    'DeclarationAssignmentDivision',
    'AugmentableAssignment',
    'DuplicateExpression',
]


class Substructure(abc.ABC):
    subsets: list['Substructure'] = []

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
    def match_collides_with_subset(cls, module, match):
        matches = chain(*(sub_struct.iter_matches(module)
                          for sub_struct in cls.subsets))
        return any(submatch.text_range.contains(match.text_range)
                   for submatch in matches)

    @classmethod
    def match(cls, from_node, to_node):
        return Match(
            cls.name,
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

    @classmethod
    def count_matches(cls, module: Module) -> int:
        """Returns the number of matching substructures in the given module"""
        return len(list(cls.iter_matches(module)))


class UnnecessaryElif(Substructure):
    name = "Unnecessary Elif"
    technical_description = "If(cond)[..] Elif(!cond)[..]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    test=t1, orelse=[If(test=t2)]
                ) if are_compliment_operations(t1, t2):
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
                ) if are_compliment_bools(r1, r2):
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
                ) if are_compliment_bools(v1, v2):
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
                        are_compliment_bools(b1, b2)
                        and dirty_compare(t1, t2)
                        and t1.id == t3
                ):
                    yield cls.match(n1, n2)


class IfElseAssignReturn(Substructure):
    name = "If/Else Assign Return"
    technical_description = "If(..)[name=..] Else[name=..], Return name"
    subsets = [IfElseAssignBoolReturn]

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, FunctionDef):
            match node:
                case FunctionDef(
                    body=[
                        *_,
                        If(
                            body=[
                                Assign(targets=[Name(id=n1)])
                                | AnnAssign(target=Name(id=n1))
                                | AugAssign(target=Name(id=n1))
                            ],
                            orelse=[
                                Assign(targets=[Name(id=n2)])
                                | AnnAssign(target=Name(id=n2))
                                | AugAssign(target=Name(id=n2))
                            ],
                        ) as node1,
                        Return(Name(id=n3)) as node2,
                    ]
                ) if n1 == n2 == n3:
                    match = cls.match(node1, node2)
                    if not cls.match_collides_with_subset(module, match):
                        yield match


class IfElseAssignBool(Substructure):
    name = "If/Else Assign Bool"
    technical_description = "If(..)[name=bool] Else[name=!bool]"
    subsets = [IfElseAssignBoolReturn]

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Assign([t1], Constant(b1))],
                    orelse=[Assign([t2], Constant(b2))]
                ) if (
                        are_compliment_bools(b1, b2)
                        and dirty_compare(t1, t2)
                ):
                    match = cls.match(node, node)
                    if not cls.match_collides_with_subset(module, match):
                        yield match


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
                    body=b1, orelse=b2
                ) if (
                        match_ends(b1, b2) == 1
                        and len(b1) > 1
                        and len(b2) > 1
                        and not dirty_compare(b1, b2)
                ):
                    yield cls.match(node, node)


class SeveralDuplicateIfElseStatements(Substructure):
    name = "Several Duplicate If/Else Statements"
    technical_description = "If(..)[.., *stmts] Else[.., *stmts]"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=b1, orelse=b2
                ) if (
                        match_ends(b1, b2) > 1
                        and not dirty_compare(b1, b2)
                ):
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
    technical_description = "name: type"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        yield from (cls.match(assign, assign)
                    for assign in nodes_of_class(module, AnnAssign)
                    if assign.simple == 1)


class AugmentableAssignment(Substructure):
    name = "Augmentable Assignment"
    technical_description = "name = name Op() .. | .. [+*] name"

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, Assign):
            match node:
                case Assign(
                    targets=[Name(id=n1)],
                    value=BinOp(left=Name(id=n2)),
                ) if n1 == n2:
                    yield cls.match(node, node)
                case Assign(
                    targets=[Name(id=n1)],
                    value=BinOp(
                        # ToDo - Check for other commutative ops
                        op=Add() | Mult(),
                        right=Name(id=n2)
                    )
                ) if n1 == n2:
                    yield cls.match(node, node)


class DuplicateExpression(Substructure):
    name = "Duplicate Expression"
    # ToDo – Clarify Effenberger2022Code definition. It is not clear if they
    #  are using the term expression formally or colloquially or whether they
    #  account for control flow
    technical_description = (
        "Module contains two expressions with more than 8 names, literals, "
        "or operators. Operators count for two tokens."
    )

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[Match]:
        # ToDo - consider using something like leoAst.py. Would require a
        #  large refactor. http://leoeditor.com/appendices.html#leoast-py
        expressions = nodes_of_class(module, expr)
        expressions = [n for n in expressions if weight_of(n) >= 8]
        duplicates = set()
        for i in range(len(expressions)):
            for j in range(i + 1, len(expressions)):
                if (expressions[j] not in duplicates
                        and dirty_compare(expressions[i], expressions[j])):
                    duplicates.add(expressions[i])
                    break
        yield from (cls.match(exp, exp) for exp in duplicates)
