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
    
    #Run quick_a_Cij to refine values
    if input_dict['temperature'] != 0.0:
                results_dict = equilibrum(input_dict['lammps_command'],
                              input_dict['initial_system'], 
                              potential, 
                              input_dict['symbols'],
                              mpi_command = input_dict['mpi_command'],
                              t_steps =     input_dict['thermo_steps'], 
                              press =       input_dict['pressure'], 
                              d_every =     input_dict['dump_every'],
                              r_steps =     input_dict['run_steps'],
                              rand =     	input_dict['random_seed'],
                              temp =     	input_dict['temperature'])
    else:
                results_dict = equilibrum(input_dict['lammps_command'],
                              input_dict['initial_system'], 
                              potential, 
                              input_dict['symbols'],
                              mpi_command = input_dict['mpi_command'],
                              t_steps =     input_dict['thermo_steps'], 
                              press =       input_dict['pressure'], 
                              d_every =     input_dict['dump_every'],
                              r_steps =     input_dict['run_steps'],
                              rand =     	input_dict['random_seed'])
    

    

    thermo_data = results_dict.find('thermo')
    total_step = np.array(thermo_data['Step'])
    total_val = np.array(thermo_data['Temp'])
    
    eq_val = find_equilibrium(total_val)
    results_dict['equilibrium_temperature'] = eq_val

    eq_time = find_time_of_equilibrium(total_val)
    results_dict['time-to-equilibrium'] = eq_time
    
    plt.plot(total_step,total_val)
    plt.plot([eq_time],[eq_val],'ro')
    plt.savefig('temperature.png')
    plt.close()
    plt.show()
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=2)

def equilibrum(lammps_command, system, potential, symbols, mpi_command='',
               t_steps=1000, press=0.0, d_every=100000, r_steps=100000, rand = 1734812, temp = 0):
    
    pair_info = potential.pair_info(symbols)
        
    #write system to data file
    system_info = lmp.atom_data.dump('perfect.dat', system, 
                                     units=potential.units, 
                                     atom_style=potential.atom_style)

    #create LAMMPS input script
    if temp == 0.0:
	            min_in = min_script('min_zero_temp.template', system_info, pair_info, t_steps=t_steps, press=press, d_every=d_every, r_steps=r_steps, rand=rand)
	            with open('perfect_min.in', 'w') as f:
	                        f.write(min_in)
    else:
	            min_in = min_script_temp('min_nonzero_temp.template', system_info, pair_info, t_steps=t_steps, press=press, d_every=d_every, r_steps=r_steps, rand=rand,temp=temp)
	            with open('perfect_min.in', 'w') as f:
	                        f.write(min_in)

    #run lammps
    data = lmp.run(lammps_command, 'perfect_min.in', mpi_command)
    
    return data
    
    #create json of data
    with open('log.lammps') as f:
	    json_data = lmp.log_extract(f)
	#create data file with temperature
    with open('results_run.dat', 'w') as f:
	    json.dump(json_data,f)
	    
    
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
    
    #Compute centrosummation of atoms near defect.0
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
    
def min_script(template_file, system_info, pair_info, t_steps = 0.0, press = 0.0, d_every = 100000, r_steps = 100000, rand = 1734812):
    """Create lammps script for performing a simple energy minimization."""    
    
    with open(template_file) as f:
        template = f.read()
    variable = {'atomman_system_info': system_info,
                'atomman_pair_info':   pair_info,
                'thermo_steps': t_steps, 
                'pressure': press,
                'dump_every': d_every,
                'run_steps': r_steps,
                'random_seed': rand}
    return '\n'.join(iprPy.tools.fill_template(template, variable, '<', '>'))
        
def min_script_temp(template_file, system_info, pair_info, t_steps = 0.0, press = 0.0, d_every = 100000, r_steps = 100000, rand = 1734812, temp = 0):
    """Create lammps script for performing a simple energy minimization."""    
    
    with open(template_file) as f:
        template = f.read()
    variable = {'atomman_system_info': system_info,
                'atomman_pair_info':   pair_info,
                'thermo_steps': t_steps, 
                'pressure': press,
                'dump_every': d_every,
                'run_steps': r_steps,
                'random_seed': rand,
                'temperature': temp}
    return '\n'.join(iprPy.tools.fill_template(template, variable, '<', '>'))
    
def split_list(a_list):
    half = len(a_list)/2
    if len(a_list[:half]) != len(a_list[half:]):
        return a_list[:half], a_list[half:len(a_list)-1]
    else:
        return a_list[:half], a_list[half:]
        
# finds the equilibrium value by splitting data in half and fining averages of the halves, the spliting again
def find_equilibrium(data, increment = 100, index = 0):
    
    data_one, data_two = split_list(data[index:])
    
    f_half_ave = np.average(data_one)
    f_half_std = np.std(data_one)
    s_half_ave = np.average(data_two)
    s_half_std = np.std(data_two)
    
    if (f_half_ave > s_half_ave):
    
        if (len(data_one) < increment):
            return np.average([f_half_ave, s_half_ave])
        else:
            index = index + increment
            #recursive
            return find_equilibrium(data, index = index)
        
    return np.average([f_half_ave, s_half_ave])

#finds time of equilibrium
def find_time_of_equilibrium(data, increment = 100, index = 0):
    data_one, data_two = split_list(data[index:])
    
    f_half_ave = np.average(data_one)
    f_half_std = np.std(data_one)
    s_half_ave = np.average(data_two)
    s_half_std = np.std(data_two)
    
    if (f_half_std > s_half_std):
    
        if (len(data_one) < increment):
            return index
        else:
            index = index + increment
            return find_time_of_equilibrium(data, index = index)
    return index


if __name__ == '__main__':
    main(*sys.argv[1:])  

