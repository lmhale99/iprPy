import numpy as np

def axes(input_dict, **kwargs):
    """
    Converts a set of axes input terms to lists of three values each.
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    x_axis, y_axis, z_axis -- three right-handed orthogonal vectors. They are 
                              read in as space-delimited strings, and this 
                              function converts them to lists of floats.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    x_axis -- replacement parameter key name for 'x_axis'
    y_axis -- replacement parameter key name for 'y_axis'
    z_axis -- replacement parameter key name for 'z_axis'
    """
    #Set default keynames
    keynames = ['x_axis', 'y_axis', 'z_axis']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
        
    #Give default values for terms
    if kwargs['x_axis'] in input_dict or kwargs['y_axis'] in input_dict or kwargs['z_axis'] in input_dict:
        if kwargs['x_axis'] not in input_dict or kwargs['y_axis'] not in input_dict or kwargs['z_axis'] not in input_dict:
            raise TypeError('incomplete set of axis terms found')
    else:
        input_dict[kwargs['x_axis']] = '1 0 0'
        input_dict[kwargs['y_axis']] = '0 1 0'
        input_dict[kwargs['z_axis']] = '0 0 1'
     
    #Convert into lists of floats
    input_dict[kwargs['x_axis']] = list(np.array(input_dict[kwargs['x_axis']].strip().split(), dtype=float))
    input_dict[kwargs['y_axis']] = list(np.array(input_dict[kwargs['y_axis']].strip().split(), dtype=float))
    input_dict[kwargs['z_axis']] = list(np.array(input_dict[kwargs['z_axis']].strip().split(), dtype=float))