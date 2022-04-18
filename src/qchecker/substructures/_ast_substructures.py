import abc
import re
from ast import *
from collections.abc import Iterator, Iterable
from itertools import chain, combinations

from qchecker.match import Match, TextRange
from qchecker.substructures._base import Substructure

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
    'AugmentableAssignment',
    'DuplicateExpression',
    'MissedAbsoluteValue',
    'RepeatedAddition',
    'RepeatedMultiplication',
    'RedundantArithmetic',
    'RedundantNot',
    'RedundantComparison',
    'MergeableEqual',
]

_DOUBLE_WEIGHTED_NODES = (
    operator,
    boolop,
    unaryop,
    cmpop,
)
_SINGLE_WEIGHTED_NODES = (
    Name,
    Constant,
)

_COMPLIMENT_OPS = {
    Eq: NotEq,
    Lt: GtE,
    LtE: Gt,
    Is: IsNot,
    In: NotIn,
}
_COMPLIMENT_OPS |= {v: k for k, v in _COMPLIMENT_OPS.items()}


class ASTSubstructure(Substructure, abc.ABC):
    @classmethod
    def iter_matches(cls, code: str) -> Iterator[Match]:
        # All problems in computer science
        # can be solved by another level of indirection.
        module = parse(code)
        yield from cls._iter_matches(module)

    @classmethod
    @abc.abstractmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        """Iterates over matches found in the AST"""

    @classmethod
    def match_collides_with_subset(cls, module, match):
        matches = chain(*(sub_struct.iter_matches(module)
                          for sub_struct in cls.subsets))
        return any(submatch.text_range.contains(match.text_range)
                   for submatch in matches)

    @classmethod
    def _make_match(cls, from_node, to_node=None):
        to_node = to_node if to_node is not None else from_node
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
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(test=t1, orelse=[If(test=t2)]) if compliments(t1, t2):
                    yield cls._make_match(node)


class IfElseReturnBool(ASTSubstructure):
    # Covered by pylint-R1703
    name = "If/Else Return Bool"
    technical_description = "If(..)[Return bool] Else[Return !bool]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Return(Constant(c1))],
                    orelse=[Return(Constant(c2))],
                ) if compliment_bools(c1, c2):
                    yield cls._make_match(node)


class IfReturnBool(ASTSubstructure):
    name = "If Return Bool"
    technical_description = "If(..)[Return bool], Return !bool"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, FunctionDef):
            match node.body:
                case [
                    *_,
                    If(body=[Return(Constant(v1))]) as start,
                    Return(Constant(v2)) as end
                ] if compliment_bools(v1, v2):
                    yield cls._make_match(start, end)


class IfElseAssignBoolReturn(ASTSubstructure):
    # Covered by pylint-R1703
    name = "If/Else Assign Bool Return"
    technical_description = "If(..)[name=bool] Else[name=!bool], Return name"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, FunctionDef):
            match node.body:
                case [
                    *_,
                    If(body=[Assign([Name(n1)], Constant(v1))],
                       orelse=[Assign([Name(n2)], Constant(v2))]) as start,
                    Return(Name(n3)) as end,
                ] if (n1 == n2 == n3 and compliment_bools(v1, v2)):
                    yield cls._make_match(start, end)


class IfElseAssignReturn(ASTSubstructure):
    # ToDo - Check if/elif*/else?
    name = "If/Else Assign Return"
    technical_description = "If(..)[name=..] Else[name=..], Return name"
    subsets = [IfElseAssignBoolReturn]

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, FunctionDef):
            match node.body:
                case [
                    *_,
                    If(
                        body=[Assign([Name(n1)])
                              | AnnAssign(Name(n1))
                              | AugAssign(Name(n1))],
                        orelse=[Assign([Name(n2)])
                                | AnnAssign(Name(n2))
                                | AugAssign(Name(n2))],
                    ) as start,
                    Return(Name(id=n3)) as end,
                ] if (n1 == n2 == n3):
                    match = cls._make_match(start, end)
                    if not cls.match_collides_with_subset(module, match):
                        yield match


