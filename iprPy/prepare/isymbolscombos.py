import numpy as np
import atomman.lammps as lmp

def isymbolscombos(prototype, potential):
    
    symbols = lmp.Potential(potential.content).symbols
    natypes = prototype.todict()['natypes']
            
    for ivals in iterbox(len(symbols), natypes):
        yield list(np.asarray(symbols)[ivals])

def iterbox(a, b):
    """Allows for dynamic iteration over all arrays of length b where each term is in range 0-a"""
    for i in xrange(a):    
        if b > 1:
            for j in iterbox(a,b-1):
                yield [i] + j
        elif b == 1:
            yield [i]