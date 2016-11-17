import numpy as np
def parse_size_mults(input_dict, size_mults='size_mults'):

    #Convert string to integer terms
    if isinstance(input_dict[size_mults], (str, unicode)): 
        new_mults = list(np.array(input_dict[size_mults].strip().split(), dtype=int))

    #Properly divide up size_mults if 6 terms given
    if len(new_mults) == 6:
        if (new_mults[0] <= 0 and new_mults[0] < new_mults[1] and new_mults[1] >= 0 and
            new_mults[2] <= 0 and new_mults[2] < new_mults[3] and new_mults[3] >= 0 and
            new_mults[4] <= 0 and new_mults[4] < new_mults[5] and new_mults[5] >= 0):
            return [[new_mults[0], new_mults[1]], 
                    [new_mults[2], new_mults[3]],
                    [new_mults[4], new_mults[5]]]
        
        else: raise ValueError('Invalid size_mults command')     
    
    #Properly divide up size_mults if 3 terms given
    elif len(new_mults) == 3:
        for i in xrange(3):
            
            #Add 0 before if value is positive
            if new_mults[i] > 0:
                new_mults[i] = [0, new_mults[i]]
            
            #Add 0 after if value is negative
            elif new_mults[i] < 0:
                new_mults[i] = [new_mults[i], 0]
            
            else: raise ValueError('Invalid size_mults command') 
        
        return new_mults
        
    else: raise ValueError('Invalid size_mults command') 