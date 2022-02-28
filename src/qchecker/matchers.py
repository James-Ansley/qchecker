import textwrap
from ast import *

from ._substructures import Substructure, TextRange
from .utils import *


class UnnecessaryElif(Substructure):
    name = "Unnecessary Elif"
    technical_description = "If(cond)[..] Elif(!cond)[..]"
    description = textwrap.dedent("""
    Looks like you have an unnecessary Elif condition.
    It might be better in this case to just use an Else.
    For example, instead of:
    ```python
    if x < 5:
        # do something
    elif x >= 5:
        # do something else
    ```
    Consider doing this:
    ```python
    if x < 5:
        # do something
    else:
        # do something else
    ```
    
    Or, instead of:
    ```python
    if current is None:
        current = Node()
    elif current is not None:
        current = current.next
    ```
    Consider doing this:
    ```python
    if current is None:
        current = Node()
    else:
        current = current.next
    ```
    """)

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(test=t1, orelse=[If(test=t2)]) if is_compliment(t1, t2):
                    yield TextRange(node, node)


class IfElseReturnBool(Substructure):
    name = "If/Else Return Bool"
    technical_description = "If(..)[Return bool] Else[Return !bool]"
    description = textwrap.dedent("""
    Looks like you are returning two booleans inside of an If/Else statement.
    It might be better if you just return the If condition or its inverse.
    For example, instead of:
    ```python
    if x < 5:
        return True
    else:
        return False
    ```
    Consider doing this:
    ```python
    return x < 5
    ```
    
    Or, instead of:
    ```python
    if x % 2 == 0:
        return False
    else:
        Return True
    ```
    Consider doing this:
    ```python
    return x % 2 == 1
    ```
    """)

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Return(Constant(r1))],
                    orelse=[Return(Constant(r2))]
                ) if compliment_bools(r1, r2):
                    yield TextRange(node, node)


class IfReturnBool(Substructure):
    name = "If Return Bool"
    technical_description = "If(..)[Return bool], Return !bool"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, FunctionDef):
            match node:
                case FunctionDef(
                    body=[
                        *_,
                        If(body=[Return(Constant(v1))]) as n1,
                        Return(Constant(v2)) as n2,
                    ]
                ) if compliment_bools(v1, v2):
                    yield TextRange(n1, n2)


class IfElseAssignReturn(Substructure):
    name = "If/Else Assign Return"
    technical_description = "If(..)[name=..] Else[name=..], Return name"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[TextRange]:
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
                    yield TextRange(n1, n2)


class IfElseAssignBoolReturn(Substructure):
    name = "If/Else Assign Bool Return"
    technical_description = "If(..)[name=bool] Else[name=!bool], Return name"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[TextRange]:
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
                        and dirty_cmp(t1, t2)
                        and t1.id == t3
                ):
                    yield TextRange(n1, n2)


class IfElseAssignBool(Substructure):
    name = "If/Else Assign Bool"
    technical_description = "If(..)[name=bool] Else[name=!bool]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[Assign([t1], Constant(b1))],
                    orelse=[Assign([t2], Constant(b2))]
                ) if (
                        compliment_bools(b1, b2)
                        and dirty_cmp(t1, t2)
                ):
                    yield TextRange(node, node)


class EmptyIfBody(Substructure):
    name = "Empty If Body"
    technical_description = "If(..)[Pass|Constant|name=name]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                # ToDo - Check name=name
                case If(body=[Expr(Constant()) | Pass()]):
                    yield TextRange(node, node)


class EmptyElseBody(Substructure):
    name = "Empty Else Body"
    technical_description = "If(..)[..] Else[Pass|Constant|name=name]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                # ToDo - Check name=name
                case If(orelse=[Expr(Constant()) | Pass()]):
                    yield node, node


class NestedIf(Substructure):
    name = "Nested If"
    technical_description = "If(..)[If(..)[..]]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[If()]):
                    yield TextRange(node, node)


class ConfusingElse(Substructure):
    name = "Confusing Else"
    technical_description = "If(..)[..] Else[If(..)[..] Else[..]]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(orelse=[If(orelse=orselse) as inner]) if len(orselse):
                    yield TextRange(inner, inner)


class UnnecessaryElse(Substructure):
    name = "Unnecessary Else"
    technical_description = "If(..)[*.., stmt] Else[stmt]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=[*_, _, s1], orelse=[s2]) if dirty_cmp(s1, s2):
                    yield TextRange(node, node)


class DuplicateIfElseStatement(Substructure):
    name = "Duplicate If/Else Statement"
    technical_description = "If(..)[.., stmt] Else[.., stmt]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(
                    body=[*_, _, s1],
                    orelse=[*_, _, s2]
                ) if dirty_cmp(s1, s2):
                    yield node, node


class SeveralDuplicateIfElseStatements(Substructure):
    name = "Several Duplicate If/Else Statements"
    technical_description = "If(..)[.., *stmts] Else[.., *stmts]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if match_ends(b1, b2) > 1:
                    yield TextRange(node, node)


class DuplicateIfElseBody(Substructure):
    name = "Duplicate If/Else Body"
    technical_description = "If(..)[body] Else[body]"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, If):
            match node:
                case If(body=b1, orelse=b2) if dirty_cmp(b1, b2):
                    yield TextRange(node, node)


class DeclarationAssignmentDivision(Substructure):
    name = "Declaration/Assignment Division"
    technical_description = "name: type, name=.."
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        # ToDo - Make this better
        declared_names = set()
        for ann_assign in nodes_of_class(module, AnnAssign):
            if ann_assign.simple == 1 and isinstance(ann_assign.target, Name):
                declared_names.add(ann_assign.target.id)
        for name in nodes_of_class(module, Name):
            if name.id in declared_names and isinstance(name.ctx, Store):
                yield TextRange(name, name)


class NoOpAssign(Substructure):
    name = "No-op Assign"
    technical_description = "name=name"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        for node in nodes_of_class(module, Assign):
            match node:
                case Assign(
                    targets=[Name() as n1],
                    value=Name() as n2
                ) if n1.id == n2.id:
                    yield TextRange(n1, n2)


class UnusedVariable(Substructure):
    name = "Unused Variable"
    technical_description = "A name is assigned but never used"
    description = textwrap.dedent("""""")  # ToDo - Add Description

    @classmethod
    def iter_matches(cls, module: ast.Module) -> Iterable[TextRange]:
        # ToDo - Make this better
        loads = set()
        stores = {}
        for node in nodes_of_class(module, Name):
            if isinstance(node.ctx, Load):
                loads.add(node.id)
            if isinstance(node.ctx, Store):
                stores[node.id] = node
        for name in loads:
            if name in stores:
                stores.pop(name)
        yield from zip(stores.values(), stores.values())


# ToDo – One of these days the API will be stable! I'm sure of it
__all__ = [
    cls.__name__ for cls in Substructure.__subclasses__()
]
