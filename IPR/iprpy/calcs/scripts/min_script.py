#Perform energy minimization on atoms in file read_data using potential information from all other parameters
def min_script(pair_info, units, atom_style, masses, read_data,
                    etol = 0, ftol = 1e-6, maxiter = 100000, maxeval = 100000):
    
    mass = ''
    for i in xrange(len(masses)):
        mass += 'mass %i %f\n'%(i+1,masses[i])
    
    nl = '\n'
    script = nl.join(['boundary p p p',
                      'units ' + units,
                      'atom_style ' + atom_style,
                      'read_data ' + read_data,
                      '',
                      mass,
                      pair_info,
                      '',
                      'variable peatom equal pe/atoms',
                      '',
                      'thermo_style custom step lx pxx pe v_peatom',
                      'thermo_modify format float %.13e',
                      '',
                      'dump dumpit all custom %i atom.* id type x y z'%(maxeval),
                      'dump_modify dumpit format "%i %i %.13e %.13e %.13e"',
                      'minimize %f %f %i %i'%(etol, ftol, maxiter, maxeval)])
    return script