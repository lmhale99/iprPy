import subprocess
import numpy as np
import iprp.lammps as lmp
from copy import deepcopy
from scripts import cij_script
  
#Iterates to compute the exact lattice parameters for a particular potential+crystal from initial guess.
#Returns refined lattice parameters along with cohesive energy and elastic constant matrix
def refine_lat(lammps_exe, pot, elements, masses, proto, alat_init):
    
    #initial parameter setup
    alat0 = deepcopy(alat_init)         #lattice parameter guess to check
    alat1 = np.zeros(3)                 #new updated guess based on Cij
    alat_neg1 = np.zeros(3)             #old guess from prior to alat0
    converged = False                   #flag for if values have converged
    size = [3,3,3]                      #system size scalers (i.e. lx = 3 * a)
    dimensions = np.empty((13,6))       #system dimensions taken from simulation results
    stresses = np.empty((13,6))         #system virial stresses (-pressures) taken from sim results
    
    #needed parameters from the potential and prototype
    ucell = proto.get('ucell')          
    units = pot.get('units')
    pair_info = pot.coeff(elements)
    atom_style = pot.get('atom_style')
    
    for cycle in xrange(100):
        #Run LAMMPS Cij script using guess alat0
        f = open('cij.in','w')
        f.write(cij_script(pair_info, units, atom_style, masses, ucell, alat0))
        f.close()
        data = lmp.extract(subprocess.check_output(lammps_exe+' < cij.in',shell=True))
        
        #Extract system dimensions and stresses from LAMMPS data output
        for p in xrange(13):
            for i in xrange(6):
                dimensions[p, i] = float(data[p+1][i+1])
                stresses[p, i] = -float(data[p+1][i+10])*1e-4
        eps_scale = np.array([dimensions[0,0], dimensions[0,1], dimensions[0,2], 
                              dimensions[0,2], dimensions[0,2], dimensions[0,1]])

        #Calculate Cij from dimensions and pressures
        cij = np.empty((6,6))
        for i in xrange(0,6):
            eps_ij = (dimensions[2*i+2, i] - dimensions[2*i+1, i]) / eps_scale[i]
            for j in xrange(0,6):
                sig_ij = stresses[2*i+2, j] - stresses[2*i+1, j]
                cij[j,i] = sig_ij/eps_ij
        
        #Invert Cij to Sij and compute new guess alat1
        S = np.linalg.inv(cij)
        for i in xrange(3):
            alat1[i] = (dimensions[0,i] / 
                        (S[i,0] * stresses[0,0] + 
                         S[i,1] * stresses[0,1] + 
                         S[i,2] * stresses[0,2] + 1)) / size[i]

        #Test if values have converged to one value
        if np.allclose(alat0, alat1, rtol=0, atol=1e-13):
            converged = True
            break
            
        #Test if values have diverged from initial guess
        elif (alat1[0] < alat_init[0] / 5. or alat1[0] > alat_init[0] * 5. or
              alat1[1] < alat_init[1] / 5. or alat1[1] > alat_init[0] * 5. or
              alat1[2] < alat_init[2] / 5. or alat1[2] > alat_init[0] * 5.):
            break
            
        #Test if values have converged to two values 
        elif np.allclose(alat_neg1, alat1, rtol=0, atol=1e-13):
            
            #Run LAMMPS Cij script using average between alat0 and alat1
            for i in xrange(3):
                alat0[i] = (alat1[i] + alat0[i])/2.
            f = open('cij.in','w')
            f.write(cij_script(pair_info, units, atom_style, masses, ucell, alat0))
            f.close()
            data = lmp.extract(subprocess.check_output(lammps_exe+' < cij.in',shell=True))
            
            #Extract system dimensions and pressures from LAMMPS data output
            for p in xrange(13):
                for i in xrange(6):
                    dimensions[p, i] = float(data[p+1][i+1])
                    stresses[p, i] = -float(data[p+1][i+10])*1e-4
            eps_scale = np.array([dimensions[0,0], dimensions[0,1], dimensions[0,2], 
                                  dimensions[0,2], dimensions[0,2], dimensions[0,1]])

            #Calculate Cij from LAMMPS results
            cij = np.empty((6,6))
            for i in xrange(0,6):
                eps_ij = (dimensions[2*i+2, i] - dimensions[2*i+1, i]) / eps_scale[i]  
                for j in xrange(0,6):
                    sig_ij = stresses[2*i+2, j] - stresses[2*i+1, j]
                    cij[j,i] = sig_ij/eps_ij
            print 'yes'
            converged = True
            break
            
        #if not converged or diverged, shift alat1 -> alat0 -> alat_neg1
        else:
            for i in xrange(3):
                alat_neg1[i] = alat0[i]
                alat0[i] = alat1[i]
    
    #Return values if converged
    if converged:        
        ecoh = float(data[1][16])
        return {'alat':alat0, 'ecoh':ecoh, 'cij':cij}
    else:
        return None 