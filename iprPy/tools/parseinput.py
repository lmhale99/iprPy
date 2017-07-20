from .aslist import aslist

def parseinput(infile, singularkeys=[], allsingular=False):
    """
    Parses an input file and returns a dictionary of parameter terms.
    
    These are the parsing rules:
    - The first word in a line is taken as the key name of the parameter.
    - All other words are joined together into a single string value for the 
      parameter.
    - Words that start with # indicate comments with that word and all words to
      the right of it in the same line being ignored.
    - Any lines with less than two non-comment terms are ignored. In other words, 
      blank lines and lines with keys but not values are skipped over.    
    - Multiple values can be assigned to the same term by repeating the key 
      name on a different line. 
    - The keyword arguments can be used to issue an error if multiple values are 
      trying to be assigned to terms that should only have a single values. 
    
    Argument:
    infile -- string or file-like-object to parse out parameter terms. 
    
    Keyword Arguments:
    singularkeys -- list of term key names that should not have multiple values.  
    allsingular -- boolean indicating if all term keys should be singular.
    """
    
    #Argument check
    singularkeys = aslist(singularkeys)
    if allsingular and len(singularkeys) > 0:
        raise TypeError('allsingular and singularkeys options cannot both be given')
    
    #Split strings into lines
    if isinstance(infile, (str, unicode)):
        infile = infile.splitlines()

    params = {}
    
    #iterate over all lines in infile
    for line in infile:
        terms = line.split()

        #remove comments
        i = 0
        while i < len(terms):
            if len(terms[i]) > 0 and terms[i][0] == '#':
                break
            i += 1
        terms = terms[:i]

        #skip empty (and comment) lines
        if len(terms) > 1:
            
            #Split into key and value
            key = terms[0]
            value = ' '.join(terms[1:])
        
            #First time key is called save as is
            if key not in params:
                params[key] = value
            
            #Append value to key if not singular
            elif not allsingular and key not in singularkeys:
                
                #Append value if parameter is already a list
                if isinstance(params[key], list):
                    params[key].append(value)
                
                #Convert parameter to list if needed and then append value
                else:
                    params[key] = [params[key]]
                    params[key].append(value)
            
            #Issue error for trying to append to a singular value
            else:
                raise ValueError('multiple values found for singular input parameter ' + key)
            
    return params