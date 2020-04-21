# coding: utf-8
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
from ..tools import dynamic_import

from .Database import Database

ignorelist = ['Database', 'prepare', 'runner', 'load_database']
loaded, failed = dynamic_import(__name__, ignorelist=ignorelist)

from .load_database import load_database

__all__ = ['Database', 'load_database', 'failed', 'loaded']
__all__.sort()