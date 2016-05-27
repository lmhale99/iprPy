
def all_combinations(variable, keys):
    """
    Generate all combinations based on variables with lists of values.
    
    Arguments:
    variable -- DataModelDict of key-value pairs where value may be a list
    keys -- list of key names to include in the combination
    
    yields tuples containing a value for each key
    """
    
    for v in variable.iteraslist(keys[0]):
        if len(keys) == 1:
            yield (v,)
        else:
            for vals in all_combinations(variable, keys[1:]):
                yield (v,) + vals
                
                
def index_combinations(variable, keys):
    """
    Generate all combinations based on variables with lists of values.
    
    Arguments:
    variable -- DataModelDict of key-value pairs where value may be a list
    keys -- list of key names to include in the combination
    
    yields tuples containing each parameter index set
    """
    
    for i in xrange(len(variable.aslist(keys[0]))):
        if len(keys) == 1:
            yield (i,)
        else:
            for ii in index_combinations(variable, keys[1:]):
                yield (i,) + ii