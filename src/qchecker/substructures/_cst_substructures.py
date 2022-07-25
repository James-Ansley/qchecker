import abc
import ast
from collections.abc import Iterable, Iterator

from libcst import *
from libcst.metadata import PositionProvider, MetadataWrapper

import qchecker.match
from qchecker.match import TextRange
from qchecker.parser import CodeModule
from qchecker.substructures._base import Substructure

__all__ = [
    'ConfusingElse',
    'ElseIf',
    'DuplicateIfElseStatement',
    'SeveralDuplicateIfElseStatements',
]


class CSTSubstructure(Substructure, abc.ABC):
    @classmethod
    def iter_matches(cls, code: CodeModule | str) -> Iterable[Match]:
        # All problems in computer science
        # can be solved by another level of indirection.
        if isinstance(code, CodeModule):
            module = code.cst
        else:
            module = MetadataWrapper(parse_module(code))
        yield from cls._iter_matches(module)

    @classmethod
    @abc.abstractmethod
    def _iter_matches(cls, module: MetadataWrapper) -> Iterable[Match]:
        """Iterates over matches found in the CST"""

    @classmethod
    def _make_match(cls, from_pos, to_pos):
        return qchecker.match.Match(
            cls.name,
            cls.description,
            TextRange(
                from_pos.start.line,
                from_pos.start.column,
                to_pos.end.line,
                to_pos.end.column,
            ),
        )


class ConfusingElse(CSTSubstructure):
    name = "Confusing Else"
    technical_description = "If(..)[..] Else[If(..)[..] Else[..]]"

    class _Visitor(CSTVisitor):
        METADATA_DEPENDENCIES = (PositionProvider,)

        def __init__(self):
            super().__init__()
            self.match_positions = []

        def visit_If(self, node: If) -> bool | None:
            match node:
                case If(
                    orelse=Else(
                        body=IndentedBlock(body=[
                            If(orelse=Else()) as inner
                        ])
                    )
                ):
                    pos = self.get_metadata(PositionProvider, inner)
                    self.match_positions.append((pos, pos))
            return True

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        v = cls._Visitor()
        module.visit(v)
        yield from (cls._make_match(from_pos, to_pos)
                    for from_pos, to_pos in v.match_positions)


class ElseIf(CSTSubstructure):
    name = 'Else If'
    technical_description = 'IF(..)[] Else[If()]'

    class _Visitor(CSTVisitor):
        METADATA_DEPENDENCIES = (PositionProvider,)

        def __init__(self):
            super().__init__()
            self.match_positions = []

        def visit_If(self, node: If) -> bool | None:
            match node:
                case If(
                    orelse=Else(
                        body=IndentedBlock(body=[
                            If(test=inner, orelse=None)
                        ])
                    ) as orelse
                ):
                    from_pos = self.get_metadata(PositionProvider, orelse)
                    to_pos = self.get_metadata(PositionProvider, inner)
                    self.match_positions.append((from_pos, to_pos))
            return True

    @classmethod
    def _iter_matches(cls, module: MetadataWrapper) -> Iterable[Match]:
        # ToDo - Adjust end lineno and col offset
        v = cls._Visitor()
        module.visit(v)
        yield from (cls._make_match(from_pos, to_pos)
                    for from_pos, to_pos in v.match_positions)


class DuplicateIfElseStatement(CSTSubstructure):
    name = "Duplicate If/Else Statement"
    technical_description = "If(..)[.., stmt] Else[.., stmt]"

    class _Visitor(CSTVisitor):
        METADATA_DEPENDENCIES = (PositionProvider,)

        def __init__(self):
            super().__init__()
            self.parents = []
            self.match_positions = []

        def visit_If(self, node: If) -> bool | None:
            match node:
                case If(
                    body=IndentedBlock(body=b1),
                    orelse=Else(body=IndentedBlock(body=b2))
                ) if (
                        (not self.parents
                         or self.parents[-1].orelse is not node)
                        and len(b2) > 1 and len(b1) > 1
                        and match_ends(b1, b2) == 1
                        and not equals(b1, b2)
                ):
                    pos = self.get_metadata(PositionProvider, node)
                    self.match_positions.append((pos, pos))
            self.parents.append(node)
            return True

        def leave_If(self, node: If):
            self.parents.pop()

    @classmethod
    def _iter_matches(cls, module: MetadataWrapper) -> Iterator[Match]:
        v = cls._Visitor()
        module.visit(v)
        yield from (cls._make_match(from_pos, to_pos)
                    for from_pos, to_pos in v.match_positions)


class SeveralDuplicateIfElseStatements(CSTSubstructure):
    name = "Several Duplicate If/Else Statements"
    technical_description = "If(..)[.., *stmts] Else[.., *stmts]"

    class _Visitor(CSTVisitor):
        METADATA_DEPENDENCIES = (PositionProvider,)

        def __init__(self):
            super().__init__()
            self.parents = []
            self.match_positions = []

        def visit_If(self, node: If) -> bool | None:
            match node:
                case If(
                    body=IndentedBlock(body=b1),
                    orelse=Else(body=IndentedBlock(body=b2))
                ) if (
                        (not self.parents
                         or self.parents[-1].orelse is not node)
                        and len(b2) > 1 and len(b1) > 1
                        and match_ends(b1, b2) > 1
                        and not equals(b1, b2)
                ):
                    pos = self.get_metadata(PositionProvider, node)
                    self.match_positions.append((pos, pos))
            self.parents.append(node)
            return True

        def leave_If(self, node: If):
            self.parents.pop()

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterator[Match]:
        v = cls._Visitor()
        module.visit(v)
        yield from (
            cls._make_match(from_pos, to_pos)
            for from_pos, to_pos in v.match_positions
        )


def _dump(nodes: CSTNode | Iterable[CSTNode]):
    # ToDo - There has to be a better way of doing this
    if isinstance(nodes, CSTNode):
        nodes = [nodes]
    # Parse as AST to remove irrelevant whitespace information
    code = [Module([]).code_for_node(n) for n in nodes]
    ast_nodes = [ast.parse(c) for c in code]
    return [ast.dump(n) for n in ast_nodes]


def equals(node1: CSTNode | Iterable[CSTNode],
           node2: CSTNode | Iterable[CSTNode]):
    return _dump(node1) == _dump(node2)


def match_ends(nodes1: list[CSTNode], nodes2: list[CSTNode]):
    for i, (elt1, el2) in enumerate(zip(reversed(nodes1), reversed(nodes2))):
        if not equals(elt1, el2):
            return i
    return min(len(nodes1), len(nodes2))
