#!/usr/bin/env python
import os
import sys
import random
import matplotlib.pyplot as plt
import numpy as np
import uuid
from copy import deepcopy

import iprPy
from DataModelDict import DataModelDict as DM
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):    
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = iprPy.calculation_read_input(__calc_type__, f, *args[1:])
       
    #read in potential
    potential = lmp.Potential(input_dict['potential'], input_dict['potential_dir'])        
    
    #Unscale vector parameters relative to ucell
    for params in input_dict['point_defect_model'].iterfinds('atomman-defect-point-parameters'):
        if 'scale' in params and params['scale'] is True:
            if 'pos' in params:
                params['pos'] = list(input_dict['ucell'].unscale(params['pos']))
            if 'db_vect' in params:
                params['db_vect'] = list(input_dict['ucell'].unscale(params['db_vect']))
            params['scale'] = False
        
    #Run quick_a_Cij to refine values
    results_dict = ptd_energy(input_dict['lammps_command'],
                              input_dict['initial_system'], 
                              potential, 
                              input_dict['symbols'], 
                              input_dict['point_defect_model'],
                              mpi_command = input_dict['mpi_command'],
                              etol =        input_dict['energy_tolerance'], 
                              ftol =        input_dict['force_tolerance'], 
                              maxiter =     input_dict['maximum_iterations'],
                              maxeval =     input_dict['maximum_evaluations'])
    
    check_config('ptd.dump', input_dict['point_defect_model'], 1.05*input_dict['ucell'].box.a, results_dict)
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def ptd_energy(lammps_command, system, potential, symbols, ptd, mpi_command='',
               etol=0.0, ftol=1e-6, maxiter=100000, maxeval=100000):
    
    pair_info = potential.pair_info(symbols)
        
    #write system to data file
    system_info = lmp.atom_data.dump('perfect.dat', system, 
                                     units=potential.units, 
                                     atom_style=potential.atom_style)

    #create LAMMPS input script
    min_in = min_script('min.template', system_info, pair_info, etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval)
    with open('perfect_min.in', 'w') as f:
        f.write(min_in)

    #run lammps
    data = lmp.run(lammps_command, 'perfect_min.in', mpi_command)

    #extract cohesive energy
    e_coh = uc.set_in_units(data.finds('peatom')[-1], 
                            lmp.style.unit(potential.units)['energy'])
    
    #Rename final dump file
    try:
        os.rename('atom.'+str(int(data.finds('Step')[-1])), 'perfect.dump')
    except:
        os.remove('perfect.dump')
        os.rename('atom.'+str(int(data.finds('Step')[-1])), 'perfect.dump')
    
    #add defect(s) to system
    system = lmp.atom_dump.load('perfect.dump')    
    for params in ptd.iterfinds('atomman-defect-point-parameters'):       
        system = am.defect.point(system, **params)
        
    #write system to data file
    system_info = lmp.atom_data.dump('ptd.dat', system, 
                                     units=potential.units, 
                                     atom_style=potential.atom_style)
    
    #create LAMMPS input script
    min_in = min_script('min.template', system_info, pair_info, etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval)
    with open('ptd_min.in', 'w') as f:
        f.write(min_in)

    #run lammps
    data = lmp.run(lammps_command, 'ptd_min.in', mpi_command)

    #extract per-atom energy and caclulate formation energy
    d_pot_eng = uc.set_in_units(data.finds('PotEng')[-1], 
                                lmp.style.unit(potential.units)['energy'])
    e_ptd_f = d_pot_eng - e_coh * system.natoms
    
    #rename final dump file
    try:
        os.rename('atom.'+str(int(data.finds('Step')[-1])), 'ptd.dump')
    except:
        os.remove('ptd.dump')
        os.rename('atom.'+str(int(data.finds('Step')[-1])), 'ptd.dump')
    
    os.remove('atom.0')
    
    return {'e_coh':e_coh, 'e_ptd_f': e_ptd_f}

def check_config(dump_file, ptd, cutoff, results_dict={}):
    #Extract the parameter sets
    params = ptd.finds('atomman-defect-point-parameters')
    
    #if there is only one set, use that set
    if len(params) == 1:
        params = params[0]
    #if there are two sets (divacancy), average the positions
    elif len(params) == 2:
        di_pos = (np.array(params[0]['pos']) + np.array(params[1]['pos'])) / 2
        params = params[0]
        params['pos'] = di_pos
    
    pos = params['pos']
    
    system = lmp.atom_dump.load(dump_file)
    
    #Compute centrosummation of atoms near defect.
    #Calculate distance of all atoms from pos
    pos_vects = system.dvect(system.atoms.view['pos'], pos) 
    
    #Identify all atoms close to pos
    pos_mags = np.linalg.norm(pos_vects, axis=1)
    index = np.where(pos_mags < cutoff)
    
    #sum up the positions of the close atoms
    results_dict['centrosummation'] = np.sum(pos_vects[index], axis=0)
    
    results_dict['has_reconfigured'] = False
    if not np.allclose(results_dict['centrosummation'], np.zeros(3), atol=1e-5):
        results_dict['has_reconfigured'] = True
        
    #Calculate shift of defect atom's position if interstitial or substitutional
    if params['ptd_type'] == 'i' or params['ptd_type'] == 's':
        new_pos = system.atoms_prop(a_id=system.natoms-1, key='pos')
        results_dict['position_shift'] = pos - new_pos
       
        if not np.allclose(results_dict['position_shift'], np.zeros(3), atol=1e-5):
            results_dict['has_reconfigured'] = True
        
    #Investigate if dumbbell vector has shifted direction 
    elif params['ptd_type'] == 'db':
        db_vect = params['db_vect'] / np.linalg.norm(params['db_vect'])
        new_pos1 = system.atoms_prop(a_id=system.natoms-1, key='pos')
        new_pos2 = system.atoms_prop(a_id=system.natoms-2, key='pos')
        new_db_vect = (new_pos1 - new_pos2) / np.linalg.norm(new_pos1 - new_pos2)
        results_dict['db_vect_shift'] = db_vect - new_db_vect
        
        if not np.allclose(results_dict['db_vect_shift'], np.zeros(3), atol=1e-5):
            results_dict['has_reconfigured'] = True
    
    return results_dict

def min_script(template_file, system_info, pair_info, etol = 0.0, ftol = 1e-6, maxiter = 100000, maxeval = 100000):
    """Create lammps script for performing a simple energy minimization."""    
    
    with open(template_file) as f:
        template = f.read()
    variable = {'atomman_system_info': system_info,
                'atomman_pair_info':   pair_info,
                'energy_tolerance': etol, 
                'force_tolerance': ftol,
                'maximum_iterations': maxiter,
                'maximum_evaluations': maxeval}
    return '\n'.join(iprPy.tools.fill_template(template, variable, '<', '>'))
        
if __name__ == '__main__':
    main(*sys.argv[1:])    