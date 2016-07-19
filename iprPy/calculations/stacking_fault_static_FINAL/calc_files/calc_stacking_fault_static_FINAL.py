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
from atomman import Atoms, Box, System

__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = iprPy.calculation_read_input(__calc_type__, f)
        
    results_dict = sf_return_results(input_dict,__calc_type__)
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp = f, indent = 2)
    
    
def sf_relax_script(template_file, system_info, pair_info, etol = 0.0, ftol = 1e-6, maxiter = 100000, maxeval = 100000, 
                    cutting_axis = 'z', relax_params_in = '0.0 0.0 NULL'):
    """Create lammps script for performing a simple energy minimization."""    
    
    with open(template_file) as f:
        template = f.read()
    variable = {'atomman_system_info': system_info,
                'atomman_pair_info':   pair_info,
                'energy_tolerance': etol, 
                'force_tolerance': ftol,
                'maximum_iterations': maxiter,
                'maximum_evaluations': maxeval,
                'cutting_axis': cutting_axis,
                'relax_params': relax_params_in
               }
    return '\n'.join(iprPy.tools.fill_template(template, variable, '<', '>'))



def sf_run_calcs(input_dict, __calc_type__, step):  
    """This calculation takes atomic positions for an already-rotated and supersized system and applies the necessary shift to 
    calculate the stacking fault energy. The code first sets up the system depending on the step, performs the calculation, and
    returns both the area and the cohesive energy of the system for that step."""
    
    #----------PULL INFO FROM STACKING FAULT MODEL-----------
    #searches within stacking_fault_model for the string 'atomman-defect-stacking_fault-parameters'
    sf_params = input_dict['stacking_fault_model'].find('atomman-generalized-fault-parameters')
    
    cutting_axis = sf_params['cutting-axis']
    
    #--------------------------CHECKS------------------------
    #CHECK: make sure that the cutting axis definition matches up with the shift values
    if cutting_axis == 'z':
        assert int(input_dict['stacking_fault_shift_amount'].split()[2]) == 0, "Ensure that the z-coordinate in <stacking_fault_shift_amount> = 0!"
    elif cutting_axis == 'y':
        assert int(input_dict['stacking_fault_shift_amount'].split()[1]) == 0, "Ensure that the y-coordinate in <stacking_fault_shift_amount> = 0!"
    elif cutting_axis == 'x':
        assert int(input_dict['stacking_fault_shift_amount'].split()[0]) == 0, "Ensure that the x-coordinate in <stacking_fault_shift_amount> = 0!"
    
    #CHECK: cutting_plane_location value is a fraction of the entire supercell
    assert 0 < float(sf_params['cutting-plane-location']) < 1, 'cutting-plane-location must be a value between 0 and 1!'
        
    #-------------------SETS UP THE SYSTEM--------------------   
    #pulls the axes for rotation as they were defined in stacking_fault_model
    axes = np.array([sf_params['crystallographic-axes']['x-axis'],
            sf_params['crystallographic-axes']['y-axis'],
            sf_params['crystallographic-axes']['z-axis']])
    
    #Read in potential
    potential = lmp.Potential(input_dict['potential'], input_dict['potential_dir']) #reads the potential filename
    system = input_dict['initial_system']

    #change boundary condition and relaxation parameters depending on the step
    if step == 'change_bc' or step == 'shift':
        if cutting_axis == 'z':
            x_bool = True #periodic
            y_bool = True #periodic
            z_bool = False #free surface
            axis_1 = 'x-axis' 
            axis_2 = 'y-axis'
            relax_params = '0.0 0.0 NULL' #allow relaxation in direction of cutting axis
            period_dict = {'axis_1': abs(input_dict['size_mults'][0][0]-input_dict['size_mults'][0][1]), #get system multiplier in axis_1 direction
                           'axis_2': abs(input_dict['size_mults'][1][0]-input_dict['size_mults'][1][1])} #get system multiplier in axis_2 direction
                                                                                                         #to normalize
            
        elif cutting_axis == 'x':
            x_bool = False
            y_bool = True
            z_bool = True
            axis_1 = 'y-axis'
            axis_2 = 'z-axis'
            relax_params = 'NULL 0.0 0.0'
            period_dict = {'axis_1': abs(input_dict['size_mults'][1][0]-input_dict['size_mults'][1][1]), 
                           'axis_2': abs(input_dict['size_mults'][2][0]-input_dict['size_mults'][2][1])}
            
        elif cutting_axis == 'y':
            x_bool = True
            y_bool = False
            z_bool = True
            axis_1 = 'x-axis'
            axis_2 = 'z-axis'
            relax_params = '0.0 NULL 0.0'
            period_dict = {'axis_1': abs(input_dict['size_mults'][0][0]-input_dict['size_mults'][0][1]), 
                           'axis_2': abs(input_dict['size_mults'][2][0]-input_dict['size_mults'][2][1])}
            
        #set boundary conditions for both change_bc and shift steps
        system.pbc = [x_bool, y_bool, z_bool]

        #perform shifting if on the shift step
        if step == 'shift':
                                   
            #calculate periodicity along the 2 axis directions because one repeat unit can be periodic at the halfway point
            periodicity_1 = np.sum(np.absolute(sf_params['crystallographic-axes'][axis_1][:])) 
            periodicity_2 = np.sum(np.absolute(sf_params['crystallographic-axes'][axis_2][:]))
            
            if periodicity_1%2 == 0:
                shift_divisor_1 = 2*period_dict['axis_1']
            elif periodicity_1%2 == 1:
                shift_divisor_1 = period_dict['axis_1']
            
            if periodicity_2%2 == 0:
                shift_divisor_2 = 2*period_dict['axis_2']
            elif periodicity_2%2 == 1:
                shift_divisor_2 = period_dict['axis_2']
                            
            #store initial position
            pos = system.atoms_prop(key='pos')

            #define cutting plane at a user-specified fraction of the entire system and then shift initial positions as necessary
            if cutting_axis == 'z':                
                cutting_plane = ((system.box.zhi + system.box.zlo)*float(sf_params['cutting-plane-location']))
                pos[pos[:,2]>cutting_plane - 1e-9] += np.array([float(input_dict['stacking_fault_shift_amount'].split()[0])*system.box.a/shift_divisor_1, 
                                                    float(input_dict['stacking_fault_shift_amount'].split()[1])*system.box.b/shift_divisor_2, 0.0])
            elif cutting_axis == 'y':
                cutting_plane = ((system.box.yhi + system.box.ylo)*float(sf_params['cutting-plane-location']))
                pos[pos[:,1]>cutting_plane - 1e-9] += np.array([float(input_dict['stacking_fault_shift_amount'].split()[0])*system.box.a/shift_divisor_1, 0.0, 
                                                    float(input_dict['stacking_fault_shift_amount'].split()[2])*system.box.c/shift_divisor_2,])
            elif cutting_axis == 'x':
                cutting_plane = ((system.box.xhi + system.box.xlo)*float(sf_params['cutting-plane-location']))
                pos[pos[:,0]>cutting_plane - 1e-9] += np.array([0.0, float(input_dict['stacking_fault_shift_amount'].split()[1])*system.box.b/shift_divisor_1, 
                                                    float(input_dict['stacking_fault_shift_amount'].split()[2])*system.box.c/shift_divisor_2])
            #assign shifted values to the system
            system.atoms_prop(key='pos', value=pos)

    elif step == 'initial':
        system.pbc = [True, True, True]
        relax_params = 'NULL NULL NULL'
    
    #ensure all atoms are within the box
    system.wrap()
    
    #-------------------RUN LAMMPS AND SAVE RESULTS------------------
    #use above information to generate system_info and pair_info for LAMMPS
    system_info = am.lammps.atom_data.dump('stacking_fault.dat', system, units=potential.units, atom_style=potential.atom_style)
    pair_info = potential.pair_info(input_dict['symbols']) #pulls the potential info when given which element the calculation is running on

    #write the LAMMPS input script
    with open('stacking_fault.in', 'w') as f:
        f.write(sf_relax_script('min.template', system_info, pair_info, 
                                etol = input_dict['energy_tolerance'], 
                                ftol = input_dict['force_tolerance'], 
                                maxiter = input_dict['maximum_iterations'], 
                                maxeval = input_dict['maximum_evaluations'],
                                cutting_axis = cutting_axis,
                                relax_params_in = relax_params))
    
    #run LAMMPS
    output = lmp.run(input_dict['lammps_command'], 'stacking_fault.in', input_dict['mpi_command'])
    atom_last = 'atom.%i' % output.finds('Step')[-1] #prints number of iterations (?)
    
    #save results into results_dict
    if step == 'initial':
        try:
            os.rename(atom_last, 'initial.dump')
        except:
            os.remove('initial.dump')
            os.rename(atom_last, 'initial.dump')
        os.remove('atom.0')
        d_system = lmp.atom_dump.load('initial.dump')

    elif step == 'change_bc':
        try:
            os.rename(atom_last, 'surface.dump')
        except:
            os.remove('surface.dump')
            os.rename(atom_last, 'surface.dump')
        os.remove('atom.0')
        d_system = lmp.atom_dump.load('surface.dump')

    elif step == 'shift':
        try:
            os.rename(atom_last, 'gpfe.dump')
        except:
            os.remove('gpfe.dump')
            os.rename(atom_last, 'gpfe.dump')
        os.remove('atom.0')
        d_system = lmp.atom_dump.load('gpfe.dump')

    results_dict = {}
    results_dict['defect_system'] = d_system
    results_dict['potential_energy'] = float(output.finds('PotEng')[-1])
    
    #calculate area for output
    if cutting_axis == 'z':
        area = (system.box.xhi-system.box.xlo)*(system.box.yhi-system.box.ylo)
    elif cutting_axis == 'y':
        area = (system.box.xhi-system.box.xlo)*(system.box.zhi-system.box.zlo) 
    elif cutting_axis == 'x':
        area = (system.box.yhi-system.box.ylo)*(system.box.zhi-system.box.zlo)

    #return values
    return [results_dict['potential_energy'], area, system.natoms]

def sf_return_results(input_dict,__calc_type__):
    #initialize
    results_dict = {}
    
    #run for each step and store results
    initial_results = sf_run_calcs(input_dict, __calc_type__, 'initial') 
    change_bc_results = sf_run_calcs(input_dict, __calc_type__, 'change_bc')
    shift_results = sf_run_calcs(input_dict, __calc_type__, 'shift')
    
    #process results to return in the units of interest    
    results_dict['cohesive_energy'] = initial_results[0]/initial_results[2] #eV/atom
    results_dict['surface_energy'] = abs(initial_results[0]-change_bc_results[0])/(2*change_bc_results[1]) #eV/angstrom^2
    results_dict['fault_energy'] = abs(shift_results[0]-change_bc_results[0])/(2*shift_results[1]) #eV/angstrom^2
    
    
    
    return results_dict

if __name__ == '__main__':
    main(*sys.argv[1:])     
    
