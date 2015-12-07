import numpy as np

#Writes a LAMMPS style dump file from system using all assigned per-atom properties    
def write_dump(fname, system, xf='%.13e', scale=False):
    f = open(fname,'w')
    
    #Write timestep info
    f.write('ITEM: TIMESTEP\n')
    f.write('0\n')
    
    #Write number of atoms
    f.write('ITEM: NUMBER OF ATOMS\n')
    f.write('%i\n' % ( system.natoms() ))
    
    #Write systemtem boundary info for an orthogonal box
    if np.isclose(system.box('xy'), 0.0) and np.isclose(system.box('xz'), 0.0) and np.isclose(system.box('yz'), 0.0):
        f.write('ITEM: BOX BOUNDS')
        for i in xrange(3):
            if system.pbc(i):
                f.write(' pp')
            else:
                f.write(' fm')
        f.write('\n')
        
        f.write('%f %f\n' % ( system.box('xlo'), system.box('xhi') )) 
        f.write('%f %f\n' % ( system.box('ylo'), system.box('yhi') ))
        f.write('%f %f\n' % ( system.box('zlo'), system.box('zhi') ))
    
    #Write systemtem boundary info for a triclinic box
    else:
        f.write('ITEM: BOX BOUNDS xy xz yz')
        for i in xrange(3):
            if system.pbc(i):
                f.write(' pp')
            else:
                f.write(' fm')
        f.write('\n')

        xlo_bound = system.box('xlo') + min(( 0.0, system.box('xy'), system.box('xz'), system.box('xy') + system.box('xz') ))
        xhi_bound = system.box('xhi') + max(( 0.0, system.box('xy'), system.box('xz'), system.box('xy') + system.box('xz') ))
        ylo_bound = system.box('ylo') + min(( 0.0, system.box('yz') ))
        yhi_bound = system.box('yhi') + max(( 0.0, system.box('yz') ))
        zlo_bound = system.box('zlo')
        zhi_bound = system.box('zhi')
        
        f.write('%f %f %f\n' % ( xlo_bound, xhi_bound, system.box('xy') )) 
        f.write('%f %f %f\n' % ( ylo_bound, yhi_bound, system.box('xz') ))
        f.write('%f %f %f\n' % ( zlo_bound, zhi_bound, system.box('yz') ))

    #Write atomic header info
    prop_list = system.atoms_prop_list()

    f.write('ITEM: ATOMS id')
    for prop in prop_list:
        #Change atype to type
        if prop == 'atype':
            f.write(' type')
        
        #Change pos to x y z or xs ys zs
        elif prop == 'pos':
            if scale:
                f.write(' xs ys zs')
            else:
                f.write(' x y z')
        
        #Handle all other properties
        else:
            test = system.atoms(0, prop)
            shape = test.shape
            #Scaler
            if len(shape) == 0:
                f.write(' ' + prop)
            #Vector
            elif len(shape) == 1:
                for i in xrange(shape[0]):
                    f.write(' %s[%i]' % (prop, i))
            #Array
            elif len(shape) == 2:
                for i in xrange(shape[0]):
                    for j in xrange(shape[1]):
                        f.write(' %s[%i][%i]' % (prop, i, j))
                
    f.write('\n')
    
    #Write atomic info
    for i in xrange(system.natoms()):
        f.write('%i' % (i+1))
        for prop in prop_list:
            value = system.atoms(i, prop)
            shape = value.shape
            dtype = value.dtype
            
            #Scaler
            if len(shape) == 0:
                if dtype == int:
                    f.write(' %i' % value)
                else:
                    f.write(' ' + xf % value)
            
            #Vector
            elif len(shape) == 1:
                if prop == 'pos' and scale:
                    value = system.scale(value)
                for j in xrange(shape[0]):
                    if dtype == int:
                        f.write(' %i' % value[j])
                    else:
                        f.write(' ' + xf % value[j])

            #Array
            elif len(shape) == 2:
                for j in xrange(shape[0]):
                    for k in xrange(shape[0]):
                        if dtype == int:
                            f.write(' %i' % value[j][k])
                        else:
                            f.write(' ' + xf % value[j][k])
            
        f.write('\n')

    f.close()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
