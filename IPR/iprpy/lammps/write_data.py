from style_params import atom_style_params, velocity_style_params

#Writes a LAMMPS style atom file from sys using supplied atom style    
def write_data(fname, sys, units='metal', atom_style='atomic'):
    #Header info
    f = open(fname,'w')
    f.write('\n%i atoms\n' % sys.natoms())
    f.write('%i atom types\n' % sys.ntypes())
    f.write('%f %f xlo xhi\n' % (sys.box('xlo'), sys.box('xhi')))
    f.write('%f %f ylo yhi\n' % (sys.box('ylo'), sys.box('yhi')))
    f.write('%f %f zlo zhi\n' % (sys.box('zlo'), sys.box('zhi')))
    if np.isclose(sys.box('xy'), 0.0) and np.isclose(sys.box('xz'), 0.0) and np.isclose(sys.box('yz'), 0.0):
        pass
    else:
        f.write('%f %f %f xy xz yz\n' % (sys.box('xy'), sys.box('xz'), sys.box('yz')))
    
    #Write atom info
    prop_names = atom_style_params(atom_style=atom_style)
    f.write('\nAtoms\n\n')
    for i in xrange(sys.natoms()):
        line = '%i' % (i+1)
        for prop in prop_names:
            if prop == 'id':
                pass
            elif prop == 'type':
                line += ' %i' % sys.atoms(i, 'atype')
            elif prop == 'x':
                line += ' %.13e' % sys.atoms(i, 'pos', 0)
            elif prop == 'y':
                line += ' %.13e' % sys.atoms(i, 'pos', 1)
            elif prop == 'z':
                line += ' %.13e' % sys.atoms(i, 'pos', 2)
            else:
                if isinstance(sys.atoms(i, prop), int):
                    line += ' %i' % sys.atoms(i, prop)
                else:
                    line += ' %.13e' % sys.atoms(i, prop)
        f.write(line+'\n')
        
    #Test for velocity info
    prop_names = velocity_style_params(atom_style=atom_style)
    do_velocity = True
    for prop in prop_names:
        if sys.atoms(0, prop) is None:
            do_velocity = False
            break
    
    #Write velocity info
    if do_velocity:
        f.write('\nVelocities\n\n')
    for i in xrange(sys.natoms()):
        line = '%i' % (i+1)
        for prop in prop_names:
            if prop == 'id':
                pass
            else:
                if isinstance(sys.atoms(i, prop), int):
                    line += ' %i' % sys.atoms(i, prop)
                else:
                    line += ' %.13e' % sys.atoms(i, prop)
        f.write(line+'\n')
    
    f.close()
    
    boundary = ''
    for i in xrange(3):
        if sys.pbc(i):
            boundary += 'p '
        else:
            boundary += 'm '    
    
    newline = '\n'
    script = newline.join(['#Script prepared by NIST iprPy code',
                           '',
                           'units ' + units,
                           'atom_style ' + atom_style,
                           ''
                           'boundary ' + boundary,
                           'read_data ' + fname])
    return script
    