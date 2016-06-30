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
from pymbar import testsystems
from pymbar import timeseries
import math

####
sys.path.insert(0, '/data/kas6/calculations')
import methods_equilibrium as me
####

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
    
    # equilibrium value
    eq_val = find_equilibrium(total_val)
    results_dict['equilibrium-temperature'] = eq_val

    # equilibrium time
    eq_time = find_equil_all_data(thermo_data)
    results_dict['time-to-equilibrium'] = eq_time
    eq_time = int(eq_time)
    
    # mean lattice parameters
    [a,b,c] = lattice_param(input_dict, thermo_data, eq_time)
    results_dict['mean-lattice-parameter'] = DM()
    results_dict['mean-lattice-parameter']['a'] = np.mean(a)
    results_dict['mean-lattice-parameter']['b'] = np.mean(b)
    results_dict['mean-lattice-parameter']['c'] = np.mean(c)
    
    # mean cohesive energy
    co_eng = cohesive_energy(np.array(thermo_data['PotEng']), eq_time, input_dict['initial_system'])
    results_dict['mean-cohesive-energy'] = np.mean(co_eng)
    
    # temperature pressures
    tmp = np.array(thermo_data['Temp'])[eq_time:]
    Pxx = np.array(thermo_data['Pxx'])[eq_time:]
    Pxy = np.array(thermo_data['Pxy'])[eq_time:]
    Pxz = np.array(thermo_data['Pxz'])[eq_time:]
    Pyy = np.array(thermo_data['Pyy'])[eq_time:]
    Pyz = np.array(thermo_data['Pyz'])[eq_time:]
    Pzz = np.array(thermo_data['Pzz'])[eq_time:]
    
    # mean temperature pressures
    results_dict['mean-temperature-pressure'] = DM()
    results_dict['mean-temperature-pressure']['temperature'] = np.mean(tmp)
    results_dict['mean-temperature-pressure']['pressure-xx'] = np.mean(Pxx)
    results_dict['mean-temperature-pressure']['pressure-xy'] = np.mean(Pxy)
    results_dict['mean-temperature-pressure']['pressure-xz'] = np.mean(Pxz)
    results_dict['mean-temperature-pressure']['pressure-yy'] = np.mean(Pyy)
    results_dict['mean-temperature-pressure']['pressure-yz'] = np.mean(Pyz)
    results_dict['mean-temperature-pressure']['pressure-zz'] = np.mean(Pzz)
    
    # standard_errors and uncorrelated samples
    [stderror_a, uncorsamp_a] = standard_error_uncorr_samp(a, eq_time = 0)
    [stderror_b, uncorsamp_b] = standard_error_uncorr_samp(b, eq_time = 0)
    [stderror_c, uncorsamp_c] = standard_error_uncorr_samp(c, eq_time = 0)
    [stderror_co_eng, uncorsamp_co_eng] = standard_error_uncorr_samp(co_eng, eq_time = 0)
    [stderror_tmp, uncorsamp_tmp] = standard_error_uncorr_samp(tmp, eq_time = 0)
    [stderror_Pxx, uncorsamp_Pxx] = standard_error_uncorr_samp(Pxx, eq_time = 0)
    [stderror_Pxy, uncorsamp_Pxy] = standard_error_uncorr_samp(Pxy, eq_time = 0)
    [stderror_Pxz, uncorsamp_Pxz] = standard_error_uncorr_samp(Pxz, eq_time = 0)
    [stderror_Pyy, uncorsamp_Pyy] = standard_error_uncorr_samp(Pyy, eq_time = 0)
    [stderror_Pyz, uncorsamp_Pyz] = standard_error_uncorr_samp(Pyz, eq_time = 0)
    [stderror_Pzz, uncorsamp_Pzz] = standard_error_uncorr_samp(Pzz, eq_time = 0)
    
    # standard_errors
    results_dict['standard-error'] = DM()
    results_dict['standard-error']['a'] = float(stderror_a)
    results_dict['standard-error']['b'] = float(stderror_b)
    results_dict['standard-error']['c'] = float(stderror_c)
    results_dict['standard-error']['cohesive-energy'] = float(stderror_co_eng)
    results_dict['standard-error']['temperature'] = float(stderror_tmp)
    results_dict['standard-error']['pressure-xx'] = float(stderror_Pxx)
    results_dict['standard-error']['pressure-xy'] = float(stderror_Pxy)
    results_dict['standard-error']['pressure-xz'] = float(stderror_Pxz)
    results_dict['standard-error']['pressure-yy'] = float(stderror_Pyy)
    results_dict['standard-error']['pressure-yz'] = float(stderror_Pyz)
    results_dict['standard-error']['pressure-zz'] = float(stderror_Pzz)
    
    # uncorrelated samples
    results_dict['uncorrelated-samples'] = DM()
    results_dict['uncorrelated-samples']['a'] = float(uncorsamp_a)
    results_dict['uncorrelated-samples']['b'] = float(uncorsamp_b)
    results_dict['uncorrelated-samples']['c'] = float(uncorsamp_c)
    results_dict['uncorrelated-samples']['cohesive-energy'] = float(uncorsamp_co_eng)
    
    plt.plot(total_step,total_val)
    plt.plot([eq_time],[eq_val],'ro')
    plt.savefig('temperature.png')
    plt.close()
    plt.show()
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=3)

