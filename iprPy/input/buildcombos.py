# iprPy imports
from .buildcombos_functions import loaded

__all__ = ['buildcombos']

def buildcombos(style, database, keys, content_dict=None, **kwargs):
    """
    Wrapper function for the modular buildcombos styles
    """
    return loaded[style](database, keys, content_dict=content_dict, **kwargs)
