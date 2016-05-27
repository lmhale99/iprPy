def list_build(terms, t_dict):
    """
    Takes a list of terms and a dictionary of terms t_dict and builds a full 
    list where any terms matching names in t_dict are replaced by the t_dict 
    values. 
    
    For example:
    terms = ['x', 'y', 'z']
    t_dict = {'y':'a', 'z':['b', 'c']}
    then list_build(terms, t_dict) returns ['x', 'a', 'b', 'c']
    
    """
    
    new_terms = []
    if not isinstance(terms, list):
        terms = [terms]
    
    for term in terms:
        if term in t_dict:
            for val in t_dict.iteraslist(term):
                if val not in new_terms:
                    new_terms.append(val)
        else:  
            if term not in new_terms:
                new_terms.append(term)
    return new_terms