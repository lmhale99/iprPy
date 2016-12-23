def filltemplate(template, variable, s_delimiter, e_delimiter):
    """
    Takes a template and fills in values for delimited template variable names.
    
    Arguments:
    template -- string or file-like object representing a template file.
    variable -- dictionary giving the values to fill in for each tempate variable name.
    s_delimiter -- leading delimiter for identifying the template variable names.
    s_delimiter -- trailing delimiter for identifying the template variable names.
    
    Returns a string of the template with all indicated values replaced.
    """
    
    #Convert to string if a file-like object
    try:
        template = template.read()
    except AttributeError:
        pass
    
    #Loop until done
    while True:
        
        #Search for starting delimiter
        try:
            s = template.index(s_delimiter)
        except ValueError: 
            s = None
        else:
            s = s + len(s_delimiter)
        
        #search for ending delimiter
        try:
            e = template.index(e_delimiter)
        except ValueError:
            e = None        
        
        #Replace delimited string with value
        if s is not None and e is not None and s < e:
            name = template[s: e]
            var = s_delimiter + name + e_delimiter
            try:
                value = str(variable[name])
            except KeyError:
                raise KeyError(name + ' not found in variable dictionary')
            template = template.replace(var, value)
        
        #Finish if no delimiters remain
        elif s is None and e is None:
            break
            
        #Issue errors
        elif s is None:
            raise ValueError('ending delimiter found without starting delimiter')
        elif e is None:
            raise ValueError('starting delimiter found without ending delimiter')
        else:
            raise ValueError('ending delimiter found before starting delimiter')
            
    return template
        
        