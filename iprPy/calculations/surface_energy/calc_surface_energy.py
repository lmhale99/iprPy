#!/usr/bin/env python

# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from __future__ import print_function, division
import os
import sys
import uuid
import shutil
import datetime
from copy import deepcopy

# http://www.numpy.org/
import numpy as np 

# https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

# https://github.com/usnistgov/iprPy
import iprPy

# Define calc_style and record_style
calc_style = 'surface_energy'
record_style = 'calculation-surface-energy'

def main(*args):
    """Main function for running calculation"""

    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters 
    process_input(input_dict, *args[1:])
   
    results_dict = surface_energy(input_dict['lammps_command'], 
                                  input_dict['initialsystem'], 
                                  input_dict['potential'], 
                                  input_dict['symbols'], 
                                  mpi_command = input_dict['mpi_command'], 
                                  etol =        input_dict['energytolerance'], 
                                  ftol =        input_dict['forcetolerance'], 
                                  maxiter =     input_dict['maxiterations'], 
                                  maxeval =     input_dict['maxevaluations'], 
                                  dmax =        input_dict['maxatommotion'],
                                  cutboxvector = input_dict['surface_cutboxvector'])
    
    # Save data model of results 
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def surface_energy(lammps_command, system, potential, symbols, mpi_command=None, 
                   etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000, 
                   dmax=uc.set_in_units(0.01, 'angstrom'), cutboxvector='c'):
    """
    This calculates surface energies by comparing the energy of a system with 
    all periodic boundaries to the same system with one non-periodic boundary,
    effectively cutting along that atomic plane.
    """

    # Evaluate perfect system
    system.pbc = [True, True, True]
    perfect = relax_system(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                           etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax)
    
    # Extract results from perfect system
    dumpfile_base = 'perfect.dump'
    shutil.move(perfect['finaldumpfile'], dumpfile_base)
    shutil.move('log.lammps', 'perfect-log.lammps')
    E_total_base = perfect['potentialenergy']   

    # Set up defect system
    # A_surf is area of parallelogram defined by the two box vectors not along the cutboxvector
    if   cutboxvector == 'a':
        system.pbc[0] = False
        A_surf = np.linalg.norm(np.cross(system.box.bvect, system.box.cvect))
        
    elif cutboxvector == 'b':
        system.pbc[1] = False
        A_surf = np.linalg.norm(np.cross(system.box.avect, system.box.cvect))
        
    elif cutboxvector == 'c':
        system.pbc[2] = False
        A_surf = np.linalg.norm(np.cross(system.box.avect, system.box.bvect))
        
    else:
        raise ValueError('Invalid cutboxvector')
        
    # Evaluate system with free surface
    surface = relax_system(lammps_command, system, potential, symbols, mpi_command=mpi_command, 
                          etol=etol, ftol=ftol, maxiter=maxiter, maxeval=maxeval, dmax=dmax)
    
    # Extract results from system with free surface
    dumpfile_surf = 'surface.dump'
    shutil.move(surface['finaldumpfile'], dumpfile_surf)
    shutil.move('log.lammps', 'surface-log.lammps')
    E_total_surf = surface['potentialenergy']
    
    # Compute the free surface formation energy
    E_surf_f = (E_total_surf - E_total_base) / (2 * A_surf)
    
    # Save values to results dictionary
    results_dict = {}
    
    results_dict['dumpfile_base'] = dumpfile_base
    results_dict['dumpfile_surf'] = dumpfile_surf
    results_dict['E_total_base'] = E_total_base
    results_dict['E_total_surf'] = E_total_surf
    results_dict['A_surf'] = A_surf
    results_dict['E_coh'] = E_total_base / system.natoms 
    results_dict['E_surf_f'] = E_surf_f    
    
    return results_dict
    
def relax_system(lammps_command, system, potential, symbols, mpi_command=None, 
                 etol=0.0, ftol=0.0, maxiter=100, maxeval=1000, dmax=0.01):
    """
    Sets up and runs the min LAMMPS script for statically relaxing a system
    """

    # Ensure all atoms are within the system's box
    system.wrap()
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
      
    #Get lammps version date
    lammps_date = iprPy.tools.check_lammps_version(lammps_command)['lammps_date']
    
    # Define lammps variables
    lammps_variables = {}
    
    # Generate system and pair info
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'system.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    
    # Pass in run parameters
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = uc.get_in_units(dmax, lammps_units['length'])
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%i %i %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'            
    
    # Write lammps input script
    template_file = 'min.template'
    lammps_script = 'min.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command, return_style='object')
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    results = {}
    results['logfile'] =         'log.lammps'
    results['initialdatafile'] = 'system.dat'
    results['initialdumpfile'] = 'atom.0'
    results['finaldumpfile'] =   'atom.%i' % thermo.Step.values[-1] 
    results['potentialenergy'] = uc.set_in_units(thermo.PotEng.values[-1], lammps_units['energy'])
    
    return results

def process_input(input_dict, UUID=None, build=True):
    """Reads the calc_*.in input commands for this calculation and sets default values if needed."""
    
    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.units(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['maxiterations'] =  int(input_dict.get('maxiterations',  10000))
    input_dict['maxevaluations'] = int(input_dict.get('maxevaluations', 100000))
    
    # These are calculation-specific default unitless floats
    input_dict['energytolerance'] = float(input_dict.get('energytolerance', 0.0))
    
    # These are calculation-specific default floats with units
    input_dict['forcetolerance'] = iprPy.input.value(input_dict, 'forcetolerance',
                                                     default_unit=input_dict['force_unit'],  
                                                     default_term='1.0e-6 eV/angstrom')             
    input_dict['maxatommotion'] = iprPy.input.value(input_dict, 'maxatommotion', 
                                                    default_unit=input_dict['length_unit'], 
                                                    default_term='0.01 angstrom')
    
    # Check lammps_command and mpi_command
    iprPy.input.commands(input_dict)
    
    # Load potential
    iprPy.input.potential(input_dict)
    
    # Load free surface parameters
    iprPy.input.freesurface(input_dict)
    
    # Load ucell system
    iprPy.input.systemload(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)
    
if __name__ == '__main__':
    main(*sys.argv[1:])     
    
