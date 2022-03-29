import textwrap
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import BinaryIO

import tomli

_DEFAULT_PATH = Path(__file__).parent.resolve() / 'descriptions.toml'
_DESCRIPTIONS: list[dict[str, 'Description']] = []


class Markup(Enum):
    markdown = 'markdown'
    plaintext = 'plaintext'


@dataclass
class Description:
    markup: Markup
    content: str

    def __str__(self):
        return f'Description({self.markup}, ' \
               f'"{textwrap.shorten(self.content, 40)}")'

    def __repr__(self):
        return f'Description({self.markup}, "{self.content}")'


def _set_default():
    """Loads default descriptions. Called on module initialisation"""
    with open(_DEFAULT_PATH, 'rb') as f:
        append_description_from_toml(f)


def append_descriptions(descriptions: dict[str, 'Description']) -> None:
    """
    Adds a path to a TOML file containing pattern descriptions which can then
    be retrieved from the `get_descriptions` function. Paths are searched in
    the order they are added with each new path overwriting previous
    descriptions.

    :param descriptions: A mapping from pattern names to their description
    """
    _DESCRIPTIONS.append(descriptions)


def set_descriptions(*descriptions: dict[str, 'Description']) -> None:
    """
    Sets the TOML description paths. Overwrites previously specified and
    default descriptions

    :param descriptions:  A list of mappings of pattern names to their
    descriptions
    """
    global _DESCRIPTIONS
    _DESCRIPTIONS = list(descriptions)


def append_description_from_toml(f: BinaryIO) -> None:
    """
    Loads TOML data from a  BinaryIO stream and appends to the descriptions
    list.

    :param f: the TOML BinaryIO
    """
    data = tomli.load(f)
    descriptions = {
        name: Description(Markup[values['markup']], values['content'])
        for name, values in data.items()
    }
    _DESCRIPTIONS.append(descriptions)


def get_description(description_name: str) -> Description:
    """
    Retrieves a description from the set description paths. Searches through
    each set description path in the order they have been added. Retrieves
    the last found description.

    :param description_name: The name of the description
    :return: The retrieved description

    :raises ValueError: If the description cannot be found
    """
    description = None
    for descriptions in _DESCRIPTIONS:
        current = descriptions.get(description_name)
        description = current if current is not None else description
    if description is None:
        raise ValueError(f'"{description_name}" cannot be found in '
                         f'the provided descriptions.')
    return description


_set_default()
