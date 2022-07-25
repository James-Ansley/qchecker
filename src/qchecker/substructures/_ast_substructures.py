import abc
from ast import *
from collections.abc import Iterator, Iterable
from dataclasses import dataclass
from itertools import chain, combinations
from typing import Any

from deprecated.sphinx import deprecated
from qchecker.match import Match, TextRange
from qchecker.parser import CodeModule
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
    'DuplicateIfElseBody',
    'AugmentableAssignment',
    'DuplicateExpression',  # Deprecated
    'MissedAbsoluteValue',
    'RepeatedAddition',
    'RepeatedMultiplication',
    'RedundantArithmetic',
    'RedundantNot',
    'RedundantComparison',
    'MergeableEqual',
    'RedundantFor',
    'NoOp',
    'Tautology',
    'Contradiction',
    'WhileAsFor',
    'ForWithRedundantIndexing',
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
    # TODO - Deprecated, remove in 2.0.0
    subsets: list['ASTSubstructure'] = []

    @classmethod
    def iter_matches(cls, code: CodeModule | str) -> Iterator[Match]:
        # All problems in computer science
        # can be solved by another level of indirection.
        if isinstance(code, CodeModule):
            module = code.ast
        else:
            try:
                module = parse(code)
            except IndentationError as e:
                raise SyntaxError from e
        yield from cls._iter_matches(module)

    @classmethod
    @abc.abstractmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        """Iterates over matches found in the AST"""

    @classmethod
    @deprecated(
        "subsets can be manually filtered if needed – better to give callers "
        "control over what substructures they need",
        version="1.1.1",
    )
    def _match_collides_with_subset(cls, module, match):
        matches = chain(*(sub_struct._iter_matches(module)
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
    # TODO - Deprecated, remove in 2.0.0
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
                    if not cls._match_collides_with_subset(module, match):
                        yield match


class IfElseAssignBool(ASTSubstructure):
    name = "If/Else Assign Bool"
    technical_description = "If(..)[name=bool] Else[name=!bool]"
    # TODO - Deprecated, remove in 2.0.0
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
                    if not cls._match_collides_with_subset(module, match):
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
                    yield cls._make_match(node, inner)


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
    # ToDo – Flag as cautionary, in many cases it may be impossible to know
    #  *for certain* whether this can be flagged automatically.
    #  Depending on type, objects may not have augmented operations and so
    #  should infer type if possible and ignore cases where type cannot
    #  be inferred
    name = "Augmentable Assignment"
    technical_description = "name = name Op() .. | .. [+*] name"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, Assign):
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


@deprecated(
    "DuplicateExpression is deprecated because this has such a low "
    "threshold to be annoying and unhelpful for anything larger than "
    "a simple function. Will be removed in future versions.",
    version="0.0.0a4",
)
class DuplicateExpression(ASTSubstructure):
    # ToDo - This is a smell not a pattern
    #  – should be removed for automated feedback
    name = "Duplicate Expression"
    technical_description = (
        "Module contains two expressions with more than 8 names, literals, "
        "or operators. Operators have twice the weight of other tokens."
    )

    @classmethod
    @deprecated(
        "DuplicateExpression is deprecated because this has such a low "
        "threshold to be annoying and unhelpful for anything larger than "
        "a simple function. Will be removed in future versions.",
        version="0.0.0a4",
    )
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
        for node in nodes_of_class(module, BinOp, excluding=BinOp):
            expression = simplify_expression(node)
            if contains_duplicate_add(expression):
                yield cls._make_match(node)


class RepeatedMultiplication(ASTSubstructure):
    name = 'Repeated Multiplication'
    technical_description = 'val( * val){2,}'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, BinOp, excluding=BinOp):
            expression = simplify_expression(node)
            if contains_duplicate_mult(expression):
                yield cls._make_match(node)


class RedundantArithmetic(ASTSubstructure):
    name = 'Redundant Arithmetic'
    technical_description = '1 * x | x + 0 | x - 0 | x / 1 | +x'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, BinOp):
            match (node.left, node.op, node.right):
                case ((Constant(0), Add(), _)
                      | (_, Add(), Constant(0))
                      | (_, Sub(), Constant(0))
                      | (Constant(1), Mult(), _)
                      | (_, Mult(), Constant(1))
                      | (_, Pow(), Constant(1))
                      | (_, Div(), Constant(1))):
                    yield cls._make_match(node)
                case (Name(n1), Div(), Name(n2)) if n1 == n2:
                    yield cls._make_match(node)
        for node in nodes_of_class(module, UnaryOp):
            # ToDo - check if there are weird edge cases that make
            #  this unnecessary
            match node:
                case UnaryOp(op=UAdd()):
                    yield cls._make_match(node)


