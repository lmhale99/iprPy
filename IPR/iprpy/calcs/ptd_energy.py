import os
import iprp
import iprp.lammps as lmp
import numpy as np
from copy import deepcopy
import subprocess
from scripts import min_script

#Compute the energies associated with point defects for different system sizes   
def ptd_energy(lammps_exe, pot, elements, masses, proto, alat, ptd_params, output_dir=None, ptd_tag=None, min_size=4, max_size=10):         
    if min_size%2 == 1 or max_size%2 == 1:
        raise ValueError('min_size and max_size must be even')
        
    #Parameter setup
    sizes =    range(min_size, max_size+2, 2)
    natoms =   np.zeros(len(sizes))
    energies = np.zeros(len(sizes))
    centro =   np.zeros((len(sizes),3))
    rcoord =   np.zeros((len(sizes),3))
    atomtypes = []
    for i in xrange(len(elements)):
        atomtypes.append(iprp.AtomType(elements[i],masses[i]))
    pbc = [True, True, True]
    
    ucell = proto.get('ucell')
    units = pot.get('units')
    pair_info = pot.coeff(elements)
    atom_style = pot.get('atom_style')
    
    if output_dir != None:
        out_file = proto.get('tag') + '-'
        for element in elements:
            out_file += '-' + element
        if ptd_tag != None:    
            out_file += '--' + ptd_tag    
    
    #For all system sizes
    for i in xrange(len(sizes)):    
        #Construct perfect system
        h = sizes[i]/2
        size = np.array([[-h,h], [-h,h], [-h,h]], dtype=np.int) 
        
        sys0 = lmp.create_sys(lammps_exe, atomtypes, pbc, alat=alat, ucell=ucell, size=size)
        pnatoms = len(sys0.atoms)
        lmp.write_atom('sys0.dat',sys0)

        #Run LAMMPS and record cohesive energy of perfect system
        with open('min.in','w') as script:
            script.write(min_script(pair_info, units, atom_style, masses, 'sys0.dat'))
        data = lmp.extract(subprocess.check_output(lammps_exe + ' < min.in', shell=True))
        ecoh = float(data[2][4])
        
        #Construct defect system
        dsys = deepcopy(sys0)
        for params in ptd_params:
            psys, dsys = dsys.pt_defect(ptdtype=params['ptdtype'], 
                                        atype=params['type'], 
                                        pos=alat*params['pos'], 
                                        d=alat*params['d'], 
                                        shift=True)
            
        lmp.write_atom('def.dat',dsys)
        natoms[i] = dnatoms = len(dsys.atoms)
            
        #Run LAMMPS, record formation energy and obtain relaxed system
        with open('min.in','w') as script:
            script.write(min_script(pair_info, units, atom_style, masses, 'def.dat'))
        data = lmp.extract(subprocess.check_output(lammps_exe + ' < min.in', shell=True))
        energies[i] = float(data[2][3]) - ecoh * dnatoms
        dsys_r = lmp.read_dump('atom.'+data[2][0], atomtypes)
        
        if output_dir != None:
            atomfile = out_file + '--' + str(sizes[i]) + '.dump'
            lmp.write_dump(os.path.join(output_dir,atomfile), dsys_r)          

        #Perform structure test calculations if only one defect was added
        if len(ptd_params) == 1:
            
            #Compute centrosymmetry of atoms near defect. 
            nids = []
            for k in xrange(dnatoms):
                if k >= pnatoms:
                    nids.append(k)
                elif (psys.atoms[k].get('x')**2 + 
                      psys.atoms[k].get('y')**2 + 
                      psys.atoms[k].get('z')**2) **.5 < alat[0] * 1.05:
                    nids.append(k)
            #Sum up positions (using relaxed defect system) of selected atoms
            for k in nids:
                centro[i] += dsys_r.atoms[k].get('pos')
        
            #check position of interstitial and substitutional atoms after relaxing
            if ptd_params[0]['ptdtype'] == 'i' or ptd_params[0]['ptdtype'] == 's':
                rcoord1 = dsys_r.atoms[-1].get('pos')
                rcoord2 = dsys.atoms[-1].get('pos')
                rcoord[i] = rcoord1 - rcoord2
            #check dumbbell vector directions after relaxing   
            elif ptd_params[0]['ptdtype'] == 'db':
                dcheck = dsys_r.atoms[-1].get('pos') - dsys_r.atoms[-2].get('pos')
                d_init = ptd_params[0]['d']
                rcoord1 = dcheck/(dcheck[0]**2+dcheck[1]**2+dcheck[2]**2)**0.5
                rcoord2 = d_init/(d_init[0]**2+d_init[1]**2+d_init[2]**2)**0.5
                rcoord[i] = rcoord1 - rcoord2
    
    return natoms, energies, centro, rcoord