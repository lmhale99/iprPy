#!/usr/bin/env python
import os
import sys
import numpy as np
from copy import deepcopy

import iprPy

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
    burgers = input_dict['ucell'].box.a * np.array(input_dict['burgers'])
    b_width = input_dict['ucell'].box.a * np.array(input_dict['boundary_width'])
    axes = np.array([input_dict['x-axis'], input_dict['y-axis'], input_dict['z-axis']])                     
    C = input_dict['C']
    
    #Read in potential
    potential = lmp.Potential(input_dict['potential'], input_dict['potential_dir'])        
    
    #Save initial perfect system
    am.lammps.atom_dump.dump(input_dict['initial_system'], 'base.dump')
    
    #Generate unrelaxed dislocation system
    unrelaxed = disl_monopole_gen(input_dict['initial_system'], C, burgers, axes=axes)
    
    #Add fixed boundary condition
    system, symbols = disl_boundary_fix(unrelaxed['system_disl_unrelaxed'], input_dict['symbols'], b_width, input_dict['boundary_shape'])
    
    #relax system
    relaxed = disl_relax(input_dict['lammps_command'], system, potential, symbols, 
                         mpi_command=input_dict['mpi_command'], 
                         anneal_temperature=input_dict['anneal_temperature'],
                         etol=input_dict['energy_tolerance'], 
                         ftol=input_dict['force_tolerance'], 
                         maxiter=input_dict['maximum_iterations'], 
                         maxeval=input_dict['maximum_evaluations'])
    
    #Save relaxed dislocation system
    am.lammps.atom_dump.dump(relaxed['system_disl'], 'disl.dump')

    #Copy results to results_dict
    results_dict = {}
    results_dict['dump_file_base'] = 'base.dump'
    results_dict['dump_file_disl'] = 'disl.dump'    
    results_dict['symbols_disl'] = symbols
    results_dict['E_total_disl'] = relaxed['E_total_disl']
    results_dict['pre-ln_factor'] = unrelaxed['stroh'].preln    
    
    #Save data model of results 
    results = iprPy.calculation_data_model(__calc_type__, input_dict, results_dict)
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def disl_monopole_gen(system, C, burgers, axes=None):
    """Add a dislocation monopole to a system using the Stroh method."""
    
    system_disl_unrelaxed = deepcopy(system)
    
    stroh = am.defect.Stroh(C, burgers, axes=axes)
    
    disp = stroh.displacement(system_disl_unrelaxed.atoms.view['pos'])
    system_disl_unrelaxed.atoms.view['pos'] += disp
        
    system_disl_unrelaxed.wrap()
    
    return {'system_disl_unrelaxed':system_disl_unrelaxed, 'stroh':stroh}        

def disl_boundary_fix(system, symbols, b_width, b_shape='circle'):
    """Create boundary region by changing atom types. Returns a new system and symbols list."""
    natypes = system.natypes
    atypes = system.atoms_prop(key='atype')
    pos = system.atoms_prop(key='pos')
    
    if b_shape == 'circle':
        #find x or y bound closest to 0
        smallest_xy = min([abs(system.box.xlo), abs(system.box.xhi),
                           abs(system.box.ylo), abs(system.box.yhi)])
        
        radius = smallest_xy - b_width
        xy_mag = np.linalg.norm(system.atoms_prop(key='pos')[:,:2], axis=1)        
        atypes[xy_mag > radius] += natypes
    
    elif b_shape == 'rect':
        index = np.unique(np.hstack((np.where(pos[:,0] < system.box.xlo + b_width),
                                     np.where(pos[:,0] > system.box.xhi - b_width),
                                     np.where(pos[:,1] < system.box.ylo + b_width),
                                     np.where(pos[:,1] > system.box.yhi - b_width))))
        atypes[index] += natypes
           
    else:
        raise ValueError("Unknown b_shape type! Enter 'circle' or 'rect'")

    new_system = deepcopy(system)
    new_system.atoms_prop(key='atype', value=atypes)
    symbols.extend(symbols)
    
    return new_system, symbols        
        
def disl_relax(lammps_command, system, potential, symbols, 
               mpi_command=None, anneal_temperature=0.0,
               etol=0.0, ftol=1e-6, maxiter=100000, maxeval=100000):
    """Runs LAMMPS using the disl_relax.in script for relaxing a dislocation monopole system."""
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Read LAMMPS input template
    if anneal_temperature == 0.0:
        with open('disl_relax_no_temp.template') as f:
            template = f.read()
    else:
        with open('disl_relax.template') as f:
            template = f.read()
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'disl_unrelaxed.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['atomman_pair_info'] =   potential.pair_info(symbols)
    lammps_variables['anneal_temp'] =         anneal_temperature
    lammps_variables['energy_tolerance'] =    etol
    lammps_variables['force_tolerance'] =     uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maximum_iterations'] =  maxiter
    lammps_variables['maximum_evaluations'] = maxeval
    lammps_variables['group_move'] =          ' '.join(np.array(range(1, system.natypes/2+1), dtype=str))
    
    #Write lammps input script
    with open('disl_relax.in', 'w') as f:
        f.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))

    #run lammps to relax perfect.dat
    output = lmp.run(lammps_command, 'disl_relax.in', mpi_command)
    
    #Extract LAMMPS thermo data.
    E_total_disl = uc.set_in_units(output.finds('PotEng')[-1], lammps_units['energy'])
    
    #Load relaxed system from dump file and copy old vects as dump files crop values
    last_dump_file = 'atom.'+str(int(output.finds('Step')[-1]))
    system_disl = lmp.atom_dump.load(last_dump_file)
    system_disl.box_set(vects=system.box.vects, origin=system.box.origin)
    
    return {'E_total_disl':E_total_disl, 'system_disl':system_disl}
    
if __name__ == '__main__':
    main(*sys.argv[1:])    