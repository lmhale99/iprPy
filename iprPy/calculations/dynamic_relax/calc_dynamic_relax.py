#!/usr/bin/env python

# Python script created by Lucas Hale and Karina Stetsyuk

# Standard library imports
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
import sys
import uuid
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

# Define calc_style and record_style
calc_style = 'dynamic_relax'
record_style = 'calculation_dynamic_relax'

def main(*args):
    """Main function called when script is executed directly."""
    
    # Read input file in as dictionary
    with open(args[0]) as f:
        input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    # Interpret and process input parameters
    process_input(input_dict, *args[1:])
    
    # Run full_Relax to refine values
    results_dict = full_relax(input_dict['lammps_command'],
                              input_dict['initialsystem'],
                              input_dict['potential'],
                              input_dict['symbols'],
                              mpi_command = input_dict['mpi_command'],
                              ucell = input_dict['ucell'],
                              p_xx = input_dict['pressure_xx'],
                              p_yy = input_dict['pressure_yy'],
                              p_zz = input_dict['pressure_zz'],
                              temperature = input_dict['temperature'],
                              runsteps = input_dict['runsteps'],
                              integrator = input_dict['integrator'],
                              thermosteps = input_dict['thermosteps'],
                              dumpsteps = input_dict['dumpsteps'],
                              equilsteps = input_dict['equilsteps'],
                              randomseed = input_dict['randomseed'])
    
    # Save data model of results
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict,
                               results_dict)
    
    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def full_relax(lammps_command, system, potential, symbols,
               mpi_command=None, ucell=None, p_xx=0.0, p_yy=0.0, p_zz=0.0,
               temperature=0.0, integrator=None, runsteps=220000,
               thermosteps=100, dumpsteps=None, equilsteps=20000,
               randomseed=None):
    """
    Performs a full dynamic relax on a given system at the given temperature
    to the specified pressure state.
    
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
    ucell : atomman.System, optional
        The fundamental unit cell correspodning to system.  This is used to
        convert system dimensions to cell dimensions. If not given, ucell will
        be taken as system.
    p_xx : float, optional
        The value to relax the x tensile pressure component to (default is
        0.0).
    p_yy : float, optional
        The value to relax the y tensile pressure component to (default is
        0.0).
    p_zz : float, optional
        The value to relax the z tensile pressure component to (default is
        0.0).
    temperature : float, optional
        The temperature to relax at (default is 0.0).
    runsteps : int, optional
        The number of integration steps to perform (default is 220000).
    integrator : str or None, optional
        The integration method to use. Options are 'npt', 'nvt', 'nph',
        'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
        (Default is None, which will use 'nph+l' for temperature == 0, and
        'npt' otherwise.)
    thermosteps : int, optional
        Thermo values will be reported every this many steps (default is
        100).
    dumpsteps : int or None, optional
        Dump files will be saved every this many steps (default is None,
        which sets dumpsteps equal to runsteps).
    equilsteps : int, optional
        The number of timesteps at the beginning of the simulation to
        exclude when computing average values (default is 20000).
    randomseed : int or None, optional
        Random number seed used by LAMMPS in creating velocities and with
        the Langevin thermostat.  (Default is None which will select a
        random int between 1 and 900000000.)
    
    Returns
    -------
    dict
        Dictionary of results consisting of keys:
        
        - **'a_lat'** (*float*) - The mean measured a lattice constant.
        - **'b_lat'** (*float*) - The mean measured b lattice constant.
        - **'c_lat'** (*float*) - The mean measured c lattice constant.
        - **'alpha_lat'** (*float*) - The alpha lattice angle.
        - **'beta_lat'** (*float*) - The beta lattice angle.
        - **'gamma_lat'** (*float*) - The gamma lattice angle.
        - **'E_coh'** (*float*) - The mean measured cohesive energy.
        - **'stress'** (*numpy.array*) - The mean measured stress state.
        - **'temp'** (*float*) - The mean measured temperature.
        - **'a_lat_std'** (*float*) - The standard deviation in the measured
          a lattice constant values.
        - **'b_lat_std'** (*float*) - The standard deviation in the measured
          b lattice constant values.
        - **'c_lat_std'** (*float*) - The standard deviation in the measured
          c lattice constant values.
        - **'E_coh_std'** (*float*) - The standard deviation in the measured
          cohesive energy values.
        - **'stress_std'** (*numpy.array*) - The standard deviation in the
          measured stress state values.
        - **'temp_std'** (*float*) - The standard deviation in the measured
          temperature values.
    """
    
    # Set ucell = system if ucell not given
    if ucell is None:
        ucell = system
    
    # Get ratios of lx, ly, and lz of system relative to a of ucell
    lx_a = system.box.a / ucell.box.a
    ly_b = system.box.b / ucell.box.b
    lz_c = system.box.c / ucell.box.c
    alpha = system.box.alpha
    beta =  system.box.beta
    gamma = system.box.gamma
    
    # Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Get lammps version date
    lammps_date = iprPy.tools.check_lammps_version(lammps_command)['lammps_date']
    
    # Handle default values
    if dumpsteps is None:
        dumpsteps = runsteps
    
    # Define lammps variables
    lammps_variables = {}
    system_info = system.dump('atom_data', 'init.dat',
                              units=potential.units,
                              atom_style=potential.atom_style)
    lammps_variables['atomman_system_info'] = system_info
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    integ_info = integrator_info(integrator=integrator,
                                 p_xx=p_xx, p_yy=p_yy, p_zz=p_zz,
                                 temperature=temperature,
                                 randomseed=randomseed,
                                 units=potential.units)
    lammps_variables['integrator_info'] = integ_info
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['dumpsteps'] = dumpsteps
    
    # Set compute stress/atom based on LAMMPS version
    if lammps_date < datetime.date(2014, 2, 12):
        lammps_variables['stressterm'] = ''
    else:
        lammps_variables['stressterm'] = 'NULL'
    
    # Write lammps input script
    template_file = 'full_relax.template'
    lammps_script = 'full_relax.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables,
                                         '<', '>'))
    
    # Run lammps 
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract LAMMPS thermo data. 
    results = {}
    thermo = output.simulations[0]['thermo']
    
    # Load relaxed system from dump file
    last_dump_file = str(thermo.Step.values[-1])+'.dump'
    results['system_relaxed'] = am.load('atom_dump', last_dump_file)
    
    # Only consider values where Step >= equilsteps
    thermo = thermo[thermo.Step >= equilsteps]
    results['nsamples'] = len(thermo)
    
    # Get cohesive energy estimates
    natoms = results['system_relaxed'].natoms
    results['E_coh'] = uc.set_in_units(thermo.PotEng.mean() / natoms,
                                       lammps_units['energy'])
    results['E_coh_std'] = uc.set_in_units(thermo.PotEng.std() / natoms,
                                           lammps_units['energy'])
    
    # Get lattice constant estimates
    results['a_lat'] = uc.set_in_units(thermo.Lx.mean() / lx_a,
                                      lammps_units['length'])
    results['b_lat'] = uc.set_in_units(thermo.Ly.mean() / ly_b,
                                      lammps_units['length'])
    results['c_lat'] = uc.set_in_units(thermo.Lz.mean() / lz_c,
                                       lammps_units['length'])
    results['a_lat_std'] = uc.set_in_units(thermo.Lx.std() / lx_a,
                                           lammps_units['length'])
    results['b_lat_std'] = uc.set_in_units(thermo.Ly.std() / ly_b,
                                           lammps_units['length'])
    results['c_lat_std'] = uc.set_in_units(thermo.Lz.std() / lz_c,
                                           lammps_units['length'])
    results['alpha_lat'] = alpha
    results['beta_lat'] =  beta
    results['gamma_lat'] = gamma
    
    # Get system stress estimates
    pxx = uc.set_in_units(thermo.Pxx.mean(), lammps_units['pressure'])
    pyy = uc.set_in_units(thermo.Pyy.mean(), lammps_units['pressure'])
    pzz = uc.set_in_units(thermo.Pzz.mean(), lammps_units['pressure'])
    pxy = uc.set_in_units(thermo.Pxy.mean(), lammps_units['pressure'])
    pxz = uc.set_in_units(thermo.Pxz.mean(), lammps_units['pressure'])
    pyz = uc.set_in_units(thermo.Pyz.mean(), lammps_units['pressure'])
    results['stress'] = -1 * np.array([[pxx, pxy, pxz],
                                       [pxy, pyy, pyz],
                                       [pxz, pyz, pzz]])
    pxx = uc.set_in_units(thermo.Pxx.std(), lammps_units['pressure'])
    pyy = uc.set_in_units(thermo.Pyy.std(), lammps_units['pressure'])
    pzz = uc.set_in_units(thermo.Pzz.std(), lammps_units['pressure'])
    pxy = uc.set_in_units(thermo.Pxy.std(), lammps_units['pressure'])
    pxz = uc.set_in_units(thermo.Pxz.std(), lammps_units['pressure'])
    pyz = uc.set_in_units(thermo.Pyz.std(), lammps_units['pressure'])
    results['stress_std'] = np.array([[pxx, pxy, pxz],
                                      [pxy, pyy, pyz],
                                      [pxz, pyz, pzz]])
    
    # Get system temperature estimates
    results['temp'] = thermo.Temp.mean()
    results['temp_std'] = thermo.Temp.std()
    
    return results

