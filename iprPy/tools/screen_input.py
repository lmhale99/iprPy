from __future__ import division, absolute_import, print_function

import sys

PY3 = sys.version_info[0] > 2

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
    if PY3: 
        return input()
    else: 
        return raw_input()