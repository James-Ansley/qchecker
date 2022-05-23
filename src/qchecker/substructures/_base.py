import abc
from collections.abc import Iterator

from qchecker.descriptions import get_description

__all__ = ['Substructure']

from qchecker.match import Match


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
    def iter_matches(cls, code: str) -> Iterator[Match]:
        """
        Iterates over all matching substructures in the given module.
        Is not guaranteed to lazily search for matches but often will.

        :raises SyntaxError: If the given code cannot be parsed.
        """

    @classmethod
    def count_matches(cls, code: str) -> int:
        """
        Returns the number of matching substructures in the given module

        :raises SyntaxError: If the given code cannot be parsed.
        """
        return len(list(cls.iter_matches(code)))

    @classmethod
    def list_matches(cls, code: str) -> list[Match]:
        """
        Returns a list of all matching substructures in the given module

        :raises SyntaxError: If the given code cannot be parsed.
        """
        return list(cls.iter_matches(code))

    @classmethod
    def is_present(cls, code: str) -> bool:
        """
        Convenience method to check if a particular substructure is present in
        the given code. This will often be more efficient than checking if
        the count_matches function is greater than 0.

        :raises SyntaxError: If the given code cannot be parsed.
        """
        return next(cls.iter_matches(code), None) is not None
