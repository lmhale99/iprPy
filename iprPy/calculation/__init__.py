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
from .Calculation import Calculation

ignorelist = ['Calculation']
loaded, failed = dynamic_import(__file__, __name__, ignorelist=ignorelist)

def load_calculation(style):
    return loaded[style]()

__all__ = ['Calculation', 'load_calculation', 'failed', 'loaded']