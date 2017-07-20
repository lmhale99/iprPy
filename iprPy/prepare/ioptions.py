def ioptions(tdict, i=None):
    """Take dictionary with multiple option fields and yield each unique single option variation"""
    
    # Set maximum i value if not given
    if i is None:
        i = len(tdict) - 1
    
    # Yield empty dictionary when i < 0
    if i < 0:
        yield {}
    
    else:
        # Build list of sorted keys
        keys = sorted(tdict.keys())
        
        # Loop over dictionaries for smaller i
        for values in z(tdict, i-1):
            
            # Loop over values for current i
            for v in iaslist(tdict[keys[i]]):
                
                # Yield dictionaries for i and smaller
                values[keys[i]] = v
                yield values