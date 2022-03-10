import abc
from ast import *
from collections.abc import Iterable
from itertools import chain

from qchecker.match import Match, TextRange
from qchecker.substructures._base import Substructure

from ._utils import *

__all__ = [
    'UnnecessaryElif',
    'IfElseReturnBool',
    'IfReturnBool',
    'IfElseAssignReturn',
    'IfElseAssignBoolReturn',
    'IfElseAssignBool',
    'EmptyIfBody',
    'EmptyElseBody',
    'NestedIf',
    'UnnecessaryElse',
    'DuplicateIfElseStatement',
    'SeveralDuplicateIfElseStatements',
    'DuplicateIfElseBody',
    'DeclarationAssignmentDivision',
    'AugmentableAssignment',
    'DuplicateExpression',
    'MissedAbsoluteValue',
    'RepeatedAddition',
]


class ASTSubstructure(Substructure, abc.ABC):
    @classmethod
    def iter_matches(cls, code: str) -> Iterable[Match]:
        # All problems in computer science
        # can be solved by another level of indirection.
        module = parse(code)
        yield from cls._iter_matches(module)

    @classmethod
    @abc.abstractmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        """Iterates over matches found in the AST"""

    @classmethod
    def match_collides_with_subset(cls, module, match):
        matches = chain(*(sub_struct.iter_matches(module)
                          for sub_struct in cls.subsets))
        return any(submatch.text_range.contains(match.text_range)
                   for submatch in matches)

    @classmethod
    def _make_match(cls, from_node, to_node):
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


class UnnecessaryElif(ASTSubstructure):
    name = "Unnecessary Elif"
    technical_description = "If(cond)[..] Elif(!cond)[..]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    test=t1, orelse=[If(test=t2)]
                ) if (
                    are_compliment_operations(t1, t2)
                ):
                    yield cls._make_match(node, node)


class IfElseReturnBool(ASTSubstructure):
    # Covered by pylint-R1703
    name = "If/Else Return Bool"
    technical_description = "If(..)[Return bool] Else[Return !bool]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Return(Constant(r1))],
                    orelse=[Return(Constant(r2))]
                ) if are_compliment_bools(r1, r2):
                    yield cls._make_match(node, node)


class IfReturnBool(ASTSubstructure):
    name = "If Return Bool"
    technical_description = "If(..)[Return bool], Return !bool"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, FunctionDef):
            match node:
                case FunctionDef(
                    body=[
                        *_,
                        If(body=[Return(Constant(v1))]) as n1,
                        Return(Constant(v2)) as n2,
                    ]
                ) if are_compliment_bools(v1, v2):
                    yield cls._make_match(n1, n2)


class IfElseAssignBoolReturn(ASTSubstructure):
    name = "If/Else Assign Bool Return"
    technical_description = "If(..)[name=bool] Else[name=!bool], Return name"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
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
                    yield cls._make_match(n1, n2)


class IfElseAssignReturn(ASTSubstructure):
    name = "If/Else Assign Return"
    technical_description = "If(..)[name=..] Else[name=..], Return name"
    subsets = [IfElseAssignBoolReturn]

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
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
                    match = cls._make_match(node1, node2)
                    if not cls.match_collides_with_subset(module, match):
                        yield match


class IfElseAssignBool(ASTSubstructure):
    name = "If/Else Assign Bool"
    technical_description = "If(..)[name=bool] Else[name=!bool]"
    subsets = [IfElseAssignBoolReturn]

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Assign([t1], Constant(b1))],
                    orelse=[Assign([t2], Constant(b2))]
                ) if (
                        are_compliment_bools(b1, b2)
                        and dirty_compare(t1, t2)
                ):
                    match = cls._make_match(node, node)
                    if not cls.match_collides_with_subset(module, match):
                        yield match


class EmptyIfBody(ASTSubstructure):
    name = "Empty If Body"
    technical_description = "If(..)[Pass|Constant|name=name]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[Expr(Constant()) | Pass() as body]):
                    yield cls._make_match(node, body)
                case If(body=[
                    Assign(targets=[Name(id=n1)], value=Name(id=n2)) as body
                ]) if n1 == n2:
                    yield cls._make_match(node, body)


class EmptyElseBody(ASTSubstructure):
    name = "Empty Else Body"
    technical_description = "If(..)[..] Else[Pass|Constant|name=name]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(orelse=[Expr(Constant()) | Pass()]):
                    yield cls._make_match(node, node)
                case If(orelse=[
                    Assign(targets=[Name(id=n1)], value=Name(id=n2))
                ]) if n1 == n2:
                    yield cls._make_match(node, node)


