#!/usr/bin/env python
import os
import sys
import random
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
    
    #Calculate the r/a ratio for the unit cell
    r_a = r_a_ratio(input_dict['ucell'])
    
    #Get ratios of lx, ly, and lz of inital_system relative to a
    lx_a = input_dict['initial_system'].box.a / input_dict['ucell'].box.a
    ly_a = input_dict['initial_system'].box.b / input_dict['ucell'].box.a
    lz_a = input_dict['initial_system'].box.c / input_dict['ucell'].box.a
    alpha = input_dict['initial_system'].box.alpha
    beta =  input_dict['initial_system'].box.beta
    gamma = input_dict['initial_system'].box.gamma
    
    #Create a copy of the initial system
    system = deepcopy(input_dict['initial_system'])
 
    #build lists of values
    results_dict = DM()
    results_dict['r_values'] = np.linspace(input_dict['minimum_r'], input_dict['maximum_r'], input_dict['number_of_steps_r'])
    results_dict['a_values'] = results_dict['r_values'] / r_a
    results_dict['Ecoh_values'] = np.empty(input_dict['number_of_steps_r'])
 
    #Loop over values
    for i in xrange(input_dict['number_of_steps_r']):
        
        #Rescale system's box
        a = results_dict['a_values'][i]
        system.box_set(a = a * lx_a, 
                       b = a * ly_a, 
                       c = a * lz_a, 
                       alpha=alpha, beta=beta, gamma=gamma, scale=True)
        
        #Get lammps units
        lammps_units = lmp.style.unit(potential.units)
        
        #Define lammps variables
        lammps_variables = {}
        lammps_variables['atomman_system_info'] = lmp.atom_data.dump('atom.dat', system, units=potential.units, atom_style=potential.atom_style)
        lammps_variables['atomman_pair_info'] = potential.pair_info(input_dict['symbols'])
        
        #Write lammps input script
        template_file = 'run0.template'
        lammps_script = 'run0.in'
        with open(template_file) as f:
            template = f.read()
        with open(lammps_script, 'w') as f:
            f.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))

        #Run lammps and extract data
        output = lmp.run(input_dict['lammps_command'], lammps_script, input_dict['mpi_command'])
        results_dict['Ecoh_values'][i] = uc.set_in_units(output.finds('peatom')[-1], lammps_units['energy'])
        shutil.move('log.lammps', 'run0-'+str(i)+'-log.lammps')
    
    #Find unit cell systems at the energy minimums
    for i in xrange(1, input_dict['number_of_steps_r'] - 1):
        if results_dict['Ecoh_values'][i] < results_dict['Ecoh_values'][i-1] and results_dict['Ecoh_values'][i] < results_dict['Ecoh_values'][i+1]:
            a = results_dict['a_values'][i]
            cell = deepcopy(input_dict['ucell'])
            cell.box_set(a = a,
                         b = a * input_dict['ucell'].box.b / input_dict['ucell'].box.a,
                         c = a * input_dict['ucell'].box.c / input_dict['ucell'].box.a, 
                         alpha=alpha, beta=beta, gamma=gamma, scale=True)
            results_dict.append('min_cell', cell)
        
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def r_a_ratio(ucell):
    """Calculates the shortest interatomic spacing, r, for a system wrt to box.a."""
    r_a = ucell.box.a
    for i in xrange(ucell.natoms):
        for j in xrange(i):
            dmag = np.linalg.norm(ucell.dvect(i,j))
            if dmag < r_a:
                r_a = dmag
    return r_a/ucell.box.a
    
if __name__ == '__main__':
    main(*sys.argv[1:])    