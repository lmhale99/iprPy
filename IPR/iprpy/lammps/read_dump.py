import iprpy
import numpy as np

#Reads a LAMMPS style dump file and returns a iprpy.System. 
def read_dump(fname):
    with open(fname, 'r') as fin:
        readnatoms = False
        readtime = False
        bcount = 3
        
        #loop over all lines in file
        for line in fin:
            terms = line.split()
            if len(terms) > 0:
                
                #read number of atoms if time to do so
                if readnatoms:                
                    natoms = int(terms[0])
                    atoms = [iprpy.Atom(1, np.zeros(3)) for i in xrange(natoms)]
                    readnatoms = False
                
                #read x boundary condition values if time to do so
                elif bcount == 0:
                    xlo = float(terms[0])
                    xhi = float(terms[1])
                    if len(terms) == 3:
                        xy = float(terms[2])
                    bcount += 1
                    
                #read y boundary condition values if time to do so
                elif bcount == 1:
                    ylo = float(terms[0])
                    yhi = float(terms[1])
                    if len(terms) == 3:
                        xz = float(terms[2])
                    bcount += 1
                    
                #read z boundary condition values if time to do so
                elif bcount == 2:
                    zlo = float(terms[0])
                    zhi = float(terms[1])
                    if len(terms) == 3:
                        yz = float(terms[2])
                        xlo = xlo - min((0.0, xy, xz, xy + xz))
                        xhi = xhi - max((0.0, xy, xz, xy + xz))
                        ylo = ylo - min((0.0, yz))
                        yhi = yhi - max((0.0, yz))
                        box = iprpy.Box(xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, zlo=zlo, zhi=zhi, xy=xy, xz=xz, yz=yz)
                    else:
                        box = iprpy.Box(xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, zlo=zlo, zhi=zhi)
                    sys = iprpy.System(box=box, pbc=pbc, atoms=atoms)  
                    bcount += 1
                
                #read atomic values if time to do so
                elif readtime:
                    atom_props = {}
                    for i in xrange(len(terms)):
                        atom_props[prop_names[i]] = terms[i]
                    
                    i = int(atom_props['id']) - 1
                    sys.atoms(i, 'atype', int(atom_props['type']))
                    if   pos_opt == 1:
                        pos = np.array([float(atom_props['x']), float(atom_props['y']), float(atom_props['z'])])
                    elif pos_opt == 2:
                        pos = np.array([float(atom_props['xu']), float(atom_props['yu']), float(atom_props['zu'])])
                    elif pos_opt == 3:
                        pos = np.array([float(atom_props['xs']), float(atom_props['ys']), float(atom_props['zs'])])
                    elif pos_opt == 4:
                        pos = np.array([float(atom_props['xsu']), float(atom_props['ysu']), float(atom_props['zsu'])])
                    sys.atoms(i, 'pos', pos, scale=scale)
                    for prop in prop_names:
                        if prop != 'x' and prop != 'y' and prop != 'z' and prop != 'xs' and prop != 'ys' and prop != 'zs' and prop != 'id' and prop != 'type':
                            sys.atoms(i, prop, atom_props[prop])
                    
                #if not time to read data, check ITEM: header information
                else:
                    #only consider ITEM: lines
                    if terms[0] == 'ITEM:':
                    
                        #ITEM: NUMBER indicates it is time to read natoms
                        if terms[1] == 'NUMBER':
                            readnatoms = True
                            
                        #ITEM: BOX gives pbc and indicates it is time to read box parameters
                        if terms[1] == 'BOX':
                            pbc = [True, True, True]
                            for i in xrange(3):
                                if terms[i + len(terms) - 3] != 'pp':
                                    pbc[i] = False
                            bcount = 0
                            
                        #ITEM: ATOMS gives list of per-Atom property names and indicates it is time to read atomic values      
                        elif terms[1] == 'ATOMS':
                            prop_names = terms[2:]
                            assert 'id' in prop_names,   'Atom id required!'
                            assert 'type' in prop_names, 'Atom type required!'
                            if 'x' in prop_names and 'y' in prop_names and 'z' in prop_names:
                                pos_opt = 1
                                scale = False
                            elif 'xu' in prop_names and 'yu' in prop_names and 'zu' in prop_names:
                                pos_opt = 2
                                scale = False
                            elif 'xs' in prop_names and 'ys' in prop_names and 'zs' in prop_names:
                                pos_opt = 3
                                scale = True
                            elif 'xsu' in prop_names and 'ysu' in prop_names and 'zsu' in prop_names:
                                pos_opt = 4  
                                scale = True
                            else:
                                raise ValueError('Atom coordinates required!')
                                
                            
                            readtime = True  
        
    return sys    