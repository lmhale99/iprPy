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
from .Record import Record

ignorelist = ['Record']
loaded, failed = dynamic_import(__file__, __name__, ignorelist=ignorelist)

def load_record(style, name=None, content=None):
    return loaded[style](name=name, content=content)

__all__ = ['Record', 'load_record', 'failed', 'loaded']