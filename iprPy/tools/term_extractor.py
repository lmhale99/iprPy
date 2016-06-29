
def term_extractor(terms, keys):
    """
    Converts a list of terms into a dictionary according to a list of keys.
    
    Arguments:
    terms -- list of terms or string of terms
    keys -- list of keys to search for
    
    Note: the first term in terms must match one of the keys
    
    Returns a dictionary with keys matching the found keys,
    and values as space-delimited strings of the terms between the keys
    """
    #convert terms to list using split if it is a string
    if isinstance(terms, (str, unicode)):
        terms = terms.split()    
    
    #initilize dict and set key to None (used to check first term is a key)
    term_dict = {}
    key = None
    
    #loop through all terms
    for term in terms:
        if term in keys:
            key = term
            if key not in term_dict:
                term_dict[key] = []
            else:
                raise ValueError('Invalid terms: key '+key+' appears multiple times')
        else:
            if key is None:
                raise ValueError('Invalid terms: no keys match first term')
            else:
                term_dict[key].append(term)
    
    #convert terms lists to space-delimited strings
    for key in term_dict:
        term_dict[key] = ' '.join(term_dict[key])
    
    return term_dict        
