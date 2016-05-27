

def fill_template(template, variable, s_delimiter, e_delimiter):
    """
    Takes a template and fills in values for delimited template variable names.
    
    Arguments:
    template -- string, list of strings or file-like object representing a 
                template file.
    variable -- dictionary giving the values to fill in for each tempate variable name.
    s_delimiter -- leading delimiter for identifying the template variable names.
    s_delimiter -- trailing delimiter for identifying the template variable names.
    
    Returns a list of strings representing the filled-out file.
    """
    
    if isinstance(template, (str, unicode)):
        template = template.split('\n')
    
    result = []
    
    for line in template:
        while True:
            try:
                s = line.index(s_delimiter)
                e = line[s + len(s_delimiter):].index(e_delimiter) + s + len(s_delimiter)
            except:
                break
            name = line[s + len(s_delimiter): e]
            var = s_delimiter + name + e_delimiter
            try:
                value = variable[name]
                if isinstance(value, (int, long, float)): 
                    value = repr(value)
            except:
                raise ValueError('No value for ' + name + ' found')
            line = line.replace(var, value)
        result.append(line)
        
    return result
        
        