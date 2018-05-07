# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# iprPy imports
from .interpret_functions import loaded

__all__ = ['interpret']

def interpret(style, input_dict, build=True, **kwargs):
    """
    
    """
    loaded[style](input_dict, build=build, **kwargs)