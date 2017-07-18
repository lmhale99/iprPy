#!/usr/bin/env python

# Python script created by Lucas Hale and Karina Stetsyuk

# Standard library imports
from __future__ import print_function, division
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
record_style = 'calculation-dynamic-relax'

def main(*args):
    """Main function for running calculation"""

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
                              mpi_command =  input_dict['mpi_command'],
                              ucell =        input_dict['ucell'],
                              p_xx =         input_dict['pressure_xx'], 
                              p_yy =         input_dict['pressure_yy'], 
                              p_zz =         input_dict['pressure_zz'],
                              temperature =  input_dict['temperature'],
                              runsteps =     input_dict['runsteps'],
                              integrator =   input_dict['integrator'],
                              thermosteps =  input_dict['thermosteps'],
                              dumpsteps =    input_dict['dumpsteps'],
                              equilsteps =   input_dict['equilsteps'],
                              randomseed =   input_dict['randomseed'])

    # Save data model of results 
    results = iprPy.buildmodel(record_style, 'calc_' + calc_style, input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

def full_relax(lammps_command, system, potential, symbols, 
               mpi_command=None, ucell=None,
               p_xx=0.0, p_yy=0.0, p_zz=0.0, temperature=0.0, integrator=None,
               runsteps=220000, thermosteps=100, dumpsteps=None, equilsteps=20000, 
               randomseed=None):
    """
    Performs a full dynamic relax on a given system at the given temperature 
    to the specified pressure state. 
    
    Arguments:
    lammps_command -- directory location for lammps executable
    system -- atomman.System to dynamically relax
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential
    symbols -- list of element-model symbols for the Potential that correspond to the System's atypes
    
    Keyword Arguments:
    mpi_command -- MPI command for running LAMMPS in parallel. Default value is None (serial run)
    ucell -- is an atomman.System representing a fundamental unit cell of the system. If not given, 
             ucell will be taken as system
    p_xx, p_yy, p_zz -- tensile pressures to equilibriate to.  Default value is 0.0 for all. 
    temperature -- temperature to relax at. Default value is 0.
    runsteps -- number of integration steps to perform. Default value is 220000.
    integrator -- string giving the integration method to use. Options are 'npt', 'nvt',
                  'nph', 'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
                  Default value is 'nph+l' for temperature = 0, and 'npt' otherwise.    
    thermosteps -- output thermo values every this many steps. Default value is 
                    100.
    dumpsteps -- output dump files every this many steps. Default value is runsteps
                  (only first and last steps are outputted as dump files).
    equilsteps -- the number of timesteps to equilibriate the system for. Only thermo values 
                  associated with timesteps greater than equilsteps will be included in the 
                  mean and standard deviation calculations. Default value is 20000.                   
    randomseed -- random number seed used by LAMMPS for velocity creation and Langevin
                   thermostat. Default value generates a new random integer every time.
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
    if dumpsteps is None:       dumpsteps = runsteps
    
    # Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'init.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['integrator_info'] = integrator_info(integrator=integrator, 
                                                          p_xx=p_xx, p_yy=p_yy, p_zz=p_zz, 
                                                          temperature=temperature, 
                                                          randomseed=randomseed, 
                                                          units=potential.units)
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
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    # Run lammps 
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    # Extract LAMMPS thermo data. 
    results = {}
    thermo = output.simulations[0]['thermo']
    
    # Load relaxed system from dump file
    last_dump_file = str(thermo.Step.values[-1])+'.dump'
    results['system_relaxed'] = lmp.atom_dump.load(last_dump_file) 
    
    # Only consider values where Step >= equilsteps
    thermo = thermo[thermo.Step >= equilsteps]
    results['nsamples'] = len(thermo)
    
    # Get cohesive energy estimates
    natoms = results['system_relaxed'].natoms
    results['E_coh'] = uc.set_in_units(thermo.PotEng.mean(), lammps_units['energy']) / natoms
    results['E_coh_std'] = uc.set_in_units(thermo.PotEng.std(), lammps_units['energy']) / natoms
    
    # Get lattice constant estimates
    results['a_lat'] = uc.set_in_units(thermo.Lx.mean(), lammps_units['length']) / lx_a
    results['b_lat'] = uc.set_in_units(thermo.Ly.mean(), lammps_units['length']) / ly_b
    results['c_lat'] = uc.set_in_units(thermo.Lz.mean(), lammps_units['length']) / lz_c
    results['a_lat_std'] = uc.set_in_units(thermo.Lx.std(), lammps_units['length']) / lx_a
    results['b_lat_std'] = uc.set_in_units(thermo.Ly.std(), lammps_units['length']) / ly_b
    results['c_lat_std'] = uc.set_in_units(thermo.Lz.std(), lammps_units['length']) / lz_c
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
    
    Keyword Arguments:
    integrator -- string giving the integration method to use. Options are 'npt', 'nvt',
                  'nph', 'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
                  Default value is 'nph+l' for temperature = 0, and 'npt' otherwise. 
    p_xx, p_yy, p_zz -- tensile pressures to equilibriate to.  Default value is 0.0 for all. 
    temperature -- temperature to relax at. Default value is 0. 
    randomseed -- random number seed used by LAMMPS for velocity creation and Langevin
                   thermostat. Default value generates a new random integer every time.
    units -- LAMMPS units style to use.
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
    
    if   integrator == 'npt':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join(['velocity all create %f %i' % (start_temp, randomseed),
                              'fix npt all npt temp %f %f %f &' % (T, T, Tdamp),
                              '                x %f %f %f &' % (Px, Px, Pdamp),
                              '                y %f %f %f &' % (Py, Py, Pdamp),
                              '                z %f %f %f' % (Pz, Pz, Pdamp)])
    
    elif integrator == 'nvt':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        int_info = '\n'.join(['velocity all create %f %i' % (start_temp, randomseed),
                              'fix nvt all nvt temp %f %f %f' % (T, T, Tdamp)])
    
    elif integrator == 'nph':
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join(['fix nph all nph x %f %f %f &' % (Px, Px, Pdamp),
                              '                y %f %f %f &' % (Py, Py, Pdamp),
                              '                z %f %f %f' % (Pz, Pz, Pdamp)])
    
    elif integrator == 'nve':
        int_info = 'fix nve all nve'
        
    elif integrator == 'nve+l':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        int_info = '\n'.join(['velocity all create %f %i' % (start_temp, randomseed),
                              'fix nve all nve',
                              'fix langevin all langevin %f %f %f %i' % (T, T, Tdamp, randomseed)])
                              
    elif integrator == 'nph+l':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join([#'velocity all create %f %i' % (start_temp, randomseed),
                              'fix nph all nph x %f %f %f &' % (Px, Px, Pdamp),
                              '                y %f %f %f &' % (Py, Py, Pdamp),
                              '                z %f %f %f' % (Pz, Pz, Pdamp),
                              'fix langevin all langevin %f %f %f %i' % (T, T, Tdamp, randomseed)])                              
    else:
        raise ValueError('Invalid integrator style')
    
    return int_info

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
    input_dict['sizemults'] = input_dict.get('sizemults', '10 10 10')
    input_dict['integrator'] = input_dict.get('integrator', None)
    
    # These are calculation-specific default booleans
    # None for this calculation
    
    # These are calculation-specific default integers
    input_dict['runsteps'] =    int(input_dict.get('runsteps',    220000))
    input_dict['thermosteps'] = int(input_dict.get('thermosteps', 100))
    input_dict['dumpsteps'] =   int(input_dict.get('dumpsteps',   input_dict['runsteps']))
    input_dict['equilsteps'] =  int(input_dict.get('equilsteps',  20000))
    input_dict['randomseed'] =  int(input_dict.get('randomseed',  random.randint(1, 900000000)))
    
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