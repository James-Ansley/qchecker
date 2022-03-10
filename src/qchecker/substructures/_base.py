import abc

from qchecker.descriptions import get_description

__all__ = ['Substructure']


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
    @abc.abstractmethod
    def iter_matches(cls, code: str):
        """
        Iterates over all matching substructures in the given module

        :raises SyntaxError: If the given code cannot be parsed.
        """

    @classmethod
    def count_matches(cls, code: str) -> int:
        """Returns the number of matching substructures in the given module"""
        return len(list(cls.iter_matches(code)))

    @classmethod
    def list_matches(cls, code: str):
        return list(cls.iter_matches(code))
