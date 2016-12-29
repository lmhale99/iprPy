import numpy as np

def sizemults(input_dict, **kwargs):
    """
    Converts sizemults input term from a string to a 3x2 array of ints.
    
    The input_dict keys used by this function (which can be renamed using the 
    function's keyword arguments):
    sizemults -- a string of three or six space-delimited integers. This gets
                 replaced with a 3x2 array of integers.    
    
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    sizemults -- replacement parameter key name for 'sizemults'
    """
    
    #Set default keynames
    keynames = ['sizemults']
    for keyname in keynames:
        kwargs[keyname] = kwargs.get(keyname, keyname)
    
    #Give default values for terms
    input_dict[kwargs['sizemults']] = input_dict.get(kwargs['sizemults'], '1 1 1')
    
    #Convert string to integer terms
    newmults = list(np.array(input_dict[kwargs['sizemults']].strip().split(), dtype=int))

    #Properly divide up sizemults if 6 terms given
    if len(newmults) == 6:
        if (newmults[0] <= 0 and newmults[0] < newmults[1] and newmults[1] >= 0 and
            newmults[2] <= 0 and newmults[2] < newmults[3] and newmults[3] >= 0 and
            newmults[4] <= 0 and newmults[4] < newmults[5] and newmults[5] >= 0):
            input_dict['sizemults'] =  [[newmults[0], newmults[1]], 
                                        [newmults[2], newmults[3]],
                                        [newmults[4], newmults[5]]]
        
        else: raise ValueError('Invalid sizemults command')     
    
    #Properly divide up sizemults if 3 terms given
    elif len(newmults) == 3:
        for i in xrange(3):
            
            #Add 0 before if value is positive
            if newmults[i] > 0:
                newmults[i] = [0, newmults[i]]
            
            #Add 0 after if value is negative
            elif newmults[i] < 0:
                newmults[i] = [newmults[i], 0]
            
            else: raise ValueError('Invalid sizemults command') 

        input_dict['sizemults'] = newmults
        
    else: raise ValueError('Invalid sizemults command') 