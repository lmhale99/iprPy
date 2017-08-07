#!/usr/bin/env python

# Python script created by Lucas Hale and Norman Luu.

# Standard library imports
from __future__ import division, absolute_import, print_function
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
record_style = 'calculation_surface_energy'

def main(*args):
    """Main function called when script is executed directly."""

    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run surface_energy
    results_dict = surface_energy(input_dict['lammps_command'],
                                  input_dict['initialsystem'],
                                  input_dict['potential'],
                                  input_dict['symbols'],
                                  mpi_command = input_dict['mpi_command'],
                                  etol = input_dict['energytolerance'],
                                  ftol = input_dict['forcetolerance'],
                                  maxiter = input_dict['maxiterations'],
                                  maxeval = input_dict['maxevaluations'],
                                  dmax = input_dict['maxatommotion'],
                                  cutboxvector = input_dict['surface_cutboxvector'])
    
    # Save data model of results
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict,
                               results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)
    
def surface_energy(lammps_command, system, potential, symbols,
                   mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000,
                   maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom'),
                   cutboxvector='c'):
    """
    Evaluates surface formation energies by slicing along one periodic
    boundary of a bulk system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list of str
        The list of element-model symbols for the Potential that correspond to
        system's atypes.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
    cutboxvector : str, optional
        Indicates which of the three system box vectors, 'a', 'b', or 'c', to
        cut with a non-periodic boundary (default is 'c').
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed bulk system.
        - **'dumpfile_surf'** (*str*) - The filename of the LAMMPS dump file
          of the relaxed system containing the free surfaces.
        - **'E_total_base'** (*float*) - The total potential energy of the
          relaxed bulk system.
        - **'E_total_surf'** (*float*) - The total potential energy of the
          relaxed system containing the free surfaces.
        - **'A_surf'** (*float*) - The area of the free surface.
        - **'E_coh'** (*float*) - The cohesive energy of the relaxed bulk
          system.
        - **'E_surf_f'** (*float*) - The computed surface formation energy.
    
    Raises
    ------
    ValueError
        For invalid cutboxvectors.
    """

    # Evaluate perfect system
    system.pbc = [True, True, True]
    perfect = relax_system(lammps_command, system, potential, symbols,
                           mpi_command=mpi_command, etol=etol, ftol=ftol,
                           maxiter=maxiter, maxeval=maxeval, dmax=dmax)
    
    # Extract results from perfect system
    dumpfile_base = 'perfect.dump'
    shutil.move(perfect['finaldumpfile'], dumpfile_base)
    shutil.move('log.lammps', 'perfect-log.lammps')
    E_total_base = perfect['potentialenergy']

    # Set up defect system
    # A_surf is area of parallelogram defined by the two box vectors not along
    # the cutboxvector
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
    surface = relax_system(lammps_command, system, potential, symbols,
                           mpi_command=mpi_command, etol=etol, ftol=ftol,
                           maxiter=maxiter, maxeval=maxeval, dmax=dmax)
    
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
    
def relax_system(lammps_command, system, potential, symbols,
                 mpi_command=None, etol=0.0, ftol=0.0, maxiter=10000,
                 maxeval=100000, dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Sets up and runs the min.in LAMMPS script for performing an energy/force
    minimization to relax a system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    symbols : list of str
        The list of element-model symbols for the Potential that correspond to
        system's atypes.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. (Default is 0.0).
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. (Default is 0.0).
    maxiter : int, optional
        The maximum number of minimization iterations to use (default is 
        10000).
    maxeval : int, optional
        The maximum number of minimization evaluations to use (default is 
        100000).
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration (default is
        0.01 Angstroms).
        
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'logfile'** (*str*) - The name of the LAMMPS log file.
        - **'initialdatafile'** (*str*) - The name of the LAMMPS data file
          used to import an inital configuration.
        - **'initialdumpfile'** (*str*) - The name of the LAMMPS dump file
          corresponding to the inital configuration.
        - **'finaldumpfile'** (*str*) - The name of the LAMMPS dump file
          corresponding to the relaxed configuration.
        - **'potentialenergy'** (*float*) - The total potential energy of
          the relaxed system.
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
    system_info = lmp.atom_data.dump(system, 'system.dat',
                                     units=potential.units,
                                     atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
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
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command,
                     return_style='object')
    
    # Extract output values
    thermo = output.simulations[-1]['thermo']
    results = {}
    results['logfile'] =         'log.lammps'
    results['initialdatafile'] = 'system.dat'
    results['initialdumpfile'] = 'atom.0'
    results['finaldumpfile'] =   'atom.%i' % thermo.Step.values[-1]
    results['potentialenergy'] = uc.set_in_units(thermo.PotEng.values[-1],
                                                 lammps_units['energy'])
    
    return results

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
    iprPy.input.units(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '3 3 3')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
                                                  
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    # None for this calculation
    
    # These are calculation-specific default unitless floats
    # None for this calculation
    
    # These are calculation-specific default floats with units
    # None for this calculation
    
    # Check lammps_command and mpi_command
    iprPy.input.commands(input_dict)
    
    # Set default system minimization parameters
    iprPy.input.minimize(input_dict)
    
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