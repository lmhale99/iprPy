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
    
    units = DM([('length', input_dict['length_unit']), ('pressure', input_dict['pressure_unit']), 
           ('energy', input_dict['energy_unit']), ('force', input_dict['force_unit'])])       
    
    #Run equilibrum to refine values
    results = equilibrum(input_dict['lammps_command'],
                         input_dict['initial_system'], 
                         potential, 
                         input_dict['symbols'],
                         sys_units = units,
                         size_mults =  input_dict['size_mults'],
                         mpi_command = input_dict['mpi_command'],
                         t_steps =     input_dict['thermo_steps'], 
                         press =       input_dict['pressure'], 
                         d_every =     input_dict['dump_every'],
                         r_steps =     input_dict['run_steps'],
                         rand =         input_dict['random_seed'],
                         integration =    input_dict['integration'],
                         temp =         input_dict['temperature'])
    
    
    #Save data model of results 
    results_data = results['data']
    results_calc = iprPy.calculation_data_model(__calc_type__, input_dict, results)
    
    with open('results.json', 'w') as f:
        results_calc.json(fp=f, indent=4)
        
    with open('results_data.json', 'w') as f:
        results_data.json(fp=f, indent=4)
        

def equilibrum(lammps_command, system, potential, symbols, sys_units, size_mults , mpi_command='',
               t_steps=1000, press=0.0, d_every=100000, r_steps=100000, rand = random.randint(0,1000000), integration='npt', temp = 100):
    
    pair_info = potential.pair_info(symbols)
        
    #write system to data file
    system_info = lmp.atom_data.dump('perfect.dat', system, 
                                     units=potential.units, 
                                     atom_style=potential.atom_style)

    lammps_units = lmp.style.unit(potential.units)
    lammps_press = uc.get_in_units(press, lammps_units['pressure'])                                 
    #create LAMMPS input script
    if integration == 'nph':
        min_in = min_script('min_nph_langevin.template', system_info, pair_info, t_steps=t_steps, press=lammps_press, d_every=d_every, r_steps=r_steps, rand=rand, temp=temp)
        with open('perfect_min.in', 'w') as f:
            f.write(min_in)
    elif integration == 'npt':
        if temp == 0.0:
            raise ValueError('temperature cannot be 0 for npt calculation')
        min_in = min_script('min_npt.template', system_info, pair_info, t_steps=t_steps, press=lammps_press, d_every=d_every, r_steps=r_steps, rand=rand, temp=temp)
        with open('perfect_min.in', 'w') as f:
            f.write(min_in)

    #run lammps
    data = lmp.run(lammps_command, 'perfect_min.in', mpi_command)
    
    calc = DM()
    
    thermo_data = data.find('thermo')
    
    total_step = np.array(thermo_data['Step'])
    total_temp = np.array(thermo_data['Temp'])
    total_Lx = np.array(thermo_data['Lx'])
    total_Ly = np.array(thermo_data['Ly'])
    total_Lz = np.array(thermo_data['Lz'])
    
    # equilibrium time and value (temperature)
    eq_time = find_equil_all_data(total_temp, total_Lx, total_Ly, total_Lz)
    eq_val = np.mean(total_temp[eq_time:])
    
    # standard_errors and uncorrelated samples
    [t,g,Neff] = detectEquilibration(total_temp, t=eq_time, nskip=10)
    calc['correlation-analysis-temp'] = DM()
    calc['correlation-analysis-temp']['equilibrium-temperature'] = eq_val
    calc['correlation-analysis-temp']['starting-equilibrium-index'] = float(t)
    calc['correlation-analysis-temp']['uncorrelated-samples'] = float(Neff)
    calc['correlation-analysis-temp']['statistical-inefficiency'] = float(g)
    
    # mean lattice parameters
    [a,b,c] = lattice_param(size_mults, total_Lx, total_Ly, total_Lz)
    calc['mean-lattice-parameter'] = lat = DM()
    
    [t,g,Neff] = detectEquilibration(a, t=eq_time, nskip=10)
    lat['a'] = DM([('value', float(np.mean(a[eq_time:]))), ('unit', sys_units['length']), 
        ('error', float(standard_error_mean(t, g, Neff, a))), ('uncorrelated-samples', float(Neff))])
    
    [t,g,Neff] = detectEquilibration(b, t=eq_time, nskip=10)
    lat['b'] = DM([('value', float(np.mean(b[eq_time:]))), ('unit', sys_units['length']), 
        ('error', float(standard_error_mean(t, g, Neff, b))), ('uncorrelated-samples', float(Neff))])
    
    [t,g,Neff] = detectEquilibration(c, t=eq_time, nskip=10)
    lat['c'] = DM([('value', float(np.mean(c[eq_time:]))), ('unit', sys_units['length']), 
        ('error', float(standard_error_mean(t, g, Neff, c))), ('uncorrelated-samples', float(Neff))])
    
    # mean cohesive energy
    co_eng = cohesive_energy(np.array(thermo_data['PotEng']), system.natoms)
    [t,g,Neff] = detectEquilibration(co_eng, t=eq_time, nskip=10)
    calc['mean-cohesive-energy'] = DM([('value', float(np.mean(co_eng[eq_time:]))), ('unit', sys_units['energy']), 
        ('error', float(standard_error_mean(t, g, Neff, co_eng))),('uncorrelated-samples', float(Neff))])
    
    # pressures
    Pxx = np.array(thermo_data['Pxx'])
    Pxy = np.array(thermo_data['Pxy'])
    Pxz = np.array(thermo_data['Pxz'])
    Pyy = np.array(thermo_data['Pyy'])
    Pyz = np.array(thermo_data['Pyz'])
    Pzz = np.array(thermo_data['Pzz'])
    
    # mean temperature pressures
    calc['pressure'] = press = DM()
    [t,g,Neff] = detectEquilibration(Pxx, t=eq_time, nskip=10)
    press['mean-pressure-xx'] = value_model(float(np.mean(Pxx[eq_time:])), sys_units['pressure'], 
        float(standard_error_mean(t, g, Neff, Pxx)))
    [t,g,Neff] = detectEquilibration(Pxy, t=eq_time, nskip=10)
    press['mean-pressure-xy'] = value_model(float(np.mean(Pxy[eq_time:])), sys_units['pressure'], 
        float(standard_error_mean(t, g, Neff, Pxy)))
    [t,g,Neff] = detectEquilibration(Pxz, t=eq_time, nskip=10)
    press['mean-pressure-xz'] = value_model(float(np.mean(Pxz[eq_time:])), sys_units['pressure'], 
        float(standard_error_mean(t, g, Neff, Pxz)))
    [t,g,Neff] = detectEquilibration(Pyy, t=eq_time, nskip=10)
    press['mean-pressure-yy'] = value_model(float(np.mean(Pyy[eq_time:])), sys_units['pressure'], 
        float(standard_error_mean(t, g, Neff, Pyy)))
    [t,g,Neff] = detectEquilibration(Pyz, t=eq_time, nskip=10)
    press['mean-pressure-yz'] = value_model(float(np.mean(Pyz[eq_time:])), sys_units['pressure'], 
        float(standard_error_mean(t, g, Neff, Pyz)))
    [t,g,Neff] = detectEquilibration(Pzz, t=eq_time, nskip=10)
    press['mean-pressure-zz'] = value_model(float(np.mean(Pzz[eq_time:])), sys_units['pressure'], 
        float(standard_error_mean(t, g, Neff, Pzz)))
    
    return {'data': data, 'calc': calc}

