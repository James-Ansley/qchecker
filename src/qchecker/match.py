import textwrap
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass


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

    def __repr__(self):
        return f"TextRange({self.from_line},{self.from_offset}" \
               f"->{self.to_line},{self.to_offset})"


@dataclass(frozen=True)
class Match:
    id: str
    description: str
    text_range: 'TextRange'

    def __str__(self):
        return (f'Match("{self.id}", '
                f'"{textwrap.shorten(self.description, 40)}", '
                f'{self.text_range})')

    def __repr__(self):
        return (f'Match("{self.id}",'
                f' """{self.description}""",'
                f' {self.text_range}')


def aggregate_match_types(matches: Iterable['Match']) -> Counter[str]:
    return Counter(match.id for match in matches)
