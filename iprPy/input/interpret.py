# iprPy imports
from .interpret_functions import loaded

__all__ = ['interpret']

def interpret(style, input_dict, build=True, **kwargs):
    """
    
    """
    loaded[style](input_dict, build=build, **kwargs)