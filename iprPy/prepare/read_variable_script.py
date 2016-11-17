from collections import OrderedDict

def read_variable_script(infile):
    
    variable = OrderedDict()
    if isinstance(infile, (str, unicode)):
        infile = infile.splitlines()

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
        if len(terms) > 0:
            
            #Split into name and value
            name = terms[0]
            value = ' '.join(terms[1:])
            assert len(terms) > 1, 'invalid argument: ' + name
        
            #First time name is called save as is
            if name not in variable:
                variable[name] = value
            
            #Second time name is called convert to list and append
            elif not isinstance(variable[name], list):
                variable[name] = [variable[name]]
                variable[name].append(value)
                
            else:
                variable[name].append(value)
            
    return variable