class IfElseAssignBool(ASTSubstructure):
    name = "If/Else Assign Bool"
    technical_description = "If(..)[name=bool] Else[name=!bool]"
    subsets = [IfElseAssignBoolReturn]

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Assign([Name(n1)], Constant(v1))],
                    orelse=[Assign([Name(n2)], Constant(v2))],
                ) if (n1 == n2 and compliment_bools(v1, v2)):
                    match = cls._make_match(node)
                    if not cls.match_collides_with_subset(module, match):
                        yield match


class EmptyIfBody(ASTSubstructure):
    name = "Empty If Body"
    technical_description = "If(..)[Pass|Constant|name=name]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[body]) if is_nop(body):
                    yield cls._make_match(node, body)


class EmptyElseBody(ASTSubstructure):
    name = "Empty Else Body"
    technical_description = "If(..)[..] Else[Pass|Constant|name=name]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(orelse=[body]) if is_nop(body):
                    yield cls._make_match(node, body)


class NestedIf(ASTSubstructure):
    name = "Nested If"
    technical_description = "If(..)[If(..)[..]]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[If(orelse=[]) as inner]):
                    yield cls._make_match(inner)


class UnnecessaryElse(ASTSubstructure):
    # ToDo - Shouldn't the inverse of this be checked? UnnecessaryIf?
    name = "Unnecessary Else"
    technical_description = "If(..)[*.., stmts] Else[stmts]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if (
                        match_ends(b1, b2) == len(b2)
                        and len(b2) >= 1
                        and not equals(b1, b2)
                ):
                    yield cls._make_match(node)


class DuplicateIfElseStatement(ASTSubstructure):
    name = "Duplicate If/Else Statement"
    technical_description = "If(..)[.., stmt] Else[.., stmt]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if (
                        len(b2) > 1 and len(b1) > 1
                        and match_ends(b1, b2) == 1
                        and not equals(b1, b2)
                ):
                    yield cls._make_match(node)


class SeveralDuplicateIfElseStatements(ASTSubstructure):
    name = "Several Duplicate If/Else Statements"
    technical_description = "If(..)[.., *stmts] Else[.., *stmts]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if (
                        len(b2) > 1 and len(b1) > 1
                        and match_ends(b1, b2) > 1
                        and not equals(b1, b2)
                ):
                    yield cls._make_match(node)


class DuplicateIfElseBody(ASTSubstructure):
    name = "Duplicate If/Else Body"
    technical_description = "If(..)[body] Else[body]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if equals(b1, b2):
                    yield cls._make_match(node)


class AugmentableAssignment(ASTSubstructure):
    name = "Augmentable Assignment"
    technical_description = "name = name Op() .. | .. [+*] name"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, Assign):
            # ToDo – depending on type may not have augmented operations
            #   Should infer type if possible
            match node:
                case Assign(
                    targets=[Name(n1)],
                    value=BinOp(Name(n2))
                ) if n1 == n2:
                    yield cls._make_match(node)
                # ToDo – depending on type may not be commutative
                case Assign(
                    targets=[Name(n1)],
                    value=BinOp(op=Add() | Mult(), right=Name(n2))
                ) if n1 == n2:
                    yield cls._make_match(node)


class DuplicateExpression(ASTSubstructure):
    name = "Duplicate Expression"
    technical_description = (
        "Module contains two expressions with more than 8 names, literals, "
        "or operators. Operators have twice the weight of other tokens."
    )

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        # ToDo - Probably better if this just checks for a match in
        #  function definitions or is otherwise limited to local scopes
        expressions = nodes_of_class(module, expr)
        expressions = [n for n in expressions if weight(n) >= 8]
        for ex1, ex2 in combinations(expressions, 2):
            if equals(ex1, ex2):
                yield cls._make_match(ex1)
                yield cls._make_match(ex2)


