import numpy as np

#Writes a LAMMPS style dump file from sys using all assigned per-atom properties    
def write_dump(fname, sys):
    f = open(fname,'w')
    
    #Write timestep info
    f.write('ITEM: TIMESTEP\n')
    f.write('0\n')
    
    #Write number of atoms
    f.write('ITEM: NUMBER OF ATOMS\n')
    f.write('%i\n' % ( sys.natoms() ))
    
    #Write system boundary info for an orthogonal box
    if np.isclose(sys.box('xy'), 0.0) and np.isclose(sys.box('xz'), 0.0) and np.isclose(sys.box('yz'), 0.0):
        f.write('ITEM: BOX BOUNDS')
        for i in xrange(3):
            if sys.pbc(i):
                f.write(' pp')
            else:
                f.write(' fm')
        f.write('\n')
        
        f.write('%f %f\n' % ( sys.box('xlo'), sys.box('xhi') )) 
        f.write('%f %f\n' % ( sys.box('ylo'), sys.box('yhi') ))
        f.write('%f %f\n' % ( sys.box('zlo'), sys.box('zhi') ))
    
    #Write system boundary info for a triclinic box
    else:
        f.write('ITEM: BOX BOUNDS xy xz yz')
        for i in xrange(3):
            if sys.pbc(i):
                f.write(' pp')
            else:
                f.write(' fm')
        f.write('\n')

        xlo_bound = sys.box('xlo') + min(( 0.0, sys.box('xy'), sys.box('xz'), sys.box('xy') + sys.box('xz') ))
        xhi_bound = sys.box('xhi') + max(( 0.0, sys.box('xy'), sys.box('xz'), sys.box('xy') + sys.box('xz') ))
        ylo_bound = sys.box('ylo') + min(( 0.0, sys.box('yz') ))
        yhi_bound = sys.box('yhi') + max(( 0.0, sys.box('yz') ))
        zlo_bound = sys.box('zlo')
        zhi_bound = sys.box('zhi')
        
        f.write('%f %f %f\n' % ( xlo_bound, xhi_bound, sys.box('xy') )) 
        f.write('%f %f %f\n' % ( ylo_bound, yhi_bound, sys.box('xz') ))
        f.write('%f %f %f\n' % ( zlo_bound, zhi_bound, sys.box('yz') ))

    #Write atomic header info
    prop_list = sys.atoms(0).prop_list()
    print prop_list
    f.write('ITEM: ATOMS id')
    for prop in prop_list:
        if prop == 'pos':
            f.write(' x y z')
        elif prop == 'atype':
            f.write(' type')
        elif isinstance(sys.atoms(0, prop), (list, tuple, np.ndarray)) and len(sys.atoms(0, prop)) > 1:
            if isinstance(sys.atoms(0, prop)[0], (list, tuple, np.ndarray)) and len(sys.atoms(0, prop)[0]) > 1:
                for i in xrange(len(sys.atoms(0, prop))):
                    for j in xrange(len(sys.atoms(0, prop)[0])):
                        f.write(' %s[%i][%i]' % (prop, i+1, j+1))
            else:
                for i in xrange(len(sys.atoms(0, prop))):
                    f.write(' %s[%i]' % (prop, i+1))
        else:
            f.write(' ' + prop)
    f.write('\n')
    
    #Write atomic info
    for i in xrange(sys.natoms()):
        f.write('%i' % (i+1))
        for prop in prop_list:
            if isinstance(sys.atoms(i, prop), int):
                f.write(' %i' % sys.atoms(i, prop))
            elif isinstance(sys.atoms(i, prop), float):
                f.write(' %.14e' % sys.atoms(i, prop))
            elif isinstance(sys.atoms(i, prop), (tuple, list, np.ndarray)) and len(sys.atoms(i, prop)) > 1:
                if isinstance(sys.atoms(i, prop)[0], (list, tuple, np.ndarray)) and len(sys.atoms(i, prop)[0]) > 1:
                    for j in xrange(len(sys.atoms(i, prop))):
                        for k in xrange(len(sys.atoms(i, prop)[0])):
                            if   isinstance(sys.atoms(i, prop)[j][k], int):
                                f.write(' %i' % sys.atoms(i, prop)[j][k])
                            elif isinstance(sys.atoms(i, prop)[j][k], float):
                                f.write(' %.14e' % sys.atoms(i, prop)[j][k])
                            else:
                                f.write(' %s' % sys.atoms(i, prop)[j][k])
                else:
                    for j in xrange(len(sys.atoms(i, prop))):
                        if   isinstance(sys.atoms(i, prop)[j], int):
                            f.write(' %i' % sys.atoms(i, prop)[j])
                        elif isinstance(sys.atoms(i, prop)[j], float):
                            f.write(' %.14e' % sys.atoms(i, prop)[j])
                        else:
                            f.write(' %s' % sys.atoms(i, prop)[j])
            else:
                f.write(' %s' % sys.atoms(i, prop))
        f.write('\n')

    f.close()