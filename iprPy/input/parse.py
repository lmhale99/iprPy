# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from atomman.tools import uber_open_rmode
                       
# iprPy imports
from ..tools import aslist
from ..compatibility import stringtype

__all__ = ['parse']

def parse(inscript, singularkeys=[], allsingular=False):
    """
    Parses an input file and returns a dictionary of parameter terms.
    
    These are the parsing rules:
    
    - The first word in a line is taken as the key name of the parameter.
    - All other words are joined together into a single string value for the
      parameter.
    - Words that start with # indicate comments with that word and all words
      to the right of it in the same line being ignored.
    - Any lines with less than two non-comment terms are ignored. In other 
      words, blank lines and lines with keys but not values are skipped over.
    - Multiple values can be assigned to the same term by repeating the key 
      name on a different line. 
    - The keyword arguments can be used to issue an error if multiple values
      are trying to be assigned to terms that should only have a single 
      values.
    
    Parameters
    ----------
    inscript : string or file-like-object
        The file, path to file, or contents of the input script to parse.
    singularkeys : list of str, optional
        List of term keys that should not have multiple values.
    allsingular : bool, optional
        Indicates if all term keys should be singular (Default is False).
    
    Returns
    -------
    params : dict
        Dictionary of parsed input key-value pairs
        
    Raises
    ------
    ValueError
        If both singularkeys and allsingular are given, or if multiple values
        found for a singular key.
    """
    
    # Argument check
    singularkeys = aslist(singularkeys)
    if allsingular and len(singularkeys) > 0:
        raise ValueError('allsingular and singularkeys options cannot both be given')
    
    params = {}
    
    # Open inscript
    with uber_open_rmode(inscript) as infile:
        
        # Iterate over all lines in infile
        for line in infile:
            try:
                line = line.decode('utf-8')
            except:
                pass
            terms = line.split()
            
            # Remove comments
            i = 0
            index = len(line)
            while i < len(terms):
                if len(terms[i]) > 0 and terms[i][0] == '#':
                    index = line.index(terms[i])
                    break
                i += 1
            terms = terms[:i]
            line = line[:index]

            # Skip empty, comment, and valueless lines
            if len(terms) > 1:
                
                # Split into key and value
                key = terms[0]
                value = line.replace(key, '', 1).strip()
            
                # First time key is called save as is
                if key not in params:
                    params[key] = value
                
                # Append value to key if not singular
                elif not allsingular and key not in singularkeys:
                    
                    # Append value if parameter is already a list
                    if isinstance(params[key], list):
                        params[key].append(value)
                    
                    # Convert parameter to list if needed and then append value
                    else:
                        params[key] = [params[key]]
                        params[key].append(value)
                
                # Issue error for trying to append to a singular value
                else:
                    raise ValueError('multiple values found for singular input parameter ' + key)
    
    return params