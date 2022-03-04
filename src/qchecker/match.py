import textwrap
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass

from qchecker.descriptions import Description


@dataclass
class TextRange:
    from_line: int
    from_offset: int
    to_line: int = None
    to_offset: int = None

    def __post_init__(self):
        if self.to_line is None:
            self.to_line = self.from_line
        if self.to_offset is None:
            self.to_offset = self.from_offset

    def contains(self, other: 'TextRange'):
        this_from = (self.from_line, self.from_offset)
        other_from = (other.from_line, other.from_offset)
        this_to = (self.to_line, self.to_offset)
        other_to = (other.to_line, other.to_offset)
        return this_from <= other_from and this_to >= other_to

    def __repr__(self):
        return f"TextRange({self.from_line},{self.from_offset}" \
               f"->{self.to_line},{self.to_offset})"


@dataclass(frozen=True)
class Match:
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
    return Counter(match.id for match in matches)