class NestedIf(ASTSubstructure):
    name = "Nested If"
    technical_description = "If(..)[If(..)[..]]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[If(orelse=[]) as inner]):
                    yield cls._make_match(node, inner)


class UnnecessaryElse(ASTSubstructure):
    name = "Unnecessary Else"
    technical_description = "If(..)[*.., stmt] Else[stmt]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[*_, _, s1], orelse=[s2]) if dirty_compare(s1, s2):
                    yield cls._make_match(node, node)


class DuplicateIfElseStatement(ASTSubstructure):
    name = "Duplicate If/Else Statement"
    technical_description = "If(..)[.., stmt] Else[.., stmt]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
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
                    yield cls._make_match(node, node)


class SeveralDuplicateIfElseStatements(ASTSubstructure):
    name = "Several Duplicate If/Else Statements"
    technical_description = "If(..)[.., *stmts] Else[.., *stmts]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=b1, orelse=b2
                ) if (
                        match_ends(b1, b2) > 1
                        and not dirty_compare(b1, b2)
                ):
                    yield cls._make_match(node, node)


class DuplicateIfElseBody(ASTSubstructure):
    name = "Duplicate If/Else Body"
    technical_description = "If(..)[body] Else[body]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if dirty_compare(b1, b2):
                    yield cls._make_match(node, node)


class DeclarationAssignmentDivision(ASTSubstructure):
    name = "Declaration/Assignment Division"
    technical_description = "name: type"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        yield from (cls._make_match(assign, assign)
                    for assign in nodes_of_class(module, AnnAssign)
                    if not hasattr(assign, 'value') or assign.value is None)


class AugmentableAssignment(ASTSubstructure):
    name = "Augmentable Assignment"
    technical_description = "name = name Op() .. | .. [+*] name"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, Assign):
            match node:
                case Assign(
                    targets=[Name(id=n1)],
                    value=BinOp(left=Name(id=n2)),
                ) if n1 == n2:
                    yield cls._make_match(node, node)
                case Assign(
                    targets=[Name(id=n1)],
                    value=BinOp(
                        # ToDo - Check for other commutative ops
                        op=Add() | Mult(),
                        right=Name(id=n2)
                    )
                ) if n1 == n2:
                    yield cls._make_match(node, node)


class DuplicateExpression(ASTSubstructure):
    name = "Duplicate Expression"
    # ToDo – Clarify effenberger2022code definition. It is not clear if they
    #  are using the term expression formally or colloquially or whether they
    #  account for control flow
    technical_description = (
        "Module contains two expressions with more than 8 names, literals, "
        "or operators. Operators count for two tokens."
    )

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        # ToDo - consider using something like leoAst.py.
        #  http://leoeditor.com/appendices.html#leoast-py
        expressions = nodes_of_class(module, expr)
        expressions = [n for n in expressions if weight_of(n) >= 8]
        for i in range(len(expressions)):
            for j in range(i + 1, len(expressions)):
                if dirty_compare(expressions[i], expressions[j]):
                    yield cls._make_match(expressions[i], expressions[i])
                    yield cls._make_match(expressions[j], expressions[j])


class MissedAbsoluteValue(ASTSubstructure):
    name = 'Missed Absolute Value'
    technical_description = ('x < val and x > -val '
                             '| x == val or x == -val '
                             '| x <= val and x >= -val')

    _inequalities = (Gt, Lt), (Lt, Gt), (GtE, LtE), (LtE, GtE), (NotEq, NotEq)

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        for node in nodes_of_class(module, BoolOp):
            match node:
                case BoolOp(
                    op=op,
                    values=[
                        Compare(left=Name(id=n1), ops=[op1], comparators=[v1]),
                        Compare(left=Name(id=n2), ops=[op2], comparators=[v2]),
                    ]
                ) if (n1 == n2
                      and ((isinstance(op, And)
                            and ((type(op1), type(op2)) in cls._inequalities))
                           or (isinstance(op, Or)
                               and isinstance(op1, Eq)
                               and isinstance(op2, Eq)))
                      and are_complimentary_unary_expressions(v1, v2)):
                    yield cls._make_match(node, node)


class RepeatedAddition(ASTSubstructure):
    name = 'Repeated Addition'
    technical_description = 'name = val( * val)+'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        # ToDo - handle reordered expressions e.g. x + y + x
        # ToDo - handle numbers in expressions e.g. x + 1 + x
        visited = set()
        for node in nodes_of_class(module, BinOp):
            if node not in visited and is_repeated_add(node):
                visited.update(nodes_of_class(node, BinOp))
                yield cls._make_match(node, node)

# pylint x == 'a' or x == 'b' covered by R1714
# pylint for i in range covered by C0200 ?
# pylint x = x covered by self-assigning-variable (W0127)
