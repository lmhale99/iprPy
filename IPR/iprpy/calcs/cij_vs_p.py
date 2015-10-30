import numpy as np
import iprp.lammps as lmp
import subprocess
from scripts import alat_script, cij_script

#Computes the pressure dependent elastic constants in strain range "delta" for "steps" number of points
def cij_vs_p(lammps_exe, pot, elements, masses, proto, alat, delta = 0.1, steps = 200):
    
    #Initial parameter setup
    ucell = proto.get('ucell')
    units = pot.get('units')
    pair_info = pot.coeff(elements)
    atom_style = pot.get('atom_style')
    
    #initial parameter definitions
    pvalues = np.empty((steps))
    C11 = np.empty((steps))
    C22 = np.empty((steps))
    C33 = np.empty((steps))
    C12 = np.empty((steps))
    C13 = np.empty((steps))
    C23 = np.empty((steps))
    C44 = np.empty((steps))
    C55 = np.empty((steps))
    C66 = np.empty((steps))
    dimensions = np.empty((13,6))       
    stresses = np.empty((13,6))
    
    #Run alat script in LAMMPS
    with open('alat.in','w') as f:
        f.write(alat_script(pair_info, units, atom_style, masses, ucell, alat, delta=delta, steps=steps))
    data1 = lmp.extract(subprocess.check_output(lammps_exe + ' < alat.in', shell=True))
    
    #Extract pressures and associated lattice parameters
    for c in xrange(steps):
        alat1 = np.array([float(data1[c+1][4]), float(data1[c+1][5]), float(data1[c+1][6])])
        pvalues[c] = ((float(data1[c+1][7]) + float(data1[c+1][8]) + float(data1[c+1][9])) / 3 ) * 1e-4
    
        with open('cij.in','w') as f:
            f.write(cij_script(pair_info, units, atom_style, masses, ucell, alat1))
            
        data2 = lmp.extract(subprocess.check_output(lammps_exe+' < cij.in',shell=True))
 
        #Extract system dimensions and pressures from LAMMPS data output
        for q in xrange(13):
            for p in xrange(6):
                dimensions[q, p] = float(data2[q+1][p+1])
                stresses[q, p] = -float(data2[q+1][p+10])*1e-4
        eps_scale = np.array([dimensions[0,0], dimensions[0,1], dimensions[0,2], 
                              dimensions[0,2], dimensions[0,2], dimensions[0,1]])

        #Calculate Cij from LAMMPS results
        cij = np.empty((6,6))
        for i in xrange(0,6):
            eps_ij = (dimensions[2*i+2, i] - dimensions[2*i+1, i]) / eps_scale[i]  
            for j in xrange(0,6):
                sig_ij = stresses[2*i+2, j] - stresses[2*i+1, j]
                cij[j,i] = sig_ij/eps_ij
        
        C11[c] = cij[0,0]
        C22[c] = cij[1,1]
        C33[c] = cij[2,2]
        C12[c] = cij[0,1]
        C13[c] = cij[0,2]
        C23[c] = cij[1,2]
        C44[c] = cij[3,3]
        C55[c] = cij[4,4]
        C66[c] = cij[5,5]
    
    return {'p':pvalues, 'C11':C11,'C22':C22,'C33':C33,
                         'C12':C12,'C13':C13,'C23':C23,
                         'C44':C44,'C55':C55,'C66':C66}