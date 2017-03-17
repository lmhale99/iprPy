import numpy as np

def atomshift(input_dict, **kwargs):
    """
    Converts the atomshift input term string into a list of floats.
    
    The input_dict keys used by this function (which can be renamed using the
    function's keyword arguments):
    atomshift -- a string of space-delimited numbers. This function
    converts it to a list of floats.
       
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    atomshift -- replacement parameter key name for 'atomshift'
    """
    #Set default keynames
    keynames = ['atomshift']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
        
    #Give default values for terms
    input_dict[kwargs['atomshift']] = input_dict.get(kwargs['atomshift'], '0 0 0')
   
    #Convert into list of floats
    input_dict[kwargs['atomshift']] = list(np.array(input_dict[kwargs['atomshift']].strip().split(), dtype=float))