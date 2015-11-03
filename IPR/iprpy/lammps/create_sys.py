import os
import subprocess

import numpy as np

import iprpy
from read_dump import read_dump
from sys_gen import sys_gen

#Uses LAMMPS to create a iprpy.System from the supplied system parameters    
def create_sys(file_name, lammps_exe, 
               pbc = (True, True, True),
               ucell_box = iprpy.Box(),
               ucell_atoms = [iprpy.Atom(1, np.array([0.0, 0.0, 0.0])),
                              iprpy.Atom(1, np.array([0.5, 0.5, 0.0])),
                              iprpy.Atom(1, np.array([0.0, 0.5, 0.5])),
                              iprpy.Atom(1, np.array([0.5, 0.0, 0.5]))],
               axes = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]),
               shift = np.array([0.0, 0.0, 0.0]),
               size = np.array([[-3,3], [-3,3], [-3,3]], dtype=np.int)):
          
    sys_info = sys_gen(ucell_box=ucell_box, ucell_atoms=ucell_atoms, axes=axes, shift=shift, size=size)

    newline = '\n'
    script = newline.join([sys_info,
                           '',
                           'mass * 1',
                           'pair_style none',
                           'atom_modify sort 0 0.0',
                           '',                           
                           'dump dumpit all custom 100000 %s id type x y z' % file_name,
                           'dump_modify dumpit format "%i %i %.13e %.13e %.13e"',                           
                           'run 0'])
    f = open('create_sys.in', 'w')
    f.write(script)
    f.close()
    output = subprocess.check_output(lammps_exe + ' -in create_sys.in', shell=True)

    sys0 = read_dump(file_name)
    os.remove('create_sys.in')
    os.remove('log.lammps')
    return sys0      