def disl_relax_script(pair_info, units, atom_style, masses, read_data, temp = 0):

    mass = ''
    group_move = ''
    for i in xrange(len(masses)):
        mass += 'mass %i %f\n'%(i+1,masses[i])
        if i < len(masses)/2:
            group_move += ' '+str(i+1)

    newline = '\n'
    script = newline.join(['boundary s s p',
                           'units ' + units,
                           'atom_style ' + atom_style,
                           'read_data ' + read_data,
                           '',
                           mass,
                           pair_info,
                           '',
                           'group move type' + group_move,
                           'group hold subtract all move',
                           '',
                           'compute peatom all pe/atom',
                           '',
                           'dump first all custom 100000 atom.* id type x y z c_peatom',
                           'dump_modify first format "%d %d %.13e %.13e %.13e %.13e"',
                           'thermo_style custom step pe',
                           ''])
    if temp == 0:
        script = newline.join([script, 
                               'fix nomove hold setforce 0.0 0.0 0.0',
                               'minimize 0 1e-5 10000 100000'])
    else:
        script = newline.join([script,
                               'velocity move create %f 9467 mom yes rot yes dist gaussian'%(2 * temp),
                               'fix nomove hold setforce 0.0 0.0 0.0',
                               'timestep 0.001',
                               'thermo 10000',
                               'fix 1 all nvt temp %f %f 0.1'%(temp, temp),
                               '',
                               'run 10000',
                               'minimize 0 1e-5 10000 100000'])  
    return script