def equilibrum(lammps_command, system, potential, symbols, mpi_command='',
               t_steps=1000, press=0.0, d_every=100000, r_steps=100000, rand = random.randint(0,1000000), temp = 0):
    
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
    
def min_script(template_file, system_info, pair_info, t_steps = 0.0, press = 0.0, d_every = 100000, r_steps = 100000, rand = random.randint(0,1000000)):
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
        
def min_script_temp(template_file, system_info, pair_info, t_steps = 0.0, press = 0.0, d_every = 100000, r_steps = 100000, rand = random.randint(0,1000000), temp = 0):
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



def find_equil_all_data(thermo_data):
    
    temp_data = np.array(thermo_data['Temp'])
    Lx_data = np.array(thermo_data['Lx'])
    Ly_data = np.array(thermo_data['Ly'])
    Lz_data = np.array(thermo_data['Lz'])
    
    array = np.zeros(4)
    
    array[0] = find_time_of_equilibrium(temp_data)
    array[1] = find_time_of_equilibrium(Lx_data)
    array[2] = find_time_of_equilibrium(Ly_data)
    array[3] = find_time_of_equilibrium(Lz_data)
    
    return np.max(array)
    
def lattice_param(input_dict, thermo_data, eq_time):
    total_lx = np.array(thermo_data['Lx'][eq_time:])
    total_ly = np.array(thermo_data['Ly'][eq_time:])
    total_lz = np.array(thermo_data['Lz'][eq_time:])
    a_mult = input_dict['a_mult']
    b_mult = input_dict['a_mult']
    c_mult = input_dict['a_mult']
    a = total_lx/a_mult
    b = total_ly/b_mult
    c = total_lz/c_mult
    return a, b, c

def cohesive_energy(potEng, eq_time, system):
    return potEng[eq_time:]/system.natoms
    
def pymbar_stats(data, eq_time, search_step):
    [t, g, Neff_max] = timeseries.detectEquilibration(data[eq_time:], nskip = search_step)
    return g, Neff_max
    
def standard_error_uncorr_samp(data, eq_time, search_step = 10):
	[g, Neff] = pymbar_stats(data, eq_time, search_step)
	return math.sqrt(1/Neff)*np.std(data[eq_time:]), Neff/g
    


#########################################################   
# Methods for finding time and value of equilibrium #
#########################################################

def split_list(a_list):
    #Splits data in half#
    
    half = len(a_list)/2
    if len(a_list[:half]) != len(a_list[half:]):
        return a_list[:half], a_list[half:len(a_list)-1]
    
    return a_list[:half], a_list[half:]
        
def break_data(data, block = 100):
	############FIX############### NUMPY COMMAND
    #create arrays of ave and std of the blocks
    
    length = len(data)
    block_array_ave = np.zeros(block)
    block_array_std = np.zeros(block)
    for step in range(0,block):
        block_array_ave[step] = np.average(data[(step*(length)/block):((step+1)*(length/block))])
    for step in range(0,block):
        block_array_std[step] = np.std(data[(step*(length)/block):((step+1)*(length/block))])
    return block_array_ave, block_array_std
        
