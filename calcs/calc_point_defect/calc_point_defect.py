#!/usr/bin/env python2.7

# Standard library imports
import os
import subprocess
#from multiprocessing import Pool
from copy import deepcopy
import sys
import tempfile
import json
from collections import OrderedDict
import uuid

#Additional imports
import numpy as np

#Custom imports
import atomman as am
from atomman.tools import mag

def min_script(system_info, pair_info, etol = 0, ftol = 1e-6, maxiter = 100000, maxeval = 100000):
    #Perform energy minimization on atoms in file read_data using potential information from all other parameters
    nl = '\n'
    script = nl.join([system_info,
                      '',
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
    
def point_defect_Ef(lammps_exe, ucell, potential, symbols, point_defect_params, min_size, max_size):
#Calculate the formation energy for a point defect
    
    if min_size%2 == 1 or max_size%2 == 1:
        raise ValueError('min_size and max_size must be even')
        
    #Parameter setup
    sizes =    range(min_size, max_size+2, 2)
    natoms =   np.zeros(len(sizes))
    energies = np.zeros(len(sizes))
    centro =   np.zeros((len(sizes),3))
    rcoord =   np.zeros((len(sizes),3))
    
    pair_info = potential.pair_info(symbols)
    
    if len(point_defect_params) == 1:
        shift = True
    else:
        shift = False
    
    #For all system sizes
    for i in xrange(len(sizes)):    
        #Construct perfect system
        h = sizes[i]/2
        system_info = am.lammps.sys_gen(units =       potential.units(),
                                        atom_style =  potential.atom_style(),
                                        ucell_box =   ucell.box(),
                                        ucell_atoms = ucell.atoms(scale=True),
                                        size =        np.array([[-h,h], [-h,h], [-h,h]], dtype=np.int) )
                                           
        
        
        with open('min.in','w') as script:
            script.write( min_script(system_info, pair_info) )
        data = am.lammps.log_extract(subprocess.check_output(lammps_exe + ' -in min.in', shell=True))
        
        sys0 = am.lammps.read_dump('atom.' + data[-1][0])
        pnatoms = sys0.natoms()
        ecoh = float(data[-1][4])
        
        #Construct defect system
        dsys = deepcopy(sys0)
        psys = None
        for params in point_defect_params:
            if params['pos'] is None:
                pos = ucell.unscale(np.array([0.1, 0.1, 0.1]))
            else:
                pos = ucell.unscale(params['pos'] + np.array([0.1, 0.1, 0.1]))
                
            if params['d'] is None:
                db_vect = None
            else:
                db_vect = ucell.unscale(params['d'])
                
            psys, dsys = dsys.pt_defect(ptdtype = params['ptdtype'], 
                                        atype =   params['atype'], 
                                        pos =     pos, 
                                        db_vect = db_vect,
                                        shift =   shift)                                        
            
        natoms[i] = dnatoms = dsys.natoms()
            
        #Run LAMMPS, record formation energy and obtain relaxed system
        system_info = am.lammps.write_data('def.dat', dsys)
        
        with open('min.in','w') as script:
            script.write( min_script(system_info, pair_info) )
        data = am.lammps.log_extract(subprocess.check_output(lammps_exe + ' -in min.in', shell=True))
        
        energies[i] = float(data[2][3]) - ecoh * dnatoms
        dsys_r = am.lammps.read_dump('atom.' + data[2][0])
        
        try:
            os.rename('atom.'+data[2][0], str(sizes[i]) + '.dump')
        except:
            os.remove(str(sizes[i]) + '.dump')
            os.rename('atom.'+data[2][0], str(sizes[i]) + '.dump')

        #Perform structure test calculations if only one defect was added
        if len(point_defect_params) == 1:

            #Compute centrosummation of atoms near defect. 
            nids = []
            for k in xrange(dnatoms):
                if k >= pnatoms:
                    nids.append(k)
                elif mag(psys.atoms(k, 'pos')) < ucell.box('a') * 1.05:
                    nids.append(k)

            #Sum up positions (using relaxed defect system) of selected atoms
            for k in nids:
                centro[i] += dsys_r.atoms(k, 'pos')
        
            #check position of interstitial and substitutional atoms after relaxing
            if ptd_params[0]['ptdtype'] == 'i' or ptd_params[0]['ptdtype'] == 's':
                last = dnatoms - 1
                rcoord[i] = dsys.dvect(last, dsys_r.atoms(last))
            #check dumbbell vector directions after relaxing   
            elif ptd_params[0]['ptdtype'] == 'db':
                last = dnatoms - 1
                dcheck = dsys_r.dvect(last, last-1)
                d_init = ptd_params[0]['d']
                rcoord1 = dcheck/mag(dcheck)
                rcoord2 = d_init/mag(d_init)
                rcoord[i] = rcoord1 - rcoord2
    
    return natoms, energies, centro, rcoord    


def read_input(fname):    
    with open(fname) as f:
        input_dict = {}
        for line in f:
            terms = line.split()
            if len(terms) == 0 or terms[0][0] == '#':
                pass
            elif len(terms) == 2:
                if terms[0] == 'number_of_processors':
                    input_dict['np'] = int(terms[1])
                elif terms[0] == 'lammps_exe':
                    input_dict['lammps_exe'] = terms[1]
                elif terms[0] == 'potential_file':
                    input_dict['potential_file'] = terms[1]
                elif terms[0] == 'potential_dir':
                    input_dict['potential_dir'] = terms[1]
                elif terms[0] == 'prototype_file':
                    input_dict['prototype_file'] = terms[1]
                elif terms[0] == 'phase_file':
                    input_dict['phase_file'] = terms[1]
                elif terms[0] == 'point_defect_file':
                    input_dict['point_defect_file'] = terms[1]
                elif terms[0] == 'point_defect_type':
                    input_dict['point_defect_type'] = terms[1]
                elif terms[0] == 'min_size':
                    input_dict['min_size'] = int(terms[1])
                elif terms[0] == 'max_size':
                    input_dict['max_size'] = int(terms[1])
                else:
                    raise ValueError('Invalid input file')
            else: 
                raise ValueError('Invalid input file')
    
    #test for values (and set defaults if needed)
    try:
        test = input_dict['np']
    except:
        input_dict['np'] = 1
    try:
        test = input_dict['lammps_exe']
    except:
        raise ValueError('lammps_exe not supplied')
    try:
        test = input_dict['potential_file']
    except:
        raise ValueError('potential_file not supplied')
    try:
        test = input_dict['potential_dir']
    except:
        input_dict['potential_dir'] = os.getcwd()
    try:
        test = input_dict['prototype_file']
    except:
        raise ValueError('prototype_file not supplied')
    try:
        test = input_dict['phase_file']
    except:
        raise ValueError('phase_file not supplied')
    try:
        test = input_dict['point_defect_file']
    except:
        raise ValueError('point_defect_file not supplied')
    try:
        test = input_dict['point_defect_type']
    except:
        raise ValueError('point_defect_type not supplied')
    try:
        test = input_dict['min_size']
    except:
        input_dict['min_size'] = 4
    try:
        test = input_dict['max_size']
    except:
        input_dict['max_size'] = 10

    return input_dict


    
    
    
if __name__ == '__main__':
    
    #Read in parameters from input file
    input_dict = read_input(sys.argv[1])
    
    #Read data model files
    potential = am.lammps.Potential(input_dict['potential_file'], input_dict['potential_dir'])
    prototype = am.tools.Prototype(input_dict['prototype_file'])
    phase = am.tools.CrystalPhase(input_dict['phase_file'])
    defects = am.tools.PointDefect(input_dict['point_defect_file'])
    
    #Set run parameters
    lammps_exe = input_dict['lammps_exe']
    min_size = input_dict['min_size']
    max_size = input_dict['max_size']
    
    alat = phase.get('alat')
    symbols = []
    for element in phase.get('elements'):
        symbols.append(element['element'])
    ucell = prototype.ucell(a=alat[0], b=alat[1], c=alat[2], alpha=90, beta=90, gamma=90)
    ptd_params = defects.get(input_dict['point_defect_type'], 'parameters')
    ptd_name = defects.get(input_dict['point_defect_type'], 'name')
    ptd_tag = defects.get(input_dict['point_defect_type'], 'tag')
    starting_dir = os.getcwd()
    
    #Create and move to temporary directory    
    temp_dir = tempfile.mkdtemp(dir=starting_dir)
    os.chdir(temp_dir)
    
    natoms, energies, centro, rcoord = point_defect_Ef(lammps_exe, ucell, potential, symbols, ptd_params, min_size, max_size)
    
    fheader = 'ptd--' + str(potential) + '--' + prototype.get('tag') + '-'
    for symbol in symbols:
        fheader += '-' + symbol
    fheader += '--' + ptd_tag
    
    #Copy dump files out of temp folder and delete temp folder
    os.chdir(starting_dir)
    for fname in os.listdir(temp_dir):
        if fname[-5:] == '.dump':
            try:
                os.rename(os.path.join(temp_dir,fname), fheader+'--'+fname)
            except:
                os.remove(fheader+'--'+fname)
                os.rename(os.path.join(temp_dir,fname), fheader+'--'+fname)
        else:
            os.remove(os.path.join(temp_dir,fname))
    os.rmdir(temp_dir)
    
    #Make list of energies for stable defect systems
    invatoms_list = []
    energies_list = []
    for i in xrange(len(natoms)): 
        if (np.allclose(centro[i], np.zeros(3), rtol=0, atol=1e-3) and
            np.allclose(rcoord[i], np.zeros(3), rtol=0, atol=1e-3)):
            invatoms_list.append(1./natoms[i])
            energies_list.append(energies[i])
            
    #If no stable energies found
    if len(energies_list)==0:
        defect_energy = 'Unstable'
    #If stable energies found
    else:
        xlist = np.linspace(0,max(invatoms_list))
        defect_energy = energies_list[0]
        if len(energies_list)==2:
            m1,b = np.polyfit(invatoms_list, energies_list, 1)
            defect_energy = b
        elif len(energies_list)>2:
            m2,m1,b = np.polyfit(invatoms_list, energies_list, 2)
            defect_energy = b
    
    #Create and write data model
    json_data = OrderedDict()
    json_data['calculationPointDefects'] = calc = OrderedDict()
    calc['calculationID'] = str(uuid.uuid4())
    calc['potentialID'] = OrderedDict()
    calc['potentialID']['descriptionIdentifier'] = str(potential)
        
    calc['simulation'] = sim = OrderedDict()
        
    #Copy substance information from crystal phase calculation
    sim['substance'] = phase.get()['calculationCrystalPhase']['simulation']['substance']
                    
    #Add prototype name
    sim['crystalPrototype'] = prototype.get('tag')
    
    #Add defect name
    sim['pointDefectID'] = OrderedDict()
    sim['pointDefectID']['pointDefectName'] = ptd_name
    sim['pointDefectID']['pointDefectTag'] = ptd_tag
    
    #Add extrapolated value
    sim['formationEnergy'] = OrderedDict([( 'value', defect_energy),
                                          ( 'unit',  'eV')       ])
    
    #Add calculation points
    sim['formationEnergyRelation'] = OrderedDict([('point', [] )])
    for i in xrange(len(energies)):
        point = OrderedDict()
        point['formationEnergy'] = OrderedDict([( 'value', energies[i]),
                                                ( 'unit',  'eV')        ])
        point['centrosummation'] = [float('%.3f'%centro[i][0]),
                                    float('%.3f'%centro[i][1]),
                                    float('%.3f'%centro[i][2])]
        point['coordRelaxation'] = [float('%.3f'%rcoord[i][0]),
                                    float('%.3f'%rcoord[i][1]),
                                    float('%.3f'%rcoord[i][2])]
        sim['formationEnergyRelation']['point'].append(point)
                                    

    with open(fheader+'.json', 'w') as f:
        f.write(json.dumps( json_data, indent = 4, separators = (',',': ') ))
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    