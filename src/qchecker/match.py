import textwrap
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from qchecker.descriptions import Description

__all__ = ['TextRange', 'Match', 'aggregate_match_types']


class TextRange:
    """
    Defines a range of text.
    Lines are one-indexed and columns are zero-indexed.

    Defines the following instance variables:
     - **from_line**: one-indexed start line (inclusive)
     - **from_offset**: zero-indexed start column (inclusive)
     - **to_line**: one-indexed end line (inclusive)
     - **to_offset**: zero-indexed end column (exclusive)
    """

    __slots__ = ['from_line', 'from_offset', 'to_line', 'to_offset']

    def __init__(
            self,
            from_line: int,
            from_offset: int,
            to_line: int = None,
            to_offset: int = None):
        self.from_line = from_line
        self.from_offset = from_offset
        self.to_line = to_line if to_line is not None else from_line
        self.to_offset = to_offset if to_offset is not None else -1

    def contains(self, other: 'TextRange'):
        """
        Returns True if the range of `other` is entirely contained within self.
        """
        this_from = (self.from_line, self.from_offset)
        other_from = (other.from_line, other.from_offset)
        this_to = (self.to_line, self.to_offset)
        other_to = (other.to_line, other.to_offset)
        return this_from <= other_from and this_to >= other_to

    def grab_range(self, code: str):
        """Copies the dedented range of text from the given code string."""
        lines = code.splitlines()
        code_range = lines[self.from_line - 1:self.to_line]
        code_range[-1] = code_range[-1][:self.to_offset]
        if not code_range[0][:self.from_offset].isspace():
            code_range[0] = code_range[0][self.from_offset:]
        return textwrap.dedent('\n'.join(code_range))

    def __repr__(self):
        return f"TextRange({self.from_line},{self.from_offset}" \
               f"->{self.to_line},{self.to_offset})"

    def __eq__(self, other):
        return (
                isinstance(other, TextRange)
                and all(getattr(self, name) == getattr(other, name)
                        for name in self.__slots__)
        )


@dataclass(frozen=True, slots=True)
class Match:
    """
    Describes a matched substructure in a given piece of code.

    Defines the following instance variables:
    - **id**: The name of the type of match
    - **description**: A description of the match
    - **text_range**: A TextRange describing where the match occurs
    """
    id: str
    description: Description
    text_range: 'TextRange'

    def __str__(self):
        return (f'Match("{self.id}", '
                f'"{textwrap.shorten(self.description.content, 40)}", '
                f'{self.text_range})')

    def __repr__(self):
        return (f'Match("{self.id}", '
                f'{repr(self.description)}, '
                f'{self.text_range}')


def aggregate_match_types(matches: Iterable['Match']) -> Counter[str]:
    """Returns a Counter of the given match IDs"""
    return Counter(match.id for match in matches)
