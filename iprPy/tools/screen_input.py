# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import sys

# iprPy imports
from ..compatibility import ispython2, ispython3

def screen_input(prompt=''):
    """
    Replacement input function that is compatible with Python versions 2 and
    3, as well as the mingw terminal.
    
    Parameters
    ----------
    prompt : str, optional
        The screen prompt to use for asking for the input.
        
    Returns
    -------
    str
        The user input.
    """
    
    # Flush prompt to work interactively with mingw
    print(prompt, end=' ')
    sys.stdout.flush()
    
    # Call version dependent function
    if ispython3: 
        return input()
    elif ispython2:
        return raw_input()
    else:
        raise ValueError('Unsupported Python version')