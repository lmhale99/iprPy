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
    
    #Pull out dislocation-related parameters
    disl_params = input_dict['dislocation_model'].find('atomman-defect-Stroh-parameters')
    burgers = input_dict['ucell'].box.a * np.array(disl_params['burgers'])
    b_width = input_dict['ucell'].box.a * np.array(input_dict['boundary_width'])
    axes = np.array([disl_params['crystallographic-axes']['x-axis'],
                     disl_params['crystallographic-axes']['y-axis'],
                     disl_params['crystallographic-axes']['z-axis']], dtype='int32')                     
    C = am.tools.ElasticConstants(model=input_dict['elastic_constants_model'])
    
    #Read in potential
    potential = lmp.Potential(input_dict['potential'], input_dict['potential_dir'])        
    
    #Generate perfect system
    system = am.tools.rotate_cubic(input_dict['ucell'], axes)
    spos = system.atoms_prop(key='pos', scale=True) + np.array(disl_params['shift'])
    system.atoms_prop(key='pos', value=spos, scale=True)
    system.wrap()
    system.supersize(input_dict['a_mult'], input_dict['b_mult'],input_dict['c_mult'])
    system_info = am.lammps.atom_data.dump('base.dat', system, units=potential.units, atom_style=potential.atom_style)
    
    #Generate dislocation monopole system
    stroh = am.defect.Stroh(C, burgers, axes=axes)
    pos = system.atoms_prop(key='pos')
    disp = stroh.displacement(pos)
    system.atoms_prop(key='pos', value=pos+disp)
    system.wrap()
    
    #Add fixed boundary condition
    moving_atypes = ' '.join(np.array(range(1, system.natypes+1), dtype=str))
    system, symbols = boundary_fix(system, input_dict['symbols'], b_width, input_dict['boundary_shape'])
    system_info = am.lammps.atom_data.dump('disl.dat', system, units=potential.units, atom_style=potential.atom_style)
    
    #Run LAMMPS to relax system
    pair_info = potential.pair_info(symbols)
    if input_dict['anneal_temperature'] == 0.0:
        template_file = 'disl_relax_notemp.template'
    else:   
        template_file = 'disl_relax.template'
    with open('disl_relax.in', 'w') as f:
        f.write(disl_relax_script(template_file, system_info, pair_info, 
                                  etol = input_dict['energy_tolerance'], 
                                  ftol = input_dict['force_tolerance'], 
                                  maxiter = input_dict['maximum_iterations'], 
                                  maxeval = input_dict['maximum_evaluations'], 
                                  anneal_temp = input_dict['anneal_temperature'], 
                                  moving_atypes = moving_atypes))
    output = lmp.run(input_dict['lammps_command'], 'disl_relax.in', input_dict['mpi_command'])
    atom_last = 'atom.%i' % output.finds('Step')[-1]
    try:
        os.rename(atom_last, 'disl.dump')
    except:
        os.remove('disl.dump')
        os.rename(atom_last, 'disl.dump')
    os.remove('atom.0')
    d_system = lmp.atom_dump.load('disl.dump')
    
    results_dict = {}
    
    results_dict['defect_system'] = d_system
    
    results_dict['pre-ln_factor'] = stroh.preln
    results_dict['potential_energy'] =float(output.finds('PotEng')[-1])
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f)


def boundary_fix(system, symbols, b_width, shape='circle'):
    """Create boundary region by changing atom types. Returns a new system and symbols list."""
    natypes = system.natypes
    atypes = system.atoms_prop(key='atype')
    pos = system.atoms_prop(key='pos')
    
    if shape == 'circle':
        #find x or y bound closest to 0
        smallest_xy = min([abs(system.box.xlo), abs(system.box.xhi),
                           abs(system.box.ylo), abs(system.box.yhi)])
        
        radius = smallest_xy - b_width
        xy_mag = np.linalg.norm(system.atoms_prop(key='pos')[:,:2], axis=1)        
        atypes[xy_mag > radius] += natypes
    
    elif shape == 'rect':
        index = np.unique(np.hstack((np.where(pos[:,0] < system.box.xlo + b_width),
                                     np.where(pos[:,0] > system.box.xhi - b_width),
                                     np.where(pos[:,1] < system.box.ylo + b_width),
                                     np.where(pos[:,1] > system.box.yhi - b_width))))
        atypes[index] += natypes
           
    else:
        raise ValueError("Unknown shape type! Enter 'circle' or 'rect'")

    new_system = deepcopy(system)
    new_system.atoms_prop(key='atype', value=atypes)
    symbols.extend(symbols)
    
    return new_system, symbols
        
        
def disl_relax_script(template_file, system_info, pair_info, etol = 0.0, ftol = 1e-6, maxiter = 100000, maxeval = 100000, anneal_temp = 0.0, moving_atypes = '1'):
    """Create lammps script for performing a simple energy minimization."""    
    
    with open(template_file) as f:
        template = f.read()
    variable = {'atomman_system_info': system_info,
                'atomman_pair_info':   pair_info,
                'anneal_temp': anneal_temp,
                'group_move': moving_atypes,
                'energy_tolerance': etol, 
                'force_tolerance': ftol,
                'maximum_iterations': maxiter,
                'maximum_evaluations': maxeval}
    return '\n'.join(iprPy.tools.fill_template(template, variable, '<', '>'))
        
if __name__ == '__main__':
    main(*sys.argv[1:])    