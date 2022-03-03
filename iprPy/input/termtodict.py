# coding: utf-8

# Standard Python libraries
from typing import List

# iprPy imports
from ..tools import aslist

__all__ = ['termtodict']

def termtodict(term: str,
               keys: List[str]) -> dict:
    """
    Takes a str term and parses it into a dictionary of key-value pairs
    based on the supplied key list.
    
    Parameters
    ----------
    term : str
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
        If any key appears multiple times or the first word in term does not
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

def dicttoterm(param_dict: dict) -> str:
    """
    Takes a dictionary and converts it into a single str term that can be
    parsed by termtodict().
    
    Parameters
    ----------
    param_dict : dict
        The dictionary of separated parameter terms.
    
    Returns
    -------
    str
        The single str term representation.
    """
    term = ''
    for key, value in param_dict.items():
        term += f'{key} '
        for v in aslist(value):
            term += f'{v} '
    return term