class RedundantNot(ASTSubstructure):
    # ToDo - check if there are weird edge cases that make this unnecessary
    name = 'Redundant Not'
    technical_description = 'not Compare'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, UnaryOp):
            match node:
                case UnaryOp(Not(), Compare()):
                    yield cls._make_match(node)


class RedundantComparison(ASTSubstructure):
    # ToDo - This TECHNICALLY might not count as an antipattern.
    #  Should check in the future
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
        # ToDo - Consider chains of more than two
        # ToDo - consider value == name as well
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


class RedundantFor(ASTSubstructure):
    name = 'Redundant For'
    technical_description = 'for _ in range(1|0):'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, For):
            match node:
                case For(
                    iter=Call(func=Name(id='range'), args=[Constant(v)]) as end
                ) if v in (0, 1):
                    yield cls._make_match(node, end)


class NoOp(ASTSubstructure):
    name = 'No Op'
    technical_description = 'name = name | name (+|-)= 0 | name (*|/|**)= 1'
    # TODO - Deprecated, remove in 2.0.0
    subsets = [EmptyIfBody, EmptyElseBody]

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, (Assign, AnnAssign)):
            if is_nop(node):
                match = cls._make_match(node, node)
                if not cls._match_collides_with_subset(module, match):
                    yield match
        for node in nodes_of_class(module, AugAssign):
            match (node.op, node.value):
                case ((Add(), Constant(0))
                      | (Sub(), Constant(0))
                      | (Mult(), Constant(1))
                      | (Div(), Constant(1))
                      | (Pow(), Constant(1))):
                    match = cls._make_match(node, node)
                    if not cls._match_collides_with_subset(module, match):
                        yield match


class Tautology(ASTSubstructure):
    name = 'Tautology'
    technical_description = 'A statement that is always True ' \
                            '(excluding the True constant)'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, (BoolOp, Compare)):
            match node:
                case BoolOp(
                    op=Or(), values=[left, right]
                ) if compliments(left, right):
                    yield cls._make_match(node, node)
                case BoolOp(
                    op=Or(), values=values
                ) if any(
                    isinstance(v, Constant) and v.value is True for v in values
                ):
                    yield cls._make_match(node, node)
                case Compare(
                    left=Name(id=n1) | Constant(value=n1),
                    ops=[Eq()] | [Is()],
                    comparators=[Name(id=n2) | Constant(value=n2)],
                ) if n1 == n2:
                    yield cls._make_match(node, node)


class Contradiction(ASTSubstructure):
    name = 'Contradiction'
    technical_description = 'A statement that is always False ' \
                            '(excluding the False constant)'

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, (BoolOp, Compare)):
            match node:
                case BoolOp(
                    op=And(), values=[left, right]
                ) if compliments(left, right):
                    yield cls._make_match(node, node)
                case BoolOp(
                    op=And(), values=values
                ) if any(
                    isinstance(v, Constant) and v.value is False for v in values
                ):
                    yield cls._make_match(node, node)
                case Compare(
                    left=Name(id=n1) | Constant(value=n1),
                    ops=[NotEq()] | [IsNot()],
                    comparators=[Name(id=n2) | Constant(value=n2)],
                ) if n1 == n2:
                    yield cls._make_match(node, node)


class WhileAsFor(ASTSubstructure):
    # Notes: does not consider names within calls.
    # ToDo - Does not consider mutable types – might lead to weird behaviour
    name = 'While as For'
    technical_description = "while(compare(...)):... " \
                            "- where exactly one variable from the compare " \
                            "is updated in the body, and it is updated by " \
                            "a constant amount"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, While):
            match node:
                case While(
                    test=Compare() as cmp,
                    body=body,
                ):
                    test_name_ids = {
                        n.id for n in nodes_of_class(cmp, Name, excluding=Call)
                    }
                    ctx_store = {
                        n.id for n in nodes_of_class(body, Name)
                        if isinstance(n.ctx, Store)
                    }
                    updated_by_constant = set(names_updated_by_constant(body))
                    if (
                            len(test_name_ids & ctx_store) == 1
                            and len(test_name_ids & updated_by_constant) == 1
                            and len(ctx_store & updated_by_constant) == 1
                    ):
                        yield cls._make_match(node)


