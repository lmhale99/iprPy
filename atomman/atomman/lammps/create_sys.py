import os
import subprocess

import numpy as np

from read_dump import read_dump

#Uses LAMMPS to create a iprpy.System from the supplied system parameters    
def create_sys(lammps_exe, system_info):

    newline = '\n'
    script = newline.join([system_info,
                           '',
                           'mass * 1',
                           'pair_style none',
                           'atom_modify sort 0 0.0',
                           '',                           
                           'dump dumpit all custom 100000 temp.dump id type x y z',
                           'dump_modify dumpit format "%i %i %.13e %.13e %.13e"',                           
                           'run 0'])
    f = open('create_sys.in', 'w')
    f.write(script)
    f.close()
    output = subprocess.check_output(lammps_exe + ' -in create_sys.in', shell=True)

    system = read_dump('temp.dump')
    os.remove('create_sys.in')
    os.remove('log.lammps')
    os.remove('temp.dump')
    return system      