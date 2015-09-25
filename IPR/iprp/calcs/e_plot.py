import subprocess
import numpy as np
import iprp.lammps as lmp
from calc_tools import *
from scripts import alat_script

#Measure crystal prototype energy as a function of lattice dimensions
def e_plot(lammps_exe, pot, elements, masses, proto, rmin=2.0, rmax=5.0, rsteps=200):
    #Variable setup and conversion
    rscale = calculate_r_a(proto)
    amin = rmin/rscale
    amax = rmax/rscale
    alat0 = (amax+amin)/2.
    alat = alat0*proto.get('lat_mult')
    delta = (amax-amin)/alat0 
    ucell = proto.get('ucell')
    units = pot.get('units')
    pair_info = pot.coeff(elements)
    atom_style = pot.get('atom_style')
    
    #Write the LAMMPS input file
    with open('alat.in','w') as script:
        script.write(alat_script(pair_info, units, atom_style, masses, ucell, alat, delta=delta, steps=rsteps))
    
    #Run LAMMPS
    data = lmp.extract(subprocess.check_output(lammps_exe+' < alat.in',shell=True))
    
    avalues = np.zeros((rsteps))
    evalues = np.zeros((rsteps))
    rvalues = np.zeros((rsteps))
    for c in xrange(rsteps):
        avalues[c] = float(data[c+1][4])
        rvalues[c] = float(data[c+1][4]) * rscale
        evalues[c] = float(data[c+1][10])
    return rvalues, avalues, evalues    
