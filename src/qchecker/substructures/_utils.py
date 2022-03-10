import ast
import re
from collections.abc import Iterable

__all__ = [
    'nodes_of_class',
    'dirty_compare',
    'match_ends',
    'are_compliment_operations',
    'are_compliment_operators',
    'are_compliment_bools',
    'weight_of',
    'are_complimentary_unary_expressions',
    'is_repeated_add',
]

_COMPLIMENT_OPS = {
    ast.Eq: ast.NotEq,
    ast.Lt: ast.GtE,
    ast.LtE: ast.Gt,
    ast.Is: ast.IsNot,
    ast.In: ast.NotIn,
}
_COMPLIMENT_OPS |= {v: k for k, v in _COMPLIMENT_OPS.items()}

_DOUBLE_WEIGHTED_NODES = (
    ast.operator,
    ast.boolop,
    ast.unaryop,
    ast.cmpop,
)
_SINGLE_WEIGHTED_NODES = (
    ast.Name,
    ast.Constant,
)


def nodes_of_class(node: ast.AST, cls: type | tuple[type, ...]) -> Iterable:
    """
    Yields nodes in the AST walk of the given cls type. Order is not guaranteed.
    """
    for child in ast.walk(node):
        if isinstance(child, cls):
            yield child


def dirty_compare(n1: ast.AST | Iterable[ast.AST],
                  n2: ast.AST | Iterable[ast.AST]):
    """
    Performs dirty equivalence check between two nodes or iterables of nodes.
    Two nodes are considered equivalent if their dumps are equal.
    """
    if isinstance(n1, Iterable) and isinstance(n2, Iterable):
        n1, n2 = list(n1), list(n2)
        return (
                len(n1) == len(n2)
                and all(dirty_compare(n1, n2)
                        for n1, n2 in zip(n1, n2))
        )
    return (
            isinstance(n1, ast.AST)
            and isinstance(n2, ast.AST)
            and ast.dump(n1) == ast.dump(n2)
    )


def match_ends(nodes1: list[ast.AST], nodes2: list[ast.AST]):
    """
    Returns the number of consecutive equivalent nodes at the end of both
    node lists.
    """
    matching = 0
    for n1, n2 in zip(reversed(nodes1), reversed(nodes2)):
        if dirty_compare(n1, n2):
            matching += 1
        else:
            break
    return matching


def are_compliment_operators(n1, n2):
    return type(n1) == _COMPLIMENT_OPS[type(n2)]


def are_compliment_binary_expressions(n1: ast.Compare, n2: ast.Compare):
    """Matches `x < 5` compliments `x >= 5 `"""
    match (n1, n2):
        case (
            ast.Compare(left=l1, comparators=c1, ops=[o1]),
            ast.Compare(left=l2, comparators=c2, ops=[o2]),
        ) if (
                dirty_compare(l1, l2)
                and dirty_compare(c1, c2)
                and are_compliment_operators(o1, o2)
        ):
            return True
    return False


def are_complimentary_unary_expressions(n1, n2):
    """matches `x` compliments `not x`"""
    match (n1, n2):
        case (
            cond1,
            ast.UnaryOp(op=ast.Not() | ast.USub(), operand=cond2),
        ) if dirty_compare(cond1, cond2):
            return True
        case (
            ast.UnaryOp(op=ast.Not() | ast.USub(), operand=cond1),
            cond2,
        ) if dirty_compare(cond1, cond2):
            return True
    return False


def are_complimented_expression_boolean_literals(n1, n2):
    """
    matches `x < 5 == True` compliments `x < 5 == False`
    """
    match (n1, n2):
        case (
            ast.Compare(left=l1,
                        comparators=[*r1, ast.Constant(value=v1)],
                        ops=[*_, o1]),
            ast.Compare(left=l2,
                        comparators=[*r2, ast.Constant(value=v2)],
                        ops=[*_, o2]),
        ) if (
                dirty_compare(l1, l2)
                and dirty_compare(r1, r2)
                and are_compliment_bools(v1, v2)
                and dirty_compare(o1, o2)
        ):
            return True
    return False


def are_compliment_operations(n1, n2):
    """
    Returns True if the two nodes n1 and n2 are compliment expressions of
    each other. For example:
        - `x < 5` compliments `x >= 5`
        - `x` compliments `not x`
        - `x < 5 == True` compliments `x < 5 == False`
    """
    return (
            are_compliment_binary_expressions(n1, n2)
            or are_complimentary_unary_expressions(n1, n2)
            or are_complimented_expression_boolean_literals(n1, n2)
    )


def are_compliment_bools(v1, v2):
    """Returns true if v1 and v2 are both bools and not equal"""
    return isinstance(v1, bool) and isinstance(v2, bool) and v1 != v2


def weight_of(node):
    # ToDo – Clarify effenberger2022code definition. What do they mean by token?
    weight = 2 * len(list(nodes_of_class(node, _DOUBLE_WEIGHTED_NODES)))
    weight += len(list(nodes_of_class(node, _SINGLE_WEIGHTED_NODES)))
    return weight


def is_repeated_add(node: ast.BinOp):
    code = ast.unparse(node)
    return re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)(?: \+ \1)+', code) is not None
