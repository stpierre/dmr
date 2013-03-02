""" Base package for all dmr output formats """

import sys
from pkgutil import walk_packages

__all__ = []

for _mod in walk_packages(path=__path__, prefix=__name__ + "."):
    _modname = _mod[1]
    __import__(_modname)
    if getattr(sys.modules[_modname], "__expose__", True):
        __all__.append(_modname)
