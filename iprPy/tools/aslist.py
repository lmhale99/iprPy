# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# iprPy imports
from ..compatibility import stringtype

def iaslist(term):
    """
    Iterate over items in term as if term was a list. Treats a str, unicode
    term as a single item.
    
    Parameters
    ----------
    term : any
        Term to iterate over.
    
    Yields
    ------
    any
        Items in the list representation of term.
    """
    if isinstance(term, stringtype):
        yield term
    else:
        try:
            for t in term:
                yield t
        except:
            yield term
            
def aslist(term):
    """
    Create list representation of term. Treats a str, unicode term as a single
    item.
    
    Parameters
    ----------
    term : any
        Term to convert into a list, if needed.
        
    Returns
    -------
    list of any
        All items in term as a list
    """
    return [t for t in iaslist(term)]