"""This module retrieves curated descriptions of matched patterns intended to
be shown to students.

Allows for student-readable descriptions to be automatically retrieved
from default or custom description mappings.

Internally a list of description mappings from substructure class names to
description objects is stored. The last mapping that contains a mapping from
a given class name to a description is used.
"""

__all__ = [
    'Markup',
    'Description',
    'get_description',
    'append_descriptions',
    'set_descriptions',
    'append_description_from_toml',
]


from ._descriptions import *
