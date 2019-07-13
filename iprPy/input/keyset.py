# iprPy imports
from .keyset_functions import loaded

__all__ = ['keyset']

def keyset(style):
    """
    Wrapper function for the modular keyset styles
    """
    return loaded[style]()