def integrator_info(integrator=None, p_xx=0.0, p_yy=0.0, p_zz=0.0, 
                    temperature=0.0, randomseed=None, units='metal'):
    """
    Generates LAMMPS commands for velocity creation and fix integrators. 
    
    Parameters
    ----------
    integrator : str or None, optional
        The integration method to use. Options are 'npt', 'nvt', 'nph',
        'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
        (Default is None, which will use 'nph+l' for temperature == 0, and
        'npt' otherwise.)
    p_xx : float, optional
        The value to relax the x tensile pressure component to (default is
        0.0).
    p_yy : float, optional
        The value to relax the y tensile pressure component to (default is
        0.0).
    p_zz : float, optional
        The value to relax the z tensile pressure component to (default is
        0.0).
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
        The generated LAMMPS input lines for velocity create and fix
        integration commands.
    """
    
    # Get lammps units
    lammps_units = lmp.style.unit(units)
    Px = uc.get_in_units(p_xx, lammps_units['pressure'])
    Py = uc.get_in_units(p_yy, lammps_units['pressure'])
    Pz = uc.get_in_units(p_zz, lammps_units['pressure'])
    T = temperature
    
    # Check temperature and set default integrator
    if temperature == 0.0:
        if integrator is None: integrator = 'nph+l'
        assert integrator not in ['npt', 'nvt'], 'npt and nvt cannot run at 0 K'
    elif temperature > 0:
        if integrator is None: integrator = 'npt'
    else:
        raise ValueError('Temperature must be positive')
    
    # Set default randomseed
    if randomseed is None: randomseed = random.randint(1, 900000000)
    
    if integrator == 'npt':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join([
                'velocity all create %f %i' % (start_temp, randomseed),
                'fix npt all npt temp %f %f %f &' % (T, T, Tdamp),
                '                x %f %f %f &' % (Px, Px, Pdamp),
                '                y %f %f %f &' % (Py, Py, Pdamp),
                '                z %f %f %f' % (Pz, Pz, Pdamp),
                ])
    
    elif integrator == 'nvt':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        int_info = '\n'.join([
                'velocity all create %f %i' % (start_temp, randomseed),
                'fix nvt all nvt temp %f %f %f' % (T, T, Tdamp),
                ])
    
    elif integrator == 'nph':
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join([
                'fix nph all nph x %f %f %f &' % (Px, Px, Pdamp),
                '                y %f %f %f &' % (Py, Py, Pdamp),
                '                z %f %f %f' % (Pz, Pz, Pdamp),
                ])
    
    elif integrator == 'nve':
        int_info = 'fix nve all nve'
        
    elif integrator == 'nve+l':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        int_info = '\n'.join([
                'velocity all create %f %i' % (start_temp, randomseed),
                'fix nve all nve',
                'fix langevin all langevin %f %f %f %i' % (T, T, Tdamp,
                                                           randomseed),
                ])

    elif integrator == 'nph+l':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join([
                'fix nph all nph x %f %f %f &' % (Px, Px, Pdamp),
                '                y %f %f %f &' % (Py, Py, Pdamp),
                '                z %f %f %f' % (Pz, Pz, Pdamp),
                'fix langevin all langevin %f %f %f %i' % (T, T, Tdamp,
                                                           randomseed),
                ])
    else:
        raise ValueError('Invalid integrator style')
    
    return int_info

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
    input_dict['sizemults'] = input_dict.get('sizemults', '10 10 10')
    input_dict['integrator'] = input_dict.get('integrator', None)
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['runsteps'] = int(input_dict.get('runsteps', 220000))
    input_dict['thermosteps'] = int(input_dict.get('thermosteps', 100))
    input_dict['dumpsteps'] = int(input_dict.get('dumpsteps',
                                                 input_dict['runsteps']))
    input_dict['equilsteps'] = int(input_dict.get('equilsteps', 20000))
    input_dict['randomseed'] = int(input_dict.get('randomseed',
                                      random.randint(1, 900000000)))
    
    # These are calculation-specific default unitless floats
    input_dict['temperature'] = float(input_dict.get('temperature', 0.0))
    
    # These are calculation-specific default floats with units
    input_dict['pressure_xx'] = iprPy.input.value(input_dict, 'pressure_xx',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    input_dict['pressure_yy'] = iprPy.input.value(input_dict, 'pressure_yy',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    input_dict['pressure_zz'] = iprPy.input.value(input_dict, 'pressure_zz',
                                    default_unit=input_dict['pressure_unit'],
                                    default_term='0.0 GPa')
    
    # Set default integrator based on temperature
    if input_dict['integrator'] is None:
        if input_dict['temperature'] == 0.0:
            input_dict['integrator'] = 'nph+l'
        else:
            input_dict['integrator'] = 'npt'
    
    # Check lammps_command and mpi_command
    iprPy.input.commands(input_dict)
    
    # Load potential
    iprPy.input.potential(input_dict)
    
    # Load ucell system
    iprPy.input.systemload(input_dict, build=build)
    
    # Construct initialsystem by manipulating ucell system
    iprPy.input.systemmanipulate(input_dict, build=build)

if __name__ == '__main__':
    main(*sys.argv[1:])