def min_script(template_file, system_info, pair_info, t_steps = 0.0, press = 0.0, d_every = 100000, r_steps = 100000, rand = random.randint(0,1000000), integration='npt', temp = 100):
    """Create lammps script for performing a simple energy minimization."""    
    
    with open(template_file) as f:
        template = f.read()
    variable = {'atomman_system_info': system_info,
                'atomman_pair_info': pair_info,
                'thermo_steps': t_steps, 
                'pressure': press,
                'dump_every': d_every,
                'run_steps': r_steps,
                'random_seed': rand,
                'temperature': temp}
    return '\n'.join(iprPy.tools.fill_template(template, variable, '<', '>'))
  



def value_model(value, units, error = None):
    return DM([('value', value), ('unit', units), ('error', error)])
    #return DM([('value', uc.get_in_units(value, units)), ('unit', units), ('error', uc.get_in_units(error, units))])

def find_equil_all_data(temp_data, Lx_data, Ly_data, Lz_data):
    
    array = np.zeros(4)
    
    array[0] = find_time_of_equilibrium(temp_data)
    array[1] = find_time_of_equilibrium(Lx_data)
    array[2] = find_time_of_equilibrium(Ly_data)
    array[3] = find_time_of_equilibrium(Lz_data)
    
    return np.max(array)
    
