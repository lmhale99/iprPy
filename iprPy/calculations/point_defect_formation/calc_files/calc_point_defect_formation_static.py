#!/usr/bin/env python
import os
import sys
import random
import glob
import matplotlib.pyplot as plt
import numpy as np
import uuid
from copy import deepcopy
import shutil

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
        
    #Run ptd_energy to refine values
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
    
    #Clear atom.* files and save dump files of relaxed systems
    for fname in glob.iglob(os.path.join(os.getcwd(), 'atom.*')):
        os.remove(fname)
    lmp.atom_dump.dump(results_dict['system_base'], 'perfect.dump')
    lmp.atom_dump.dump(results_dict['system_ptd'],  'defect.dump')
    
    #Run check_ptd_config
    cutoff = 1.05*input_dict['ucell'].box.a
    config_dict = check_ptd_config(results_dict['system_ptd'], 
                                   input_dict['point_defect_model'], 
                                   cutoff)
    
    #Copy and fill in results_dict
    results_dict['dump_file_base'] = 'perfect.dump'
    results_dict['dump_file_ptd'] = 'defect.dump'    
    for key, value in config_dict.iteritems():
        results_dict[key] = value
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def ptd_energy(lammps_command, system, potential, symbols, ptd_model, mpi_command=None,
               etol=0.0, ftol=1e-6, maxiter=100000, maxeval=100000):
    """
    Adds one or more point defects to a system and evaluates the defect formation energy.
    
    Arguments:
    lammps_command -- command for running LAMMPS.
    system -- atomman.System to add the point defect to.
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential.
    symbols -- list of element-model symbols for the Potential that correspond to system's atypes.
    ptd_model -- DataModelDict representation of a point defect data model.
    
    Keyword Arguments:
    mpi_command -- MPI command for running LAMMPS in parallel. Default value is None (serial run).  
    etol -- energy tolerance to use for the LAMMPS minimization. Default value is 0.0 (i.e. only uses ftol). 
    ftol -- force tolerance to use for the LAMMPS minimization. Default value is 1e-6.
    maxiter -- the maximum number of iterations for the LAMMPS minimization. Default value is 100000.
    maxeval -- the maximum number of evaluations for the LAMMPS minimization. Default value is 100000.    
    """
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Read LAMMPS input template
    with open('min.template') as f:
        template = f.read()
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'perfect.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['energy_tolerance'] =    etol
    lammps_variables['force_tolerance'] =     uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maximum_iterations'] =  maxiter
    lammps_variables['maximum_evaluations'] = maxeval

    #Write lammps input script
    with open('min.in', 'w') as f:
        f.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))

    #run lammps to relax perfect.dat
    output = lmp.run(lammps_command, 'min.in', mpi_command)
    
    #Extract LAMMPS thermo data.
    E_total_base = uc.set_in_units(output.finds('PotEng')[-1], lammps_units['energy'])
    E_coh =        uc.set_in_units(output.finds('peatom')[-1], lammps_units['energy'])
    
    #rename log file
    shutil.move('log.lammps', 'min-perfect-log.lammps')
    
    #Load relaxed system from dump file and copy old vects as dump files crop values
    last_dump_file = 'atom.'+str(int(output.finds('Step')[-1]))
    system_base = lmp.atom_dump.load(last_dump_file)
    system_base.box_set(vects=system.box.vects)
    
    #Add defect(s)
    system_ptd = deepcopy(system_base)
    for params in ptd_model.iterfinds('atomman-defect-point-parameters'):       
        system_ptd = am.defect.point(system_ptd, **params)
    
    #update lammps variables
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system_ptd, 'defect.dat',
                                                                 units = potential.units, 
                                                                 atom_style = potential.atom_style)
    
    #Write lammps input script
    with open('min.in', 'w') as f:
        f.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))

    #run lammps
    output = lmp.run(lammps_command, 'min.in', mpi_command)
    
    #extract lammps thermo data
    E_total_ptd = uc.set_in_units(output.finds('PotEng')[-1], lammps_units['energy'])
    
    #rename log file
    shutil.move('log.lammps', 'min-defect-log.lammps')    
    
    #Load relaxed system from dump file and copy old vects as dump files crop values
    last_dump_file = 'atom.'+str(int(output.finds('Step')[-1]))
    system_ptd = lmp.atom_dump.load(last_dump_file)
    system_ptd.box_set(vects=system.box.vects)
    
    #compute defect formation energy as difference between total potential energy of defect system
    #and the cohesive energy of the perfect system times the number of atoms in the defect system
    E_ptd_f = E_total_ptd - E_coh * system_ptd.natoms
    
    return {'E_coh':       E_coh,        'E_ptd_f':    E_ptd_f, 
            'E_total_base':E_total_base, 'E_total_ptd':E_total_ptd,
            'system_base': system_base,  'system_ptd': system_ptd}

def check_ptd_config(system, ptd_model, cutoff, tol=1e-5):
    """
    Evaluates a relaxed system containing a point defect to determine if the defect 
    structure has transformed to a different configuration.
    
    Arguments:
    system -- atomman.System containing the point defect(s)
    ptd_model -- DataModelDict representation of a point defect data model
    cutoff -- cutoff to use for identifying atoms nearest to the defect's position
    
    Keyword Argument:
    tol -- tolerance to use for identifying if a defect has reconfigured. Default value is 1e-5.
    """
    
    #Extract the parameter sets
    params = deepcopy(ptd_model.finds('atomman-defect-point-parameters'))
    
    #if there is only one set, use that set
    if len(params) == 1:
        params = params[0]
        
    #if there are two sets (divacancy), use the first and average position
    elif len(params) == 2:
        di_pos = (np.array(params[0]['pos']) + np.array(params[1]['pos'])) / 2
        params = params[0]
        params['pos'] = di_pos
    
    #More than two not supported by this function
    else:
        raise ValueError('Invalid point defect parameters')
    
    #Initially set has_reconfigured to False
    has_reconfigured = False
    
    #Calculate distance of all atoms from defect position
    pos_vects = system.dvect(system.atoms.view['pos'], params['pos']) 
    pos_mags = np.linalg.norm(pos_vects, axis=1)
    
    #calculate centrosummation by summing up the positions of the close atoms
    centrosummation = np.sum(pos_vects[pos_mags < cutoff], axis=0)
    
    if not np.allclose(centrosummation, np.zeros(3), atol=tol):
        has_reconfigured = True
        
    #Calculate shift of defect atom's position if interstitial or substitutional
    if params['ptd_type'] == 'i' or params['ptd_type'] == 's':
        position_shift = system.dvect(system.natoms-1, params['pos'])
       
        if not np.allclose(position_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
        
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation, 
                'position_shift':   position_shift}
        
    #Investigate if dumbbell vector has shifted direction 
    elif params['ptd_type'] == 'db':
        db_vect = params['db_vect'] / np.linalg.norm(params['db_vect'])
        new_db_vect = system.dvect(system.natoms-2, system.natoms-1)
        new_db_vect = new_db_vect / np.linalg.norm(new_db_vect)
        db_vect_shift = db_vect - new_db_vect
        
        if not np.allclose(db_vect_shift, np.zeros(3), atol=tol):
            has_reconfigured = True
    
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation, 
                'db_vect_shift':    db_vect_shift}   
    
    else:
        return {'has_reconfigured': has_reconfigured, 
                'centrosummation':  centrosummation}
        
if __name__ == '__main__':
    main(*sys.argv[1:])    