class MissedAbsoluteValue(ASTSubstructure):
    name = 'Missed Absolute Value'
    technical_description = ('x < val and x > -val '
                             '| x == val or x == -val '
                             '| x <= val and x >= -val')

    _inequalities = (Gt, Lt), (Lt, Gt), (GtE, LtE), (LtE, GtE), (NotEq, NotEq)

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, BoolOp):
            match node:
                case BoolOp(
                    op=op,
                    values=[Compare(Name(n1), [op1], [v1]),
                            Compare(Name(n2), [op2], [v2])]
                ) if (n1 == n2 and negated_unary(v1, v2)):
                    if (
                            isinstance(op, Or)
                            and isinstance(op1, Eq)
                            and isinstance(op2, Eq)
                    ):
                        yield cls._make_match(node)
                    if (
                            isinstance(op, And)
                            and (type(op1), type(op2)) in cls._inequalities
                    ):
                        yield cls._make_match(node)


class RepeatedAddition(ASTSubstructure):
    name = 'Repeated Addition'
    technical_description = 'val( + val)+'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        # ToDo – Make this better
        visited = set()
        for node in nodes_of_class(module, BinOp):
            if node not in visited and is_repeated_add(node):
                visited.update(nodes_of_class(node, BinOp))
                yield cls._make_match(node)


class RepeatedMultiplication(ASTSubstructure):
    name = 'Repeated Multiplication'
    technical_description = 'val( * val){2,}'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        # ToDo – Make this better
        visited = set()
        for node in nodes_of_class(module, BinOp):
            if node not in visited and is_repeated_multiplication(node):
                visited.update(nodes_of_class(node, BinOp))
                yield cls._make_match(node)


class RedundantArithmetic(ASTSubstructure):
    name = 'Redundant Arithmetic'
    technical_description = '1 * x | x + 0 | x / 1 | +x'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, BinOp):
            match (node.left, node.op, node.right):
                case ((Constant(0), Add(), _)
                      | (_, Add(), Constant(0))
                      | (Constant(1), Mult(), _)
                      | (_, Mult(), Constant(1))
                      | (_, Div(), Constant(1))):
                    yield cls._make_match(node)
                case (Name(n1), Div(), Name(n2)) if n1 == n2:
                    yield cls._make_match(node)
        for node in nodes_of_class(module, UnaryOp):
            match node:
                case UnaryOp(op=UAdd()):
                    yield cls._make_match(node)


class RedundantNot(ASTSubstructure):
    name = 'Redundant Not'
    technical_description = 'not Compare'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, UnaryOp):
            match node:
                case UnaryOp(Not(), Compare()):
                    yield cls._make_match(node)


class RedundantComparison(ASTSubstructure):
    name = 'Redundant Comparison'
    technical_description = 'expr == bool'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, Compare):
            match node:
                case (Compare(left=Constant(val), ops=[Eq(), *_])
                      | Compare(ops=[*_, Eq()], comparators=[*_, Constant(val)])
                ) if isinstance(val, bool):
                    yield cls._make_match(node)


class MergeableEqual(ASTSubstructure):
    # covered by Pylint-R1714
    name = 'Mergeable Equal'
    technical_description = 'name == value or name == other_value'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        # ToDo – Consider chains of more than two
        for node in nodes_of_class(module, BoolOp):
            match node:
                case BoolOp(
                    op=Or(),
                    values=[
                        Compare(Name(n1), [Eq()], [_]),
                        Compare(Name(n2), [Eq()], [_])
                    ]
                ) if (n1 == n2):
                    yield cls._make_match(node)

# pylint for i in range covered by C0200 ?
# pylint x = x covered by self-assigning-variable (W0127)


