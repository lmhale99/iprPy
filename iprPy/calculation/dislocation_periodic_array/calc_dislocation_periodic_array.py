#!/usr/bin/env python

# Python script created by Lucas Hale

# Standard library imports
from pathlib import Path
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
record_style = 'calculation_dislocation_periodic_array'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
   
    results_dict = dislocationarray(input_dict['lammps_command'],
                                    input_dict['initialsystem'],
                                    input_dict['potential'],
                                    input_dict['burgersvector'],
                                    input_dict['C'],
                                    mpi_command = input_dict['mpi_command'],
                                    axes = input_dict['transformationmatrix'],
                                    m = input_dict['stroh_m'],
                                    n = input_dict['stroh_n'],
                                    etol = input_dict['energytolerance'],
                                    ftol = input_dict['forcetolerance'],
                                    maxiter = input_dict['maxiterations'],
                                    maxeval = input_dict['maxevaluations'],
                                    dmax = input_dict['maxatommotion'],
                                    annealtemp =  input_dict['annealtemperature'],
                                    annealsteps =  input_dict['annealsteps'],
                                    randomseed = input_dict['randomseed'],
                                    bwidth = input_dict['boundarywidth'],
                                    cutoff = input_dict['duplicatecutoff'],
                                    onlyuselinear = input_dict['onlyuselinear'])
    
    # Save data model of results
    script = Path(__file__).stem
    
    record = iprPy.load_record(record_style)
    record.buildcontent(script, input_dict, results_dict)
    
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def dislocationarray(lammps_command, system, potential, burgers,
                     C, mpi_command=None, axes=None, m=[0,1,0], n=[0,0,1],
                     etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000, dmax=None,
                     annealtemp=0.0, annealsteps=None, randomseed=None,
                     bwidth=None, cutoff=None, onlyuselinear=False):
    """
    Creates and relaxes a dislocation monopole system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The bulk system to add the defect to.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    burgers : list or numpy.array of float
        The burgers vector for the dislocation being added.
    C : atomman.ElasticConstants
        The system's elastic constants.
    mpi_command : str or None, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    axes : numpy.array of float or None, optional
        The 3x3 axes used to rotate the system by during creation.  If given,
        will be used to transform burgers and C from the standard
        crystallographic orientations to the system's Cartesian units.
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
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
    annealtemp : float, optional
        The temperature to perform a dynamic relaxation at. Default is 0.0,
        which will skip the dynamic relaxation.
    annealsteps : int, optional
        The number of time steps to run the dynamic relaxation for.  Default
        is None, which will run for 10000 steps if annealtemp is not 0.0. 
    bshape : str, optional
        The shape to make the boundary region.  Options are 'circle' and
        'rect' (default is 'circle').
    cutoff : float, optional
        Cutoff distance to use for identifying duplicate atoms to remove.
        For dislocations with an edge component, applying the displacements
        creates an extra half-plane of atoms that will have (nearly) identical
        positions with other atoms after altering the boundary conditions.
        Default cutoff value is 0.5 Angstrom.
    useonlylinear : bool, optional
        If False (default) the atoms in the middle of the system will be
        displaced according to an elasticity solution for a dislocation core
        and boundary atoms displaced by a linear gradient.  If True, all 
        atoms are displaced by the linear gradient.
    
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
    # Get script's location
    script_dir = Path(__file__).parent

    # Set default values
    if dmax is None:
        dmax = uc.set_in_units(0.01, 'angstrom')

    # Save base system
    system.dump('atom_dump', f='base.dump')

    # Generate periodic array of dislocations
    if onlyuselinear is False:
        dislsol = am.defect.solve_volterra_dislocation(C, burgers, axes=axes, m=m, n=n)
        dislsystem = am.defect.dislocation_array(system, dislsol=dislsol, bwidth=bwidth,
                                                 cutoff=cutoff)
    else:
        if axes is not None:
            T = am.tools.axes_check(axes)
            burgers = T.dot(burgers)
        dislsystem = am.defect.dislocation_array(system, burgers=burgers, m=m, n=n, cutoff=cutoff)

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = dislsystem.dump('atom_data', f='initial.dat',
                                  units=potential.units,
                                  atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(dislsystem.symbols)
    lammps_variables['anneal_info'] = anneal_info(annealtemp, annealsteps, 
                                                  randomseed, potential.units)
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = dmax
    lammps_variables['bwidth'] = uc.get_in_units(bwidth, lammps_units['length'])
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    template_file = Path(script_dir, 'dislarray_relax.template')
    lammps_script = 'dislarray_relax.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    thermo = output.simulations[-1]['thermo']
    
    # Extract output values
    results_dict = {}
    results_dict['logfile'] = 'log.lammps'
    results_dict['dumpfile_base'] = 'base.dump'
    results_dict['symbols_base'] = system.symbols
    results_dict['dumpfile_disl'] = '%i.dump' % thermo.Step.values[-1]
    results_dict['symbols_disl'] = dislsystem.symbols

    return results_dict

def anneal_info(temperature=0.0, runsteps=None, randomseed=None, units='metal'):
    """
    Generates LAMMPS commands for thermo anneal.
    
    Parameters
    ----------
    temperature : float, optional
        The temperature to relax at (default is 0.0).
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    units : str, optional
        The LAMMPS units style to use (default is 'metal').
    
    Returns
    -------
    str
        The generated LAMMPS input lines for performing a dynamic relax.
        Will be '' if temperature==0.0.
    """    
    # Return nothing if temperature is 0.0 (don't do thermo anneal)
    if temperature == 0.0:
        return ''
    
    # Generate velocity, fix nvt, and run LAMMPS command lines
    else:
        if randomseed is None:
            randomseed = random.randint(1, 900000000)
        if runsteps is None:
            runsteps = 10000
        
        start_temp = 2 * temperature
        tdamp = 100 * lmp.style.timestep(units)
        timestep = lmp.style.timestep(units)
        info = '\n'.join([
            'velocity mid create %f %i mom yes rot yes dist gaussian' % (start_temp, randomseed),
            'fix nvt all nvt temp %f %f %f' % (temperature, temperature,
                                               tdamp),
            'timestep %f' % (timestep),
            'thermo %i' % (runsteps),
            'run %i' % (runsteps),
            ])
    
    return info

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
    iprPy.input.subset('units').interpret(input_dict)
    
    # These are calculation-specific default strings
    input_dict['sizemults'] = input_dict.get('sizemults', '0 3 -20 20 -20 20')
    input_dict['boundaryshape'] = input_dict.get('dislocation_boundaryshape',
                                                  'circle')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
    
    # These are calculation-specific default booleans
    input_dict['onlyuselinear'] = iprPy.input.boolean(input_dict.get('onlyuselinear', False))
    
    # These are calculation-specific default integers
    input_dict['randomseed'] = int(input_dict.get('randomseed',
                                   random.randint(1, 900000000)))
    
    # These are calculation-specific default unitless floats
    input_dict['annealtemperature'] = float(input_dict.get('annealtemperature',
                                                           0.0))
    
    # These are calculation-specific default floats with units
    input_dict['duplicatecutoff'] = iprPy.input.value(input_dict, 'duplicatecutoff',
                                            default_unit=input_dict['length_unit'],
                                            default_term='0.5 angstrom')
    input_dict['boundarywidth'] = iprPy.input.value(input_dict, 'boundarywidth',
                                            default_unit=input_dict['length_unit'],
                                            default_term='10 angstrom')
    
    # These are calculation-specific dependent parameters
    if input_dict['annealtemperature'] == 0.0:
        input_dict['annealsteps'] = int(input_dict.get('annealsteps', 0))
    else:
        input_dict['annealsteps'] = int(input_dict.get('annealsteps', 10000))

    # Check lammps_command and mpi_command
    iprPy.input.subset('lammps_commands').interpret(input_dict)
    
    # Set default system minimization parameters
    iprPy.input.subset('lammps_minimize').interpret(input_dict)
    
    # Load potential
    iprPy.input.subset('lammps_potential').interpret(input_dict)
    
    # Load system
    iprPy.input.subset('atomman_systemload').interpret(input_dict, build=build)
    
    # Load dislocation parameters
    iprPy.input.subset('dislocation').interpret(input_dict)
    
    # Load elastic constants
    if input_dict['onlyuselinear'] is False:
        iprPy.input.subset('atomman_elasticconstants').interpret(input_dict, build=build)
    else:
        input_dict['C'] = None

    # Construct initialsystem by manipulating ucell system
    iprPy.input.subset('atomman_systemmanipulate').interpret(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])