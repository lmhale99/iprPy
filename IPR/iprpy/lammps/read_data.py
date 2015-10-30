import iprpy
import numpy as np
from style_params import atom_style_params, velocity_style_params

#Reads a LAMMPS style data input file and returns a iprpy.System. 
#Periodic boundary information needs to be supplied as it is not given in the data file. 
def read_atom(fname, pbc=(True, True, True), atom_style='atomic'):
    with open(fname, 'r') as fin:
        readtime = False
        count = 0
        xy = None
        xz = None
        yz = None
        maxtype = 0
        sys = None
        
        #loop over all lines in file
        for line in fin:
            terms = line.split()
            if len(terms)>0:
                
                #read atomic information if time to do so
                if readtime == True:
                    id = int(terms[0]) - 1
                    for i in xrange(1, len(terms)):
                        if   prop_names[i] == 'type':
                            assert int(terms[i]) <= ntypes, 'More atom types found than indicated!'
                            sys.atoms(id, 'atype', int(terms[i]))
                            
                        elif prop_names[i] == 'x':
                            x = float(terms[i])
                        elif prop_names[i] == 'y':
                            y = float(terms[i])
                        elif prop_names[i] == 'z':
                            z = float(terms[i])
                            sys.atoms(id, 'pos', (x, y, z))
                        else:
                            try:
                                sys.atoms(id, prop_names[i], int(terms[i]))
                            except:
                                sys.atoms(id, prop_names[i], float(terms[i]))
                                
                    count += 1
                    if count == natoms:
                        readtime = False
                        count = 0
                
                #read number of atoms 
                elif len(terms) == 2 and terms[1] == 'atoms':
                    natoms = int(terms[0])
                
                #read number of atom types
                elif len(terms) == 3 and terms[1] == 'atom' and terms[2] == 'types': 
                    ntypes = int(terms[0])
                
                #read boundary info
                elif len(terms) == 4 and terms[2] == 'xlo' and terms[3] == 'xhi':
                    xlo = float(terms[0])
                    xhi = float(terms[1])
                elif len(terms) == 4 and terms[2] == 'ylo' and terms[3] == 'yhi':
                    ylo = float(terms[0])
                    yhi = float(terms[1])
                elif len(terms) == 4 and terms[2] == 'zlo' and terms[3] == 'zhi':
                    zlo = float(terms[0])
                    zhi = float(terms[1]) 
                elif len(terms) == 6 and terms[3] == 'xy' and terms[4] == 'xz' and terms[5] == 'yz':
                    xy = float(terms[0])
                    xz = float(terms[1])   
                    yz = float(terms[2])
                
                #Flag when reached data and setup for reading
                elif len(terms) == 1:
                    if terms[0] == 'Atoms':
                        if sys is None:
                            sys = iprpy.System(box = iprpy.Box(xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, zlo=zlo, zhi=zhi, xy=xy, xz=xz, yz=yz),
                                               atoms = [iprpy.Atom(1, np.zeros(3)) for i in xrange(natoms)],
                                               pbc = pbc)    
                        prop_names = atom_style_params(atom_style)
                        readtime = True
                        
                    elif terms[0] == 'Velocities':
                        if sys is None:
                            sys = iprpy.System(box = iprpy.Box(xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, zlo=zlo, zhi=zhi, xy=xy, xz=xz, yz=yz),
                                               atoms = [iprpy.Atom(1, np.zeros(3)) for i in xrange(natoms)],
                                               pbc = pbc)    
                        prop_names = velocity_style_params(atom_style)
                        readtime = True        
    return sys        