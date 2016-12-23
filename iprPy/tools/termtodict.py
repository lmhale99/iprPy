from .aslist import aslist

def termtodict(term, keys):
    """
    Takes a string term and parses it into a dictionary of key-value pairs 
    based on the supplied key list
    
    Arguments:
    term -- string term to parse
    keys -- list of keys to search for
    
    """
    
    #Convert keys to list if needed
    keys = aslist(keys)
    
    #initialize parameter dict
    param_dict = {}

    words = term.split()
    
    #loop through all words of term
    key = None
    for word in words:
        if word in keys:
            key = word
            if key in param_dict:
                raise ValueError('Invalid terms: key '+key+' appears multiple times')
        else:
            if key is None:
                raise ValueError('Invalid terms: no keys match first term')
            elif key in param_dict:
                param_dict[key] += ' ' + word 
            else:
                param_dict[key] = word
    
    return param_dict            
