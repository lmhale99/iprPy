# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# iprPy imports
from ..tools import aslist

__all__ = ['termtodict']

def termtodict(term, keys):
    """
    Takes a str term and parses it into a dictionary of key-value pairs
    based on the supplied key list.
    
    Parameters
    ----------
    term : str, unicode
        The str term to parse.
    keys : list of str
        The list of keys to parse by.
    
    Returns
    -------
    dict
        Dictionary of parsed key-value terms.
        
    Raises
    ------
    ValueError
        If any key appears mupltiple times or the first word in term does not
        match a key.
    
    """
    
    # Convert keys to list if needed
    keys = aslist(keys)
    
    # Initialize parameter dict
    param_dict = {}

    words = term.split()
    
    # Loop through all words of term
    key = None
    for word in words:
        if word in keys:
            key = word
            if key in param_dict:
                raise ValueError('Invalid terms: key ' + key
                                 + ' appears multiple times')
        else:
            if key is None:
                raise ValueError('Invalid terms: no keys match first term')
            elif key in param_dict:
                param_dict[key] += ' ' + word 
            else:
                param_dict[key] = word
    
    return param_dict