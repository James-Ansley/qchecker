from inspect import isabstract as _isabstract

from ._ast_substructures import *
from ._base import Substructure
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


ALL_SUBSTRUCTURES = [*_get_concrete_substructures()]

SUBSTRUCTURES = [s for s in ALL_SUBSTRUCTURES
                 if s not in _unnecessary_substructures]
