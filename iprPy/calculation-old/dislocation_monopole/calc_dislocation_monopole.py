#!/usr/bin/env python
# coding: utf-8

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

# Define calculation metadata
calculation_style = 'dislocation_monopole'
record_style = f'calculation_{calculation_style}'
script = Path(__file__).stem
pkg_name = f'iprPy.calculation.{calculation_style}.{script}'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.input.parse(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
   
    results_dict = dislocationmonopole(input_dict['lammps_command'],
                                       input_dict['ucell'],
                                       input_dict['potential'],
                                       input_dict['C'],
                                       input_dict['dislocation_burgers'],
                                       input_dict['dislocation_ξ_uvw'],
                                       input_dict['dislocation_slip_hkl'],
                                       mpi_command = input_dict['mpi_command'],
                                       m = input_dict['dislocation_m'],
                                       n = input_dict['dislocation_n'],
                                       sizemults = input_dict['sizemults'],
                                       amin = input_dict['amin'],
                                       bmin = input_dict['bmin'],
                                       cmin = input_dict['cmin'],
                                       shift = input_dict['dislocation_shift'],
                                       shiftscale = input_dict['dislocation_shiftscale'],
                                       shiftindex = input_dict['dislocation_shiftindex'],
                                       etol = input_dict['energytolerance'],
                                       ftol = input_dict['forcetolerance'],
                                       maxiter = input_dict['maxiterations'],
                                       maxeval = input_dict['maxevaluations'],
                                       dmax = input_dict['maxatommotion'],
                                       annealtemp =  input_dict['annealtemperature'],
                                       annealsteps =  input_dict['annealsteps'],
                                       randomseed = input_dict['randomseed'],
                                       boundaryshape = input_dict['dislocation_boundaryshape'],
                                       boundarywidth = input_dict['dislocation_boundarywidth'],
                                       boundaryscale = input_dict['dislocation_boundaryscale'])
    
    # Build and save data model of results
    record = iprPy.load_record(record_style)
    record.buildcontent(input_dict, results_dict)
    with open('results.json', 'w') as f:
        record.content.json(fp=f, indent=4)

def dislocationmonopole(lammps_command, ucell, potential, C, burgers, ξ_uvw,
                        slip_hkl, mpi_command=None, m=[0,1,0], n=[0,0,1],
                        sizemults=None, amin=None, bmin=None, cmin=None,
                        shift=None, shiftscale=False, shiftindex=None, tol=1e-8,
                        etol=0.0, ftol=0.0, maxiter=10000, maxeval=100000,
                        dmax=uc.set_in_units(0.01, 'angstrom'),
                        annealtemp=0.0, annealsteps=None, randomseed=None,
                        boundaryshape='cylinder', boundarywidth=0.0, boundaryscale=False):
    """
    Creates and relaxes a dislocation monopole system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    ucell : atomman.System
        The unit cell to use as the seed for generating the dislocation
        monopole system.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    C : atomman.ElasticConstants
        The elastic constants associated with the bulk crystal structure
        for ucell.
    burgers : array-like object
        The dislocation's Burgers vector given as a Miller or
        Miller-Bravais vector relative to ucell.
    ξ_uvw : array-like object
        The dislocation's line direction given as a Miller or
        Miller-Bravais vector relative to ucell.
    slip_hkl : array-like object
        The dislocation's slip plane given as a Miller or Miller-Bravais
        plane relative to ucell.
    mpi_command : str or None, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    m : array-like object, optional
        The m unit vector for the dislocation solution.  m, n, and ξ
        (dislocation line) should be right-hand orthogonal.  Default value
        is [0,1,0] (y-axis).
    n : array-like object, optional
        The n unit vector for the dislocation solution.  m, n, and ξ
        (dislocation line) should be right-hand orthogonal.  Default value
        is [0,0,1] (z-axis). n is normal to the dislocation slip plane.
    sizemults : tuple, optional
        The size multipliers to use when generating the system.  Values are
        limited to being positive integers.  The multipliers for the two
        non-periodic directions must be even.  If not given, the default
        multipliers will be 2 for the non-periodic directions and 1 for the
        periodic direction.
    amin : float, optional
        A minimum thickness to use for the a box vector direction of the
        final system.  Default value is 0.0.  For the non-periodic
        directions, the resulting vector multiplier will be even.  If both
        amin and sizemults is given, then the larger multiplier for the two
        will be used.
    bmin : float, optional
        A minimum thickness to use for the b box vector direction of the
        final system.  Default value is 0.0.  For the non-periodic
        directions, the resulting vector multiplier will be even.  If both
        bmin and sizemults is given, then the larger multiplier for the two
        will be used.
    cmin : float, optional
        A minimum thickness to use for the c box vector direction of the
        final system.  Default value is 0.0.  For the non-periodic
        directions, the resulting vector multiplier will be even.  If both
        cmin and sizemults is given, then the larger multiplier for the two
        will be used.
    shift : float, optional
        A rigid body shift to apply to the rotated cell prior to inserting
        the dislocation.  Should be selected such that the ideal slip plane
        does not correspond to any atomic planes.  Is taken as absolute if
        shiftscale is False, or relative to the rotated cell's box vectors
        if shiftscale is True.  Cannot be given with shiftindex.  If
        neither shift nor shiftindex is given then shiftindex = 0 is used.
    shiftindex : float, optional
        The index of the identified optimum shifts based on the rotated
        cell to use.  Different values allow for the selection of different
        atomic planes neighboring the slip plane.  Note that shiftindex
        values only apply shifts normal to the slip plane; best shifts for
        non-planar dislocations (like bcc screw) may also need a shift in
        the slip plane.  Cannot be given with shiftindex.  If neither shift
        nor shiftindex is given then shiftindex = 0 is used.
    shiftscale : bool, optional
        If False (default), a given shift value will be taken as absolute
        Cartesian.  If True, a given shift will be taken relative to the
        rotated cell's box vectors.
    tol : float
        A cutoff tolerance used with obtaining the dislocation solution.
        Only needs to be changed if there are issues with obtaining a
        solution.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. Default is 0.0.
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. Default is 0.0.
    maxiter : int, optional
        The maximum number of minimization iterations to use. Default is 
        10000.
    maxeval : int, optional
        The maximum number of minimization evaluations to use. Default is 
        100000.
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration. Default is
        0.01 Angstroms.
    annealtemp : float, optional
        The temperature to perform a dynamic relaxation at. Default is 0.0,
        which will skip the dynamic relaxation.
    annealsteps : int, optional
        The number of time steps to run the dynamic relaxation for.  Default
        is None, which will run for 10000 steps if annealtemp is not 0.0.  
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    boundaryshape : str, optional
        Indicates the shape of the boundary region to use.  Options are
        'cylinder' (default) and 'box'.  For 'cylinder', the non-boundary
        region is defined by a cylinder with axis along the dislocation
        line and a radius that ensures the boundary is at least
        boundarywidth thick.  For 'box', the boundary region will be
        exactly boundarywidth thick all around.      
    boundarywidth : float, optional
        The width of the boundary region to apply.  Default value is 0.0,
        i.e. no boundary region.  All atoms in the boundary region will
        have their atype values changed.
    boundaryscale : bool, optional
        If False (Default), the boundarywidth will be taken as absolute.
        If True, the boundarywidth will be taken relative to the magnitude
        of the unit cell's a box vector.
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'dumpfile_base'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed base system.
        - **'symbols_base'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the base system's
          atypes.
        - **'dumpfile_disl'** (*str*) - The filename of the LAMMPS dump file
          for the relaxed dislocation monopole system.
        - **'symbols_disl'** (*list of str*) - The list of element-model
          symbols for the Potential that correspond to the dislocation
          monopole system's atypes.
        - **'dislocation'** (*atomman.defect.Dislocation*) - The Dislocation
          object used to generate the monopole system.
        - **'E_total_disl'** (*float*) - The total potential energy of the
          dislocation monopole system.
    """
    # Construct dislocation configuration generator
    dislocation = am.defect.Dislocation(ucell, C, burgers, ξ_uvw, slip_hkl,
                                        m=m, n=n, shift=shift, shiftindex=shiftindex,
                                        shiftscale=shiftscale, tol=tol)
    
    # Generate the base and dislocation systems
    base_system, disl_system = dislocation.monopole(sizemults=sizemults,
                                                    amin=amin, bmin=bmin, cmin=cmin,
                                                    shift=shift,
                                                    shiftindex=shiftindex,
                                                    shiftscale=shiftscale,
                                                    boundaryshape=boundaryshape,
                                                    boundarywidth=boundarywidth,
                                                    boundaryscale=boundaryscale,
                                                    return_base_system=True)
    
    # Initialize results dict
    results_dict = {}
    
    # Save initial perfect system
    base_system.dump('atom_dump', f='base.dump')
    results_dict['dumpfile_base'] = 'base.dump'
    results_dict['symbols_base'] = base_system.symbols
    
    # Save dislocation generator
    results_dict['dislocation'] = dislocation

    # Relax system
    relaxed = disl_relax(lammps_command, disl_system, potential,
                         mpi_command=mpi_command, annealtemp=annealtemp,
                         annealsteps=annealsteps, randomseed=randomseed,
                         etol=etol, ftol=ftol, maxiter=maxiter, 
                         maxeval=maxeval, dmax=dmax)
    
    # Save relaxed dislocation system with original box vects
    system_disl = am.load('atom_dump', relaxed['dumpfile'], symbols=disl_system.symbols)
    
    system_disl.box_set(vects=disl_system.box.vects, origin=disl_system.box.origin)
    system_disl.dump('atom_dump', f='disl.dump')
    results_dict['dumpfile_disl'] = 'disl.dump'
    results_dict['symbols_disl'] = system_disl.symbols
    
    results_dict['E_total_disl'] = relaxed['E_total']
    
    # Cleanup files
    Path('0.dump').unlink()
    Path(relaxed['dumpfile']).unlink()
    for dumpjsonfile in Path('.').glob('*.dump.json'):
        dumpjsonfile.unlink()
    
    return results_dict

def disl_relax(lammps_command, system, potential,
               mpi_command=None, 
               annealtemp=0.0, annealsteps=None, randomseed=None,
               etol=0.0, ftol=1e-6, maxiter=10000, maxeval=100000,
               dmax=uc.set_in_units(0.01, 'angstrom')):
    """
    Sets up and runs the disl_relax.in LAMMPS script for relaxing a
    dislocation monopole system.
    
    Parameters
    ----------
    lammps_command :str
        Command for running LAMMPS.
    system : atomman.System
        The system to perform the calculation on.
    potential : atomman.lammps.Potential
        The LAMMPS implemented potential to use.
    mpi_command : str, optional
        The MPI command for running LAMMPS in parallel.  If not given, LAMMPS
        will run serially.
    annealtemp : float, optional
        The temperature to perform a dynamic relaxation at. Default is 0.0,
        which will skip the dynamic relaxation.
    annealsteps : int, optional
        The number of time steps to run the dynamic relaxation for.  Default
        is None, which will run for 10000 steps if annealtemp is not 0.0.        
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  Default is None which will select a
        random int between 1 and 900000000.
    etol : float, optional
        The energy tolerance for the structure minimization. This value is
        unitless. Default is 0.0.
    ftol : float, optional
        The force tolerance for the structure minimization. This value is in
        units of force. Default is 0.0.
    maxiter : int, optional
        The maximum number of minimization iterations to use default is 
        10000.
    maxeval : int, optional
        The maximum number of minimization evaluations to use default is 
        100000.
    dmax : float, optional
        The maximum distance in length units that any atom is allowed to relax
        in any direction during a single minimization iteration default is
        0.01 Angstroms.
        
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'logfile'** (*str*) - The name of the LAMMPS log file.
        - **'dumpfile'** (*str*) - The name of the LAMMPS dump file
          for the relaxed system.
        - **'E_total'** (*float*) - The total potential energy for the
          relaxed system.
    """
    # Build filedict if function was called from iprPy
    try:
        assert __name__ == pkg_name
        calc = iprPy.load_calculation(calculation_style)
        filedict = calc.filedict
    except:
        filedict = {}

    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = lmp.checkversion(lammps_command)['date']
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', f='system.dat',
                              potential=potential,
                              return_pair_info=True)
    lammps_variables['atomman_system_pair_info'] = system_info
    lammps_variables['anneal_info'] = anneal_info(annealtemp, annealsteps, 
                                                  randomseed, potential.units)
    lammps_variables['etol'] = etol
    lammps_variables['ftol'] = uc.get_in_units(ftol, lammps_units['force'])
    lammps_variables['maxiter'] = maxiter
    lammps_variables['maxeval'] = maxeval
    lammps_variables['dmax'] = dmax
    lammps_variables['group_move'] = ' '.join(np.array(range(1, system.natypes // 2 + 1), dtype=str))
    
    # Set dump_modify format based on dump_modify_version
    if lammps_date < datetime.date(2016, 8, 3):
        lammps_variables['dump_modify_format'] = '"%d %d %.13e %.13e %.13e %.13e"'
    else:
        lammps_variables['dump_modify_format'] = 'float %.13e'
    
    # Write lammps input script
    template_file = 'disl_relax.template'
    lammps_script = 'disl_relax.in'
    template = iprPy.tools.read_calc_file(template_file, filedict)
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run LAMMPS
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    thermo = output.simulations[-1]['thermo']
    
    # Extract output values
    results = {}
    results['logfile'] = 'log.lammps'
    results['dumpfile'] = '%i.dump' % thermo.Step.values[-1] 
    results['E_total'] = uc.set_in_units(thermo.PotEng.values[-1],
                                         lammps_units['energy'])
    
    return results

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
            'velocity move create %f %i mom yes rot yes dist gaussian' % (start_temp, randomseed),
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
    # Set script's name
    input_dict['script'] = script

    # Set calculation UUID
    if UUID is not None: 
        input_dict['calc_key'] = UUID
    else: 
        input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    # Set default input/output units
    iprPy.input.subset('units').interpret(input_dict)
    
    # These are calculation-specific default strings
    input_dict['dislocation_boundaryshape'] = input_dict.get('dislocation_boundaryshape',
                                                             'cylinder')
    input_dict['forcetolerance'] = input_dict.get('forcetolerance',
                                                  '1.0e-6 eV/angstrom')
    
    # These are calculation-specific default booleans
    input_dict['dislocation_boundaryscale'] = iprPy.input.boolean(input_dict.get('dislocation_boundaryscale',
                                                                                 False))
    
    # These are calculation-specific default integers
    input_dict['randomseed'] = int(input_dict.get('randomseed',
                                   random.randint(1, 900000000)))
    
    # These are calculation-specific default unitless floats
    input_dict['annealtemperature'] = float(input_dict.get('annealtemperature', 0.0))
    
    # These are calculation-specific default floats with units
    input_dict['dislocation_boundarywidth'] = iprPy.input.value(input_dict, 'dislocation_boundarywidth',
                                            default_unit=input_dict['length_unit'],
                                            default_term='0 angstrom')

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
    iprPy.input.subset('atomman_elasticconstants').interpret(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])