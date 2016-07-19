from DataModelDict import DataModelDict as DM
from copy import deepcopy

def term_extractor(terms, variables, keys):
    """
    Returns a variable dictionary of specified keys with values taken from inline terms and the pre-defined variable dictionary.
    Preference is given to inline terms over the pre-defined variables.
    
    Arguments:
    terms -- the inline terms of a function as a list or string
    variables -- the pre-defined variable dictionary
    keys -- list of keys to search for
    
    """
    #convert terms to list using split if it is a string
    if isinstance(terms, (str, unicode)):
        terms = terms.split()    
    
    #initilize dict and set key to None (used to check first term is a key)
    v = DM()
    key = None
    
    #loop through all terms
    for term in terms:
        if term in keys:
            key = term
            if key in v:
                raise ValueError('Invalid terms: key '+key+' appears multiple times')
        else:
            if key is None:
                raise ValueError('Invalid terms: no keys match first term')
            else:
                v.append(key, term)
    
    #convert terms to strings and check for matching variables 
    for key in v:
        v[key] = ' '.join(v.aslist(key))
        if v[key] in variables:
            v[key] = deepcopy(variables[v[key]])
    
    #fill in missing keys using pre-defined variable
    for key in keys:
        if key not in v and key in variables:
            v[key] = deepcopy(variables[key])        
    
    return v        
