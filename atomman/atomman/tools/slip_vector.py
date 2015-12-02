import atomman as am
from mag import mag
import numpy as np

def slip_vector(sys0, sys1, variable_name='slip'):
    #Computes the slip vector for all atoms in sys1 relative to sys0
    
    #Check that sys0 and sys1 are corresponding Systems
    assert isinstance(sys0, am.System), 'Invalid system type'
    assert isinstance(sys1, am.System), 'Invalid system type'
    assert sys0.natoms() == sys1.natoms(), 'Systems have different numbers of atoms'
    
    #Check that sys0 has a neighbor list
    nlist = sys0.prop('nlist')
    assert nlist is not None,   'No neighbor list for reference system!'

    #Calculate the slip vector
    for i in xrange(sys0.natoms()):
        slip = np.zeros(3)
        for n in xrange(1, nlist[i][0]+1):
            j = nlist[i][n]
            slip -= sys1.dvect(i, j) - sys0.dvect(i, j)
            
        sys1.atoms(i, variable_name, slip)
        sys1.atoms(i, variable_name+'_mag', mag(slip))