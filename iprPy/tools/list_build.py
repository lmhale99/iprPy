#def expand_values(values, variables):
def list_build(values, variables):
    """
    Expands a list by replacing any values that match key names in a 
    variable dictionary with the corresponding dictionary's values. Duplicate
    values are excluded. 
    
    For example:
    values = ['x', 'y', 'z']
    variables = {'y':'a', 'z':['b', 'c']}
    then expand_values(values, variables) returns ['x', 'a', 'b', 'c']    
    """
    
    new_values = []
    if not isinstance(values, list):
        values = [values]
    
    for value in values:
        if value in variables:
            for val in variables.iteraslist(value):
                if val not in new_values:
                    new_values.append(val)
        else:  
            if value not in new_values:
                new_values.append(value)
    
    if len(new_values) == 1:
        new_values = new_values[0]
    
    return new_values