class ForWithRedundantIndexing(ASTSubstructure):
    # assumes range and len are not bound to other values during runtime
    name = 'For With Redundant Indexing'
    technical_description = "for target in range(len(seq)): WHERE " \
                            "the only occurrences of target are: " \
                            "seq[target] AND seq, target, and seq[target] " \
                            "are not updated in the loop body"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        for node in nodes_of_class(module, For):
            match node:
                case For(
                    target=Name(id=target),
                    iter=Call(
                        func=Name(id='range'),
                        args=[Call(func=Name(id='len'), args=[Name(id=seq)])]
                    ),
                    body=body,
                ) if all_ctx_are_load(all_names_of(body, seq, target)):
                    subscripts = [*subscripts_of(body, seq, target)]
                    targets = [*all_names_of(body, target)]

                    all_subs_load = all_ctx_are_load(subscripts)
                    target_only_in_subs = len(subscripts) == len(targets)
                    if all_subs_load and target_only_in_subs:
                        yield cls._make_match(node)


def nodes_of_class(
        node: AST | Iterable[AST],
        cls: type | tuple[type, ...],
        *,
        excluding: type | tuple[type, ...] = tuple(),
) -> Iterable:
    """
    Yields nodes in the AST walk of the given cls type. Order is not guaranteed.
    Does not include nodes that are the children of nodes of type excluding.
    """
    if isinstance(node, Iterable):
        yield from chain.from_iterable(
            nodes_of_class(n, cls, excluding=excluding) for n in node
        )
        return
    if isinstance(node, cls):
        yield node
    if not isinstance(node, excluding):
        for child in iter_child_nodes(node):
            yield from nodes_of_class(child, cls, excluding=excluding)


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
        # pylint x = x covered by self-assigning-variable (W0127)
        case Assign([Name(n1)], Name(n2)) if n1 == n2:
            return True
        case AnnAssign(target=Name(id=n1), value=Name(id=n2)) if n1 == n2:
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


def names_updated_by_constant(body):
    # ToDo - check for cases where the right side of the assign contains
    #  names that don't change in the loop body.
    assigns = [n for line in body
               for n in nodes_of_class(line, (Assign, AugAssign))]
    for assign in assigns:
        match assign:
            case Assign(
                targets=targets,
                value=val
            ):
                match val:
                    case BinOp(
                        left=Name(id=n), op=Add() | Sub(), right=Constant()
                    ) if n == targets[0].id:
                        yield n
                    case BinOp(
                        left=Constant(), op=Add() | Sub(), right=Name(id=n)
                    ) if n == targets[0].id:
                        yield n
            case AugAssign(
                target=Name(id=n),
                op=Add() | Sub(),
                value=Constant(),
            ):
                yield n


@dataclass(frozen=True)
class FlatOp:
    op: Any
    values: tuple

    def __str__(self):
        return f"{self.op.__name__}({', '.join(map(str, self.values))})"


def simplify_expression(root: BinOp | expr):
    if isinstance(root, Name):
        return root.id
    if not isinstance(root, BinOp):
        return root
    left = simplify_expression(root.left)
    right = simplify_expression(root.right)
    match root.op:
        case Add():
            values = hoist(Add, left) + hoist(Add, right)
            return FlatOp(Add, values)
        case Mult():
            values = hoist(Mult, left) + hoist(Mult, right)
            return FlatOp(Mult, values)
        case _:
            return FlatOp(type(root.op), (left, right))


def hoist(op, operands):
    if isinstance(operands, FlatOp) and operands.op is op:
        return operands.values
    else:
        return operands,


def contains_duplicate_add(root):
    if not isinstance(root, FlatOp):
        return False
    if root.op is Add and len(root.values) != len(set(root.values)):
        return True
    return any(contains_duplicate_add(n) for n in root.values)


def contains_duplicate_mult(root):
    if not isinstance(root, FlatOp):
        return False
    if root.op is Mult and len(root.values) - 1 > len(set(root.values)):
        return True
    return any(contains_duplicate_mult(n) for n in root.values)


def subscripts_of(body, value_id, slice_id):
    for node in nodes_of_class(body, Subscript):
        match node:
            case Subscript(
                value=Name(id=v),
                slice=Name(id=s),
            ) if v == value_id and s == slice_id:
                yield node


def all_ctx_are_load(nodes: Iterable[Name | Subscript]):
    return all(isinstance(n.ctx, Load) for n in nodes)


def all_names_of(node: AST | Iterable[AST], *name_ids: str):
    yield from (n for n in nodes_of_class(node, Name) if n.id in name_ids)
