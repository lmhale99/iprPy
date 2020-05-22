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
from .Calculation import Calculation

ignorelist = ['Calculation']
loaded, failed = dynamic_import(__name__, ignorelist=ignorelist)

def load_calculation(style):
    """
    Loads a Calculation subclass associated with a given calculation style

    Parameters
    ----------
    style : str
        The calculation style
    
    Returns
    -------
    subclass of iprPy.calculation.Calculation 
        A Calculation object for the style
    """
    return loaded[style]()

__all__ = ['Calculation', 'load_calculation', 'failed', 'loaded']