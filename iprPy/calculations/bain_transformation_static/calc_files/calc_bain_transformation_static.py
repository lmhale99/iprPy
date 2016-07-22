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

#Read in parameters from input file

def main(*args):

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = iprPy.calculation_read_input(__calc_type__, f, *args[1:])

    results_dict = {}
    results_dict['initial'] = bain_run_calcs(input_dict,__calc_type__,'initial')    
    results_dict['bain'] = bain_run_calcs(input_dict,__calc_type__,'bain')
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp = f, indent = 2)
    

def bain_relax_script(template_file, system_info, pair_info, etol = 0.0, ftol = 1e-6, maxiter = 100000, maxeval = 100000, 
                      bain_a_scale = 0, bain_c_scale =0):
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

def bain_run_calcs(input_dict, __calc_type__, step):  

    #-------------------SETS UP THE SYSTEM--------------------
    
    #Read in potential
    potential = lmp.Potential(input_dict['potential'], input_dict['potential_dir']) #reads the potential filename
    system = input_dict['initial_system']
    
    #if initial step, set up system to find difference in cohesive energy. this step is skipped when a and c values change.
    if step == 'initial':
        a_scale = 1
        c_scale = 1
    elif step == 'bain':
        a_scale = input_dict['bain_a_scale']
        c_scale = input_dict['bain_c_scale']
    
    #scale box and atoms simultaneously
    system.box_set(a = a_scale*system.box.a,
                   b = a_scale*system.box.b,
                   c = c_scale*system.box.c,
                   scale = True)
      
    #ensure all atoms are within the box
    system.wrap()  
    
    #-------------------RUN LAMMPS AND SAVE RESULTS------------------
    #use above information to generate system_info and pair_info for LAMMPS
    system_info = am.lammps.atom_data.dump('bain.dat', system, units=potential.units, atom_style=potential.atom_style)
    pair_info = potential.pair_info(input_dict['symbols']) #pulls the potential info when given which element the calculation is running on

    #write the LAMMPS input script
    with open('bain.in', 'w') as f:
        f.write(bain_relax_script('min.template', system_info, pair_info, 
                                etol = input_dict['energy_tolerance'], 
                                ftol = input_dict['force_tolerance'], 
                                maxiter = input_dict['maximum_iterations'], 
                                maxeval = input_dict['maximum_evaluations']))
    #run LAMMPS
    output = lmp.run(input_dict['lammps_command'], 'bain.in', input_dict['mpi_command'])
    
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
        
    elif step == 'bain':
        try:
            os.rename(atom_last, 'bain.dump')
        except:
            os.remove('bain.dump')
            os.rename(atom_last, 'bain.dump')
        os.remove('atom.0')
        d_system = lmp.atom_dump.load('bain.dump')

    results_dict = {}
    results_dict['potential_energy'] = float(output.finds('PotEng')[-1])

    #return values
    return results_dict['potential_energy']

if __name__ == '__main__':
    main(*sys.argv[1:])  