def std_and_ave(total_step, total_val, breaks = 100):
    #breaks data into sections and finds the standard deviations and averages#
    
    ave_arr = np.zeros(breaks)
    for step in range(0,breaks):
        ave_arr[step] = np.average(total_val[(step*(len(total_val)-1)/breaks):((step+1)*(len(total_val)-1)/breaks)])
    
    #int_aver = np.average(ave_arr)
    #int_std = np.std(ave_arr)
    
    ones_array = np.ones(len(total_val))
    ave_fixed = np.zeros(len(total_val))
    std =  np.zeros(len(total_val))
    start = 0
    interv = int(math.ceil((1/float(breaks))*len(total_val)))
    
    for i in range(0, breaks):
        ave_fixed[start:start+interv] = ones_array[start:start+interv]*ave_arr[i]
        std[start:start+interv] = np.std(total_val[start:start+interv])
        start = start+interv
        
    return ave_fixed, std, np.average(ave_arr)

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    #Determines how close two values are#
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    
def consecutive(data, stepsize=1):
    #Determines if an array is consecutive within the stepsize#
    if stepsize > 1:
        return np.split(data, np.where(np.abs(np.diff(data)) >= stepsize)[0]+1)
    else:
        return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)
        
def find_max_indices(length_array, consec):
    #Find indices of the same max size of consecutive#
    index = np.where(length_array == np.max(length_array))
    find = np.zeros([len(index[0]),int(np.max(length_array))])
    j = 0
    for i in index[0]:
        find[j] = consec[i]
        j=j+1
    return find
    
def find_close_indices(rank): #(rank, split=3)?
    #Finds values of array that are within split value#
    #KEEP?
    split = len(rank)/3
    
    consec = consecutive(rank, stepsize=split)
    
    array = np.zeros(len(consec))
    for i in range(0,len(consec)):
        array[i] = len(consec[i])
        
    # find indices of the same max size of consecutive
    index = np.where(array == np.max(array))
    find = np.zeros([len(index[0]),int(np.max(array))])
    j = 0
    for i in index[0]:
        find[j] = consec[i]
        j=j+1
    return find

    
def find_index_interest(rank):
    #Finds index of the start of consecutive rankings to determine where data starts consistency#
    
    # find consecutive values
    consec = consecutive(rank)
    
    # create array that stores lengths of consecutive values
    array = np.zeros(len(consec))
    for i in range(0,len(consec)):
        array[i] = len(consec[i])
        
    if (np.max(array) > 1):
        # find indices of the same max size 
        find = find_max_indices(array, consec)
    else:
        find = find_close_indices(rank)
        
    # stack and sort them
    find = np.hstack(find)
    find = np.sort(find)
    
    # find smallest value of 
    i = int(consecutive(find)[0][0])
    return i
        
def find_equilibrium(data, increment = 100, index = 0):
    #finds the equilibrium value by splitting data in half and finding averages of the halves.
    #if the first standard deviation is greater than the second or the size of a half is smaller 
    #than the increment size, then the average of the two halves are returned. Else the data is
    #incremented and is put through the same process.#
    
    data_one, data_two = split_list(data[index:])
    
    f_half_ave = np.average(data_one)
    f_half_std = np.std(data_one)
    s_half_ave = np.average(data_two)
    s_half_std = np.std(data_two)
    
    if (f_half_std > s_half_std) or (len(data_one) >= increment):
        index = index + increment
        #recursive
        return find_equilibrium(data, index = index)
        
    return np.average([f_half_ave, s_half_ave])

def find_time_of_equilibrium(data, break_ = 2):
    #Finds a safe cutoff by finding when the data is consistant and has a low standard deviation#
    
    index_array = np.zeros(break_)
    block = 10
    	
    for num in range(0,break_):
        
        # average and standard deviation of blocks
        [block_array_ave, block_array_std] = break_data(data, block = block)
        
        # finds larger and smaller std rankings by halving them
        smallest_std = np.argsort(block_array_std)[:block/2]
        #if ((smallest_std[0] >= block-(block/10)) or (smallest_std[1] >= block-(block/10))):
        #    print 'You may want to make data longer.'
        biggest_std = np.argsort(block_array_std)[block/2:]
        
        # whole ranking
        whole = np.hstack((smallest_std, biggest_std))
        
        # finds indices
        i = (find_index_interest(smallest_std))
        #index_1 = (find_index_interest(smallest_std))
        #index_2 = (find_index_interest(whole)+find_index_interest(smallest_std))/2
        #print find_index_interest(whole), find_index_interest(smallest_std)
        
        if ((i >= block-(block/10)) or (i >= block-(block/10))):
            print 'You may want to make data longer.'
        
        # stores values
        index_array[num] = i*len(data)/block
        
        block = block*10
        
    # average indices
    index = int(np.average(index_array))
    
    return index


if __name__ == '__main__':
    main(*sys.argv[1:])  


