import numpy as np

def sizemults(input_dict, **kwargs):
    """
    Handles input parameters associated with system size multipliers.
    1. Returns numpy 3x2 array of ints associated with the 'sizemults' input 
       parameter string value.    
    
    Argument:
    input_dict -- dictionary containing input parameter key-value pairs
    
    Keyword Arguments:
    sizemults -- replacement parameter key name for 'sizemults'
    """
    
    #Convert string to integer terms
    if isinstance(input_dict[kwargs['sizemults']], (str, unicode)): 
        newmults = list(np.array(input_dict[kwargs['sizemults']].strip().split(), dtype=int))

    #Properly divide up sizemults if 6 terms given
    if len(newmults) == 6:
        if (newmults[0] <= 0 and newmults[0] < newmults[1] and newmults[1] >= 0 and
            newmults[2] <= 0 and newmults[2] < newmults[3] and newmults[3] >= 0 and
            newmults[4] <= 0 and newmults[4] < newmults[5] and newmults[5] >= 0):
            return [[newmults[0], newmults[1]], 
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
        
        return newmults
        
    else: raise ValueError('Invalid sizemults command') 