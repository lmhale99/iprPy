# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# http://www.numpy.org/
import numpy as np

# https://github.com/usnistgov/atomman
import atomman.lammps as lmp

# iprPy imports
from ..compatibility import range

def isymbolscombos(prototype, potential):
    """
    Iterates over all possible symbol combinations associated with a
    prototype's unique (Wycoff) sites and a potential's element models.
    
    Parameters
    ----------
    potential : iprPy.Record
        A record associated with an interatomic potential.
    prototype : iprPy.Record
        A record associated with a crystal prototype
        
    Yields
    ------
    list of str
        List of symbol tags corresponding to the potential's element models
        and the prototype's unique sites.
    """
    symbols = lmp.Potential(potential.content).symbols
    natypes = prototype.todict()['natypes']
            
    for ivals in iterbox(len(symbols), natypes):
        yield list(np.asarray(symbols)[ivals])

def iterbox(a, b):
    """
    Yields lists of integers of length b where each term is in range 0-a.
    """
    for i in range(a):
        if b > 1:
            for j in iterbox(a,b-1):
                yield [i] + j
        elif b == 1:
            yield [i]