import abc
from collections.abc import Iterator

from qchecker.descriptions import get_description

__all__ = ['Substructure']

from qchecker.match import Match
from qchecker.parser import CodeModule


class Substructure(abc.ABC):
    """
    Generic Substructure base class.

    Each substructure allows you to iterate, list, count, or check for the
    existence of a particular micro-antipattern in a code string.
    """

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
        """
        A student-readable description of the error as defined by the
        descriptions module
        """
        return get_description(cls.__name__)

    @classmethod
    @abc.abstractmethod
    def iter_matches(cls, code: CodeModule | str) -> Iterator[Match]:
        """
        Iterates over all matching substructures in the given module.
        Is not guaranteed to lazily search for matches but often will.

        :param code:
            The code to be parsed.

            .. deprecated:: 1.1.0
                String parameters will not be supported in future versions.
                Wrap the code into a CodeModule instead.

        :raises SyntaxError: If the given code cannot be parsed.
        """

    @classmethod
    def count_matches(cls, code: CodeModule | str) -> int:
        """
        Returns the number of matching substructures in the given module

        :param code:
            The code to be parsed.

            .. deprecated:: 1.1.0
                String parameters will not be supported in future versions.
                Wrap the code into a CodeModule instead.

        :raises SyntaxError: If the given code cannot be parsed.
        """
        return len(list(cls.iter_matches(code)))

    @classmethod
    def list_matches(cls, code: CodeModule | str) -> list[Match]:
        """
        Returns a list of all matching substructures in the given module

        :param code:
            The code to be parsed.

            .. deprecated:: 1.1.0
                String parameters will not be supported in future versions.
                Wrap the code into a CodeModule instead.

        :raises SyntaxError: If the given code cannot be parsed.
        """
        return list(cls.iter_matches(code))

    @classmethod
    def is_present(cls, code: CodeModule | str) -> bool:
        """
        Convenience method to check if a particular substructure is present in
        the given code. This will often be more efficient than checking if
        the count_matches function is greater than 0.

        :param code:
            The code to be parsed.

            .. deprecated:: 1.1.0
                String parameters will not be supported in future versions.
                Wrap the code into a CodeModule instead.

        :raises SyntaxError: If the given code cannot be parsed.
        """
        return next(cls.iter_matches(code), None) is not None
