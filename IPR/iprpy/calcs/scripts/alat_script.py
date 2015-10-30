import iprp.lammps as lmp
import numpy as np

#Create a LAMMPS script that applies a hydrostatic strain.
def alat_script(pair_info, units, atom_style, masses, ucell, alat, 
                delta = 1e-5, steps = 2, size = np.array([3, 3, 3], dtype=np.int)):
    
    boxsize = np.array([[0, size[0]], [0, size[1]], [0, size[2]]], dtype=np.int)
    sys_gen = lmp.sys_gen_script(alat=alat, ucell=ucell, size=boxsize)
    mass = ''
    for i in xrange(len(masses)):
        mass += 'mass %i %f\n' % (i+1, masses[i])
     
    nl = '\n'
    script = nl.join(['boundary p p p',
                      'units ' + units,
                      'atom_style ' + atom_style,
                      '',
                      sys_gen,
                      '',
                      mass,
                      pair_info,
                      '',
                      'variable lx0 equal lx',
                      'variable ly0 equal ly',
                      'variable lz0 equal lz',
                      '',
                      'variable deltax equal %f/%f' % (delta, steps-1),
                      'variable aratio equal 1-%f/2.+(v_a-1)*${deltax}' % (delta),
                      '',
                      'variable xmax equal v_aratio*${lx0}',
                      'variable ymax equal v_aratio*${ly0}',
                      'variable zmax equal v_aratio*${lz0}',
                      'variable alat equal lx/%i' % (size[0]),
                      'variable blat equal ly/%i' % (size[1]),
                      'variable clat equal lz/%i' % (size[2]),
                      '',
                      'variable peatom equal pe/atoms',
                      'thermo_style custom step lx ly lz v_alat v_blat v_clat pxx pyy pzz v_peatom pe',
                      'thermo_modify format float %.13e',
                      '',
                      'label loop',
                      '',
                      'variable a loop %i' % (steps),
                      'change_box all x final 0 ${xmax} y final 0 ${ymax} z final 0 ${zmax} remap units box',
                      'run 0',
                      'next a','jump alat.in loop'])
    return script  