def nodes_of_class(node: AST, cls: type | tuple[type, ...]) -> Iterable:
    """
    Yields nodes in the AST walk of the given cls type. Order is not guaranteed.
    """
    for child in walk(node):
        if isinstance(child, cls):
            yield child


def _dump(nodes: AST | Iterable[AST]):
    if isinstance(nodes, AST):
        nodes = [nodes]
    return "\n".join(dump(n) for n in nodes)


def equals(node1: AST | Iterable[AST],
           node2: AST | Iterable[AST]):
    return _dump(node1) == _dump(node2)


def compliments(ex1, ex2):
    return (compliment_compares(ex1, ex2)
            or compliment_unary(ex1, ex2))


def compliment_compares(cmp1: Compare, cmp2: Compare):
    match (cmp1, cmp2):
        # e.g. x < 5 compliments x >= 5
        case (
            Compare(left=l1, comparators=c1, ops=[o1]),
            Compare(left=l2, comparators=c2, ops=[o2]),
        ) if (equals(l1, l2) and equals(c1, c2) and compliment_ops(o1, o2)):
            return True
        # e.g. x < 5 == True compliments x < 5 == False
        case (
            Compare(left=l1, comparators=[*r1, Constant(value=v1)], ops=ops1),
            Compare(left=l2, comparators=[*r2, Constant(value=v2)], ops=ops2),
        ) if (equals([l1, *r1], [l2, *r2])
              and equals(ops1, ops2)
              and compliment_bools(v1, v2)):
            return True
        # e.g. x % 2 == 0 compliments x % 2 == 1
        case (
            Compare(left=BinOp(op=Mod(), right=Constant(2)) as l1,
                    ops=[Eq()],
                    comparators=[Constant(value=c1)]),
            Compare(left=BinOp(op=Mod(), right=Constant(2)) as l2,
                    ops=[Eq()],
                    comparators=[Constant(value=c2)])
        ) if (equals(l1, l2) and {c1, c2} == {0, 1}):
            return True
    return False


def compliment_ops(op1, op2):
    return type(op1) == _COMPLIMENT_OPS[type(op2)]


def compliment_unary(ex1, ex2):
    match ex1:
        case UnaryOp(op=Not(), operand=inv_ex1) if equals(ex2, inv_ex1):
            return True
    match ex2:
        case UnaryOp(op=Not(), operand=inv_ex2) if equals(ex1, inv_ex2):
            return True
    return False


def negated_unary(ex1, ex2):
    match ex1:
        case UnaryOp(op=USub(), operand=neg_ex1) if equals(neg_ex1, ex2):
            return True
    match ex2:
        case UnaryOp(op=USub(), operand=neg_ex2) if equals(ex1, neg_ex2):
            return True
    return False


def compliment_bools(v1, v2):
    """Returns true if v1 and v2 are both bools and not equal"""
    return isinstance(v1, bool) and isinstance(v2, bool) and v1 != v2


def is_nop(node):
    match node:
        case Expr(Constant() | Name()) | Pass():
            return True
        case Assign([Name(n1)], Name(n2)) if n1 == n2:
            return True
    return False


def match_ends(nodes1: list[AST], nodes2: list[AST]):
    for i, (elt1, el2) in enumerate(zip(reversed(nodes1), reversed(nodes2))):
        if not equals(elt1, el2):
            return i
    return min(len(nodes1), len(nodes2))


def weight(node):
    weight = 2 * len(list(nodes_of_class(node, _DOUBLE_WEIGHTED_NODES)))
    weight += len(list(nodes_of_class(node, _SINGLE_WEIGHTED_NODES)))
    return weight


def is_repeated_add(node: BinOp):
    code = unparse(node)
    return re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)(?: \+ \1)+', code) is not None


def is_repeated_multiplication(node: BinOp):
    code = unparse(node)
    regex = r'([a-zA-Z_][a-zA-Z0-9_]*)(?: \* \1){2,}'
    return re.search(regex, code) is not None
