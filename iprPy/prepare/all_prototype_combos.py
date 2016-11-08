import numpy as np

def all_prototype_combos(potentials, prototypes):
    
    for potential in potentials:
        symbols = np.array(potential['potential'].symbols)
        
        for prototype in prototypes:
            natypes = prototype['prototype'].natypes
            
            for i_vals in iterbox(len(symbols), natypes):
                yield potential, prototype, symbols[i_vals]

def iterbox(a, b):
    """Allows for dynamic iteration over all arrays of length b where each term is in range 0-a"""
    for i in xrange(a):    
        if b > 1:
            for j in iterbox(a,b-1):
                yield [i] + j
        elif b == 1:
            yield [i]