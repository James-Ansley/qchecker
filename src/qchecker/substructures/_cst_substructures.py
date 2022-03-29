import abc
from collections.abc import Iterable

import qchecker.match
from libcst import *
from libcst.metadata import PositionProvider
from qchecker.match import Match, TextRange
from qchecker.substructures._base import Substructure

__all__ = [
    'ConfusingElse',
    'ElseIf',
]


class CSTSubstructure(Substructure, abc.ABC):
    @classmethod
    def iter_matches(cls, code: str) -> Iterable[Match]:
        # All problems in computer science
        # can be solved by another level of indirection.
        module = MetadataWrapper(parse_module(code))
        yield from cls._iter_matches(module)

    @classmethod
    @abc.abstractmethod
    def _iter_matches(cls, module: MetadataWrapper) -> Iterable[Match]:
        """Iterates over matches found in the AST"""

    @classmethod
    def _make_match(cls, from_node, to_node, node_position_map):
        from_ = node_position_map[from_node]
        to_ = node_position_map[to_node]
        return qchecker.match.Match(
            cls.name,
            cls.description,
            TextRange(
                from_.start.line,
                from_.start.column,
                to_.end.line,
                to_.end.column,
            ),
        )


class _Visitor(CSTVisitor):
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self, cls):
        super().__init__()
        self._cls = cls
        self.nodes = []
        self.node_position_map = {}

    def on_visit(self, node: "CSTNode") -> bool:
        pos = self.get_metadata(PositionProvider, node)
        self.node_position_map[node] = pos
        if isinstance(node, self._cls):
            self.nodes.append(node)
        return True


def visit(node, cls):
    visitor = _Visitor(cls)
    node.visit(visitor)
    return visitor.nodes, visitor.node_position_map


class ConfusingElse(CSTSubstructure):
    name = "Confusing Else"
    technical_description = "If(..)[..] Else[If(..)[..] Else[..]]"

    @classmethod
    def _iter_matches(cls, module: Module) -> Iterable[Match]:
        nodes, node_position_map = visit(module, If)
        for node in nodes:
            match node:
                case If(
                    orelse=Else(
                        body=IndentedBlock(body=[
                            If(orelse=Else()) as inner
                        ])
                    )
                ):
                    yield cls._make_match(inner, inner, node_position_map)


class ElseIf(CSTSubstructure):
    name = 'Else If'
    technical_description = 'IF(..)[] Else[If()]'

    @classmethod
    def _iter_matches(cls, module: MetadataWrapper) -> Iterable[Match]:
        # ToDo - Adjust end lineno and col offset
        nodes, node_position_map = visit(module, If)
        for node in nodes:
            match node:
                case If(
                    orelse=Else(
                        body=IndentedBlock(body=[
                            If(test=inner)
                        ])
                    ) as orelse
                ):
                    yield cls._make_match(orelse, inner, node_position_map)
