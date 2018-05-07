# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# iprPy imports
from .buildcombos_functions import loaded

__all__ = ['buildcombos']

def buildcombos(style, database, keys, **kwargs):
    """
    Wrapper function for the modular builds styles
    """
    return loaded[style](database, keys, **kwargs)
