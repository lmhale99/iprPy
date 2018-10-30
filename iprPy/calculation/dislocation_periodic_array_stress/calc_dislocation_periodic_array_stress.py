#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard library imports
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import sys
import uuid
import glob
import shutil
import random
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

# Define record_style
record_style = 'calculation_dislocation_periodic_array_stress'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
   
    results_dict = dislocationarraystress(input_dict['lammps_command'],
                                          input_dict['ucell'],
                                          input_dict['potential'],
                                          input_dict['temperature'],
                                          mpi_command = input_dict['mpi_command'],
                                          sigma_xz = input_dict['sigma_xz'],
                                          sigma_yz = input_dict['sigma_yz'],
                                          runsteps = input_dict['runsteps'],
                                          thermosteps = input_dict['thermosteps'],
                                          dumpsteps = input_dict['dumpsteps'],
                                          randomseed = input_dict['randomseed'],
                                          bwidth = input_dict['boundarywidth'],
                                          rigidbounds = input_dict['rigidboundaries'])
    
    # Save data model of results
    script = os.path.splitext(os.path.basename(__file__))[0]
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def dislocationarraystress(lammps_command, system, potential, temperature,
                           mpi_command=None, sigma_xz=0.0, sigma_yz=0.0,
                           runsteps=100000, thermosteps=100, dumpsteps=None,
                           randomseed=None, bwidth=None, rigidbounds=False):
    """
    Applies a constant external shearing stress to a periodic array of
    dislocations atomic system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The bulk system to add the defect to.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    temperature : float
        The temperature to run the simulation at.
    mpi_command : str or None, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    sigma_xz : float, optional
        The xz shear stress to apply to the system through the boundary atoms.
        Default value is 0.0.
    sigma_yz : float, optional
        The yz shear stress to apply to the system through the boundary atoms.
        Default value is 0.0.
    runsteps : int, optional
        The total number of steps to run the simulation for.  Default value
        is 100000.
    thermosteps : int, optional
        The system-wide thermo data will be outputted every this many steps.
        Default value is 100.
    dumpsteps : int, optional
        The atomic configurations will be saved to LAMMPS dump files every 
        this many steps.  Default value is equal to runsteps, which will only
        save the initial and final configurations.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities. Default is
        None which will select a random int between 1 and 900000000.
    bwidth : float, optional
        The thickness of the boundary region. Default value is 10 Angstroms.
    rigidbounds : bool, optional
        If True, the atoms in the boundary regions will be treated as a rigid
        block such that they move as one and do not allow internal atomic
        relaxations.  Default value is False, in which case the boundaries will
        be free surfaces.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed base system.
        - **'symbols_base'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the base system's
          atypes.
        - **'Stroh_preln'** (*float*) - The pre-logarithmic factor in the 
          dislocation's self-energy expression.
        - **'Stroh_K_tensor'** (*numpy.array of float*) - The energy
          coefficient tensor based on the dislocation's Stroh solution.
        - **'dumpfile_disl'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed dislocation monopole system.
        - **'symbols_disl'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the dislocation
          monopole system's atypes.
        - **'E_total_disl'** (*float*) - The total potential energy of the
          dislocation monopole system.
    """
    # Set default values
    if bwidth is None:
        bwidth = uc.set_in_units(10, 'angstrom')
    if randomseed is None: 
        randomseed = random.randint(1, 900000000)

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    # Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='initial.dat',
                              units=potential.units,
                              atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(system.symbols)
    
    lammps_variables['temperature'] = temperature

    stress_unit = lammps_units['force'] + '/' + lammps_units['length'] + '^2'
    lammps_variables['sigma_xz'] = uc.get_in_units(sigma_xz, stress_unit)
    lammps_variables['sigma_yz'] = uc.get_in_units(sigma_yz, stress_unit) 
    lammps_variables['dumpsteps'] = dumpsteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['randomseed'] = randomseed
    lammps_variables['bwidth'] = uc.get_in_units(bwidth, lammps_units['length'])
    lammps_variables['tdamp'] = 100 * lmp.style.timestep(potential.units)
    lammps_variables['timestep'] = lmp.style.timestep(potential.units)
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    if rigidbounds is True:
        template_file = 'dislarray_rigid_stress.template'
    else:
        template_file = 'dislarray_free_stress.template'
    lammps_script = 'dislarray_stress.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    thermo = output.simulations[-1]['thermo']
    steps = thermo.Step.values
    times = uc.set_in_units(steps * lmp.style.timestep(potential.units),
                            lammps_units['time'])

    # Read user-defined thermo data  
    if output.lammps_date < datetime.date(2016, 8, 1):
        strains_xz = thermo['strain_xz'].values
        strains_yz = thermo['strain_yz'].values
    else:
        strains_xz = thermo['v_strain_xz'].values
        strains_yz = thermo['v_strain_yz'].values

    # Compute average strain rates
    strainrate_xz, b = np.polyfit(times, strains_xz, 1)
    strainrate_yz, b = np.polyfit(times, strains_yz, 1)

    # Extract output values
    results_dict = {}
    results_dict['times'] = times
    results_dict['strains_xz'] = strains_xz
    results_dict['strains_yz'] = strains_yz
    results_dict['strainrate_xz'] = strainrate_xz
    results_dict['strainrate_yz'] = strainrate_yz

    return results_dict

