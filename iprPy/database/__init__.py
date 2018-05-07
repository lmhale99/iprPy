"""
Attributes
----------
loaded : dict
    Dictionary of the derived classes
databases_dict : dict
    Dictionary of the database styles that successfully loaded. The
    dictionary keys are the database style names, and the values are the
    loaded modules.
"""
# Standard Python libraries
from __future__ import division, absolute_import, print_function

from ..tools import dynamic_import
from .Database import Database

ignorelist = ['Database', 'prepare', 'runner', 'settings']
loaded, failed = dynamic_import(__file__, __name__, ignorelist=ignorelist)

from .settings import *
from .settings import __all__ as settings_all

__all__ = settings_all + ['Database', 'failed', 'loaded']
__all__.sort()