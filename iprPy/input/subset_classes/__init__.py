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

from ...tools import dynamic_import
from .Subset import Subset

ignorelist = ['Subset']
loaded, failed = dynamic_import(__file__, __name__, ignorelist=ignorelist)

__all__ = ['Subset', 'failed', 'loaded']