def process_input(input_dict, UUID=None, build=True):
    """
    Processes str input parameters, assigns default values if needed, and
    generates new, more complex terms as used by the calculation.
    
    Parameters
    ----------
    input_dict :  dict
        Dictionary containing the calculation input parameters with string
        values.  The allowed keys depends on the calculation style.
    UUID : str, optional
        Unique identifier to use for the calculation instance.  If not 
        given and a 'UUID' key is not in input_dict, then a random UUID4 
        hash tag will be assigned.
    build : bool, optional
        Indicates if all complex terms are to be built.  A value of False
        allows for default values to be assigned even if some inputs 
        required by the calculation are incomplete.  (Default is True.)
    """
    
    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.interpret('units', input_dict)
    
    # These are calculation-specific default strings
    # None for this calculation
    
    # These are calculation-specific default booleans
    input_dict['rigidboundaries'] = iprPy.input.boolean(input_dict.get('rigidboundaries', False))
    
    # These are calculation-specific default integers
    input_dict['runsteps'] = int(input_dict.get('runsteps', 100000))
    input_dict['thermosteps'] = int(input_dict.get('thermosteps', 100))
    input_dict['dumpsteps'] = int(input_dict.get('dumpsteps',
                                                 input_dict['runsteps']))
    input_dict['randomseed'] = int(input_dict.get('randomseed',
                                      random.randint(1, 900000000)))
    
    # These are calculation-specific default unitless floats
    input_dict['temperature'] = float(input_dict['temperature'])
    
    # These are calculation-specific default floats with units
    input_dict['sigma_xz'] = iprPy.input.value(input_dict, 'sigma_xz',
                                            default_unit=input_dict['pressure_unit'],
                                            default_term='0.0 GPa')
    input_dict['sigma_yz'] = iprPy.input.value(input_dict, 'sigma_yz',
                                            default_unit=input_dict['pressure_unit'],
                                            default_term='0.0 GPa')
    input_dict['boundarywidth'] = iprPy.input.value(input_dict, 'boundarywidth',
                                            default_unit=input_dict['length_unit'],
                                            default_term='10 angstrom')
    
    # Check lammps_command and mpi_command
    iprPy.input.interpret('lammps_commands', input_dict)
    
    # Load potential
    iprPy.input.interpret('lammps_potential', input_dict)
    
    # Load ucell system
    iprPy.input.interpret('atomman_systemload', input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])