from inspect import isabstract as _isabstract

from ._base import Substructure
from ._ast_substructures import *
from ._cst_substructures import *


def get_concrete_base_classes():
    q = [Substructure]
    while q:
        current = q.pop()
        if not _isabstract(current):
            yield current
        q.extend(current.__subclasses__())


SUBSTRUCTURES = [*get_concrete_base_classes()]
