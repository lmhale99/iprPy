"""
Attributes
----------
loaded : dict
    Keys are the style names of the interpret functions that were
    successfully imported, and values are the associated functions.
failed : dict
    Keys are the style names of the interpret functions that failed import,
    and values are text of the associated error messages.
"""
from ...tools import dynamic_import

loaded, failed = dynamic_import(__file__, __name__)

__all__ = ['failed', 'loaded']