def lattice_param(size_mults, Lx_data, Ly_data, Lz_data):
    
    a_mult = size_mults[0][1] - size_mults[0][0]
    b_mult = size_mults[1][1] - size_mults[1][0]
    c_mult = size_mults[2][1] - size_mults[2][0]
    a = Lx_data/a_mult
    b = Ly_data/b_mult
    c = Lz_data/c_mult
    return a, b, c

def cohesive_energy(potEng, atoms):
    return potEng/atoms
    
def standard_error_mean(t, g, Neff, data):
    return math.sqrt(1/float(Neff))*np.std(data)
  


#########################################################   
''' Methods for finding time and value of equilibrium '''
#########################################################

        
def break_data(data, block = 100):
    #create arrays of ave and std of the blocks
    
    block_array_ave = np.zeros(block)
    block_array_std = np.zeros(block)
    for step in range(0,block):
        block_array_ave[step] = np.average(np.array_split(data,block)[step])
    for step in range(0,block):
        block_array_std[step] = np.std(np.array_split(data,block)[step])
    return block_array_ave, block_array_std

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    #Determines how close two values are#
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
    
def consecutive(data, stepsize=1):
    #Determines if an array is consecutive within the stepsize#
    if stepsize > 1:
        return np.split(data, np.where(np.abs(np.diff(data)) >= stepsize)[0]+1)
    else:
        return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)
        
def find_maxlen_consec(length_array, consec):
    #Find indices of the same max size of consecutive#
    index = np.where(length_array == np.max(length_array))
    find = np.zeros([len(index[0]),int(np.max(length_array))])
    j = 0
    for i in index[0]:
        find[j] = consec[i]
        j=j+1
    return find
    
def find_close_consec(rank): #(rank, split=3)?
    #Finds values of array that are within split value#
    split = len(rank)/3 #KEEP?
    
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
        find = find_maxlen_consec(array, consec)
    else:
        find = find_close_consec(rank)
        
    # stack and sort them
    find = np.hstack(find)
    find = np.sort(find)
    
    # find smallest value of 
    i = int(consecutive(find)[0][0])
    return i

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
    
    
def detectEquilibration(A_t, t, fast=True, nskip=1):
    #Modified version from pymbar where t, equilibrium time, is a parameter
    
    T = A_t.size

    # Special case if timeseries is constant.
    if A_t.std() == 0.0:
        return (0, 1, 1)  # Changed from Neff=N to Neff=1 after issue #122

    g_t = np.ones([T - 1], np.float32)
    Neff_t = np.ones([T - 1], np.float32)
    for i in range(0, T - 1, nskip):
        try:
            g_t[i] = timeseries.statisticalInefficiency(A_t[i:T], fast=fast)
        except ParameterError:  # Fix for issue https://github.com/choderalab/pymbar/issues/122
            g_t[i] = (T - i + 1)
        Neff_t[i] = (T - i + 1) / g_t[i]
    Neff_max = Neff_t.max()
    
    #t = Neff_t.argmax()
    g = g_t[t]

    return (t, g, Neff_max)


if __name__ == '__main__':
    main(*sys.argv[1:])
