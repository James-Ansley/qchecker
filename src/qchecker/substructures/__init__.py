from inspect import isabstract as _isabstract

from ._ast_substructures import *
from ._base import Substructure
from ._cst_substructures import *


def _get_concrete_substructures():
    q = [Substructure]
    while q:
        current = q.pop()
        if not _isabstract(current):
            yield current
        q.extend(current.__subclasses__())


SUBSTRUCTURES = [*_get_concrete_substructures()]
