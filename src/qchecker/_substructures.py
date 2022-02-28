import abc as _abc
import ast as _ast
from collections.abc import Iterable


class TextRange:
    def __init__(self, node1, node2):
        self.from_line = node1.lineno
        self.from_offset = node1.col_offset
        self.to_line = node2.end_lineno
        self.to_offset = node2.end_col_offset

    def __repr__(self):
        return f"TextRange({self.from_line},{self.from_offset}" \
               f"->{self.to_line},{self.to_offset})"


class Substructure(_abc.ABC):
    name: str = NotImplemented
    technical_description: str = NotImplemented
    description: str = NotImplemented

    def __init_subclass__(cls, **kwargs):
        attrs = [a for a in Substructure.__dict__ if not a.startswith('_')]
        for attr in attrs:
            if getattr(cls, attr) is NotImplemented:
                raise NotImplementedError(
                    f"\"{cls.__name__}\" does not implement "
                    f"the required class attribute \"{attr}\""
                )

    @classmethod
    @_abc.abstractmethod
    def iter_matches(cls, module: _ast.Module) -> Iterable[TextRange]:
        """Iterates over all matching substructures in the given module"""
