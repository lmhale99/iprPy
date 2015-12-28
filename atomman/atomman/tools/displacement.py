import atomman as am
from atomman.tools import mag

def displacement(sys0, sys1, variable_name='disp'):
    #Computes the slip vector for all atoms in sys1 relative to sys0    
    
    #Check that sys0 and sys1 are corresponding Systems
    assert isinstance(sys0, am.System), 'Invalid system type'
    assert isinstance(sys1, am.System), 'Invalid system type'
    assert sys0.natoms() == sys1.natoms(), 'Systems have different numbers of atoms'

    #Calculate the displacement vector
    for i in xrange(sys0.natoms()):
        disp = sys1.dvect(i, sys0.atoms(i))
            
        sys1.atoms(i, variable_name, disp)
        sys1.atoms(i, variable_name+'_mag', mag(disp))
    