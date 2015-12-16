import numpy as np
from style_params import atom_style_params, velocity_style_params

#Writes a LAMMPS style atom file from system using supplied atom style    
def write_data(fname, system, units='metal', atom_style='atomic'):
    #Wrap atoms
    system.wrap()
    
    #Header info
    f = open(fname,'w')
    f.write('\n%i atoms\n' % system.natoms())
    f.write('%i atom types\n' % system.natypes())
    f.write('%f %f xlo xhi\n' % (system.box('xlo'), system.box('xhi')))
    f.write('%f %f ylo yhi\n' % (system.box('ylo'), system.box('yhi')))
    f.write('%f %f zlo zhi\n' % (system.box('zlo'), system.box('zhi')))
    if np.isclose(system.box('xy'), 0.0) and np.isclose(system.box('xz'), 0.0) and np.isclose(system.box('yz'), 0.0):
        pass
    else:
        f.write('%f %f %f xy xz yz\n' % (system.box('xy'), system.box('xz'), system.box('yz')))
    
    #Write atom info
    prop_names = atom_style_params(atom_style=atom_style)
    f.write('\nAtoms\n\n')
    for i in xrange(system.natoms()):
        line = '%i' % (i+1)
        for prop in prop_names:
            if prop == 'id':
                pass
            elif prop == 'type':
                line += ' %i' % system.atoms(i, 'atype')
            elif prop == 'x':
                line += ' %.13e' % system.atoms(i, 'pos', 0)
            elif prop == 'y':
                line += ' %.13e' % system.atoms(i, 'pos', 1)
            elif prop == 'z':
                line += ' %.13e' % system.atoms(i, 'pos', 2)
            else:
                if isinstance(system.atoms(i, prop), int):
                    line += ' %i' % system.atoms(i, prop)
                else:
                    line += ' %.13e' % system.atoms(i, prop)
        f.write(line+'\n')
        
    #Test for velocity info
    prop_names = velocity_style_params(atom_style=atom_style)
    do_velocity = True
    for prop in prop_names:
        if system.atoms(0, prop) is None:
            do_velocity = False
            break
    
    #Write velocity info
    if do_velocity:
        f.write('\nVelocities\n\n')
        for i in xrange(system.natoms()):
            line = '%i' % (i+1)
            for prop in prop_names:
                if prop == 'id':
                    pass
                else:
                    if isinstance(system.atoms(i, prop), int):
                        line += ' %i' % system.atoms(i, prop)
                    else:
                        line += ' %.13e' % system.atoms(i, prop)
            f.write(line+'\n')
    
    f.close()
    
    boundary = ''
    for i in xrange(3):
        if system.pbc(i):
            boundary += 'p '
        else:
            boundary += 'm '    
    
    newline = '\n'
    script = newline.join(['#Script and data file prepared by AtomMan package',
                           '',
                           'units ' + units,
                           'atom_style ' + atom_style,
                           ''
                           'boundary ' + boundary,
                           'read_data ' + fname])
    return script
    