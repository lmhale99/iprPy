import subprocess
import numpy as np
import iprp.lammps as lmp
from scripts import alat_script

def bulk_mod(lammps_exe, pot, elements, masses, proto, alat, size = np.array([3, 3, 3], dtype=np.int)):

    #needed parameters from the potential and prototype
    ucell = proto.get('ucell')          
    units = pot.get('units')
    pair_info = pot.coeff(elements)
    atom_style = pot.get('atom_style')
    
    #Write the LAMMPS input file
    with open('alat.in','w') as script:
        script.write(alat_script(pair_info, units, atom_style, masses, ucell, alat))    
        
    #Run LAMMPS
    data = lmp.extract(subprocess.check_output(lammps_exe+' < alat.in',shell=True))
    
    V = alat[0] * alat[1] * alat[2] * size[0] * size[1] * size[2]
    P1 = -((float(data[1][7]) + float(data[1][8]) + float(data[1][9])) / 3) * 1e-4
    P2 = -((float(data[2][7]) + float(data[2][8]) + float(data[2][9])) / 3) * 1e-4
    V1 = float(data[1][1]) * float(data[1][2]) * float(data[1][3])
    V2 = float(data[2][1]) * float(data[2][2]) * float(data[2][3])
    
    return V * (P2 - P1) / (V2 - V1)