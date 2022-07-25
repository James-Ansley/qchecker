"""
Defines several `Substructure` classes that each detect a
micro-antipattern.

This module also includes two constants:
    - :code:`SUBSTRUCTURES` which is a tuple of all concrete
      :class:`Substructure` classes

    - :code:`ALL_SUBSTRUCTURES` which also includes deprecated
      :class:`Substructure` classes

These tuples cannot be guaranteed to be stable between versions and should not
be relied on.

A subsets class attribute identifies subset substructures whose matches are
subsets of other substructures. This attribute has been deprecated since
version 1.1.1
"""

from inspect import isabstract as _isabstract

from ._base import Substructure
from ._ast_substructures import *
from ._cst_substructures import *

# Experience shows these substructures are 'annoying' and should not be
# lumped in with all the other substructures. These will likely be removed in
# future versions.
_unnecessary_substructures = [
    # Removed because this has such a low threshold to be annoying and unhelpful
    # for anything larger than a simple function. Has been marked as deprecated
    DuplicateExpression,
]


def _get_concrete_substructures():
    q = [Substructure]
    while q:
        current = q.pop()
        if not _isabstract(current):
            yield current
        q.extend(current.__subclasses__())


ALL_SUBSTRUCTURES = tuple(_get_concrete_substructures())

SUBSTRUCTURES = tuple(s for s in ALL_SUBSTRUCTURES
                      if s not in _unnecessary_substructures)
