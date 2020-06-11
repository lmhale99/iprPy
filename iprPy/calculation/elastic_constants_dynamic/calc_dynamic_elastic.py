#!/usr/bin/env python

# Standard library imports
import os
import sys
import uuid
import shutil
import random
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

# https://github.com/choderalab/pymbar
import pymbar

__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):
    """Main function for running calculation"""

    # Read in parameters from input file
    with open(args[0]) as f:
        input_dict = read_input(f, *args[1:])
            
    interpret_input(input_dict)
    
    # Run simulations
    results_dict = dynamic_Cij( input_dict['lammps_command'],
                                input_dict['initialsystem'],
                                input_dict['potential'],
                                input_dict['symbols'],
                                mpi_command =  input_dict['mpi_command'],
                                strainrange =  input_dict['strainrange'],
                                temperature =  input_dict['temperature'],
                                runsteps =     input_dict['runsteps'],
                                integrator =   input_dict['integrator'],
                                thermosteps =  input_dict['thermosteps'],
                                dumpsteps =    input_dict['dumpsteps'],
                                restartsteps = input_dict['restartsteps'], 
                                randomseed =   input_dict['randomseed'],
                                equilsteps =   input_dict['equilsteps'])

    # Save data model of results 
    #results = data_model(input_dict, results_dict)

    #with open('results.json', 'w') as f:
    #    results.json(fp=f, indent=4)

def subcalculations(strainrange):
    """Defines the names and properties of sub-calculations"""
    
    strain = strainrange / 2
    
    return {'0':   {'strain': strain * np.array([ 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])},
            'xx+': {'strain': strain * np.array([ 1.0, 0.0, 0.0, 0.0, 0.0, 0.0])},
            'xx-': {'strain': strain * np.array([-1.0, 0.0, 0.0, 0.0, 0.0, 0.0])},
            'yy+': {'strain': strain * np.array([ 0.0, 1.0, 0.0, 0.0, 0.0, 0.0])},
            'yy-': {'strain': strain * np.array([ 0.0,-1.0, 0.0, 0.0, 0.0, 0.0])},
            'zz+': {'strain': strain * np.array([ 0.0, 0.0, 1.0, 0.0, 0.0, 0.0])},
            'zz-': {'strain': strain * np.array([ 0.0, 0.0,-1.0, 0.0, 0.0, 0.0])},
            'xy+': {'strain': strain * np.array([ 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])},
            'xy-': {'strain': strain * np.array([ 0.0, 0.0, 0.0, 0.0, 0.0,-1.0])},
            'xz+': {'strain': strain * np.array([ 0.0, 0.0, 0.0, 0.0, 1.0, 0.0])},
            'xz-': {'strain': strain * np.array([ 0.0, 0.0, 0.0, 0.0,-1.0, 0.0])},
            'yz+': {'strain': strain * np.array([ 0.0, 0.0, 0.0, 1.0, 0.0, 0.0])},
            'yz-': {'strain': strain * np.array([ 0.0, 0.0, 0.0,-1.0, 0.0, 0.0])}}    
            
def dynamic_Cij(lammps_command, system, potential, symbols, 
                mpi_command=None, strainrange=1e-6, temperature=0.0, 
                runsteps=100000, integrator=None, thermosteps=None, 
                dumpsteps=None, restartsteps=None, randomseed=None, equilsteps=None):
    """
    Sets up, runs and processes dynamic simulations for estimating the elastic constants
    
    Arguments:
    lammps_command -- directory location for lammps executable
    system -- atomman.System to dynamically relax
    potential -- atomman.lammps.Potential representation of a LAMMPS 
                 implemented potential
    symbols -- list of element-model symbols for the Potential that correspond
               to the System's atypes
    
    Keyword Arguments:
    mpi_command -- MPI command to use when running LAMMPS.
    strainrange -- strain to apply to the system to estimate the elastic constants.
    temperature -- temperature to relax at. Default value is 0.
    runsteps -- number of integration steps to perform. Default value is 100000.
    integrator -- string giving the integration method to use. Options are limited to 
                  'nvt', 'nve' and 'nve+l'. The +l options use Langevin thermostat.
                  Default value is 'nve+l' for temperature = 0, and 'nvt' otherwise.    
    thermosteps -- output thermo values every this many steps. Default value is 
                    runsteps/1000.
    dumpsteps -- output dump files every this many steps. Default value is runsteps
                  (only first and last steps are outputted as dump files).
    randomseed -- random number seed used by LAMMPS for velocity creation and Langevin
                   thermostat. Default value generates a new random integer every time.
    """
    
    # Save initial info 
    lx0 = system.box.lx
    ly0 = system.box.ly
    lz0 = system.box.lz
    if system.box.xy != 0.0 or system.box.xz != 0.0 or system.box.yz != 0.0:
        raise ValueError('system must be orthorhombic')
    dir0 = os.getcwd()
    
    # Loop over all sub-calculations
    subcalcs = subcalculations(strainrange)
    for calc, calc_dict in subcalcs.iteritems():
        
        # Change to sub-calculation directory
        if not os.path.isdir(calc):
            os.mkdir(calc)
        shutil.copy('full_relax.template', calc)
        os.chdir(calc)

        # Apply strain to the system
        system.box_set(lx = lx0 * (1 + calc_dict['strain'][0]),
                       ly = ly0 * (1 + calc_dict['strain'][1]),
                       lz = lz0 * (1 + calc_dict['strain'][2]),
                       yz = lz0 * calc_dict['strain'][3],
                       xz = lz0 * calc_dict['strain'][4],
                       xy = ly0 * calc_dict['strain'][5],
                       scale = True)
        
        # Perform a dynamic simulation to measure the stress state
        thermo_data = dynamic_stress(lammps_command, system, potential, symbols, 
                                     mpi_command=mpi_command, temperature=temperature, 
                                     runsteps=runsteps, integrator=integrator, 
                                     thermosteps=thermosteps, dumpsteps=dumpsteps, 
                                     restartsteps=restartsteps, randomseed=randomseed)
                                     
        # Process data
        calc_dict.update(process_thermo(thermo_data, system.natoms, equilsteps=equilsteps))
    
        # Return to primary calculation directory
        os.chdir(dir0)
    
    return estimate_elastic_constants(subcalcs)
    
    
        
def dynamic_stress(lammps_command, system, potential, symbols, 
                   mpi_command=None, temperature=0.0, runsteps=100000, 
                   integrator=None, thermosteps=None, dumpsteps=None, 
                   restartsteps=None, randomseed=None):
    """
    Performs a dynamic run on a given system at the given temperature to 
    measure stress state. 
    
    Arguments:
    lammps_command -- directory location for lammps executable
    system -- atomman.System to dynamically relax
    potential -- atomman.lammps.Potential representation of a LAMMPS 
                 implemented potential
    symbols -- list of element-model symbols for the Potential that correspond
               to the System's atypes
    
    Keyword Arguments:
    mpi_command -- MPI command to use when running LAMMPS.
    temperature -- temperature to relax at. Default value is 0.
    runsteps -- number of integration steps to perform. Default value is 100000.
    integrator -- string giving the integration method to use. Options are limited to 
                  'nvt', 'nve' and 'nve+l'. The +l options use Langevin thermostat.
                  Default value is 'nve+l' for temperature = 0, and 'nvt' otherwise.    
    thermosteps -- output thermo values every this many steps. Default value is 
                    runsteps/1000.
    dumpsteps -- output dump files every this many steps. Default value is runsteps
                  (only first and last steps are outputted as dump files).
    randomseed -- random number seed used by LAMMPS for velocity creation and Langevin
                   thermostat. Default value generates a new random integer every time.
    """
    
    assert integrator in ['nvt', 'nve', 'nve+l'], 'Only nvt, nve, and nve+l integrators allowed'
    
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Handle default values
    if thermosteps is None: 
        if thermosteps >= 1000: thermosteps = runsteps/1000
        else:                    thermosteps = 1
    if dumpsteps is None:       dumpsteps = runsteps
    if restartsteps is None:    restartsteps = dumpsteps
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'init.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['integrator_info'] = integrator_info(integrator=integrator, 
                                                          temperature=temperature, 
                                                          randomseed=randomseed, 
                                                          units=potential.units)
    lammps_variables['thermosteps'] = thermosteps
    lammps_variables['runsteps'] = runsteps
    lammps_variables['restartsteps'] = restartsteps
    lammps_variables['dumpsteps'] = dumpsteps
    
    #Check LAMMPS compute stress version
    compute_stress_version = iprPy.tools.lammps_version.compute_stress(lammps_command)
    if compute_stress_version == 0:
        lammps_variables['stressterm'] = 'NULL'
    elif compute_stress_version == 1:
        lammps_variables['stressterm'] = ''
    
    #Write lammps input script
    template_file = 'full_relax.template'
    lammps_script = 'full_relax.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    #Write restart input script
    lammps_restart = 'full_relax_restart.in'
    lammps_variables['atomman_system_info'] = 'read_restart *.restart'
    with open(lammps_restart, 'w') as f:
        f.write(iprPy.tools.filltemplate(template, lammps_variables, '<', '>'))
    
    #Run lammps 
    output = lmp.run(lammps_command, lammps_script, mpi_command, restart_script_name=lammps_restart, flatten_thermo='last')
    
    #Extract LAMMPS thermo data. 
    thermo = output.find('thermo')
    #lx = uc.set_in_units(np.array(thermo['Lx']), lammps_units['length'])
    #ly = uc.set_in_units(np.array(thermo['Ly']), lammps_units['length'])
    #lz = uc.set_in_units(np.array(thermo['Lz']), lammps_units['length'])
    #xy = uc.set_in_units(np.array(thermo['Xy']), lammps_units['length'])
    #xz = uc.set_in_units(np.array(thermo['Xz']), lammps_units['length'])
    #yz = uc.set_in_units(np.array(thermo['Yz']), lammps_units['length'])
    
    pxx = uc.set_in_units(np.array(thermo['Pxx']), lammps_units['pressure'])
    pyy = uc.set_in_units(np.array(thermo['Pyy']), lammps_units['pressure'])
    pzz = uc.set_in_units(np.array(thermo['Pzz']), lammps_units['pressure'])
    pxy = uc.set_in_units(np.array(thermo['Pxy']), lammps_units['pressure'])
    pxz = uc.set_in_units(np.array(thermo['Pxz']), lammps_units['pressure'])
    pyz = uc.set_in_units(np.array(thermo['Pyz']), lammps_units['pressure'])
    
    pe = uc.set_in_units(np.array(thermo['PotEng']), lammps_units['energy'])
    #ke = uc.set_in_units(np.array(thermo['KinEng']), lammps_units['energy'])
    
    temp = np.array(thermo['Temp'])
    step = np.array(thermo['Step'], dtype=int)
    
    return {'step':step, 'pe':pe, 'temp':temp,
            'pxx':pxx, 'pyy':pyy, 'pzz':pzz, 'pxy':pxy, 'pxz':pxz, 'pyz':pyz}

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
    units = LAMMPS units style to use.
    """
    
    #Get lammps units
    lammps_units = lmp.style.unit(units)
    Px = uc.get_in_units(p_xx, lammps_units['pressure'])
    Py = uc.get_in_units(p_yy, lammps_units['pressure'])
    Pz = uc.get_in_units(p_zz, lammps_units['pressure'])
    T = temperature
    
    #Check temperature and set default integrator
    if temperature == 0.0:
        if integrator is None: integrator = 'nph+l'
        assert integrator not in ['npt', 'nvt'], 'npt and nvt cannot run at 0 K'
    elif temperature > 0:
        if integrator is None: integrator = 'npt'
    else:
        raise ValueError('Temperature must be positive')
    
    #Set default randomseed
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

def process_thermo(thermo_dict, natoms, sizemults=np.array([[0,1],[0,1],[0,1]]), equilsteps=0):
    """Reduce the thermo results down to mean and standard errors."""
    results = {}
    for key in thermo_dict:
        if key == 'step':
            continue
        elif key == 'lx':
            m = (sizemults[0][1]-sizemults[0][0])
            results['a'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / m)
        elif key == 'ly':
            m = (sizemults[1][1]-sizemults[1][0])
            results['b'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / m)
        elif key == 'lz':
            m = (sizemults[2][1]-sizemults[2][0])
            results['c'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / m)
        elif key == 'pe':
            results['E_coh'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps] / natoms)
        else:
            results[key] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equilsteps])
    
    return results
    
def uncorrelated_mean(array):
    mean = np.mean(array)

    try:
        # Compute statistical inefficiency
        g = pymbar.timeseries.statisticalInefficiency(array)
    except pymbar.utils.ParameterError as e:
        # Handle case where variance is zero
        if str(e) == 'Sample covariance sigma_AB^2 = 0 -- cannot compute statistical inefficiency':
            std = 0.0
        else: raise e
    else:
        # Adjust standard deviation using g
        std = np.std(array) * g**0.5
    
    return np.array([mean, std])
        
def estimate_elastic_constants(raw_dict):
    """Computes elastic constants using the calculation data."""
    
    results_dict = {}
    
    # Copy the zero strain data to results_dict
    results_dict.update(raw_dict['0'])
    
    # Initialize cij and cij_std arrays
    cij = np.empty((6,6))
    cij_std = np.zeros((6,6))
    
    # Relate the simulation states to strain components
    all_eps = [['xx+', 'xx-'], ['yy+', 'yy-'], ['zz+', 'zz-'], ['yz+', 'yz-'], ['xz+', 'xz-'], ['xy+', 'xy-']]
    
    # Iterate over strain components
    for i, eps in enumerate(all_eps):
        
        # Calculate elastic constants
        delta_strain = raw_dict[eps[0]]['strain'][i] - raw_dict[eps[1]]['strain'][i]
        print(delta_strain)
        delta_stress = - np.array([ raw_dict[eps[0]]['pxx'][0] - raw_dict[eps[1]]['pxx'][0], 
                                    raw_dict[eps[0]]['pyy'][0] - raw_dict[eps[1]]['pyy'][0], 
                                    raw_dict[eps[0]]['pzz'][0] - raw_dict[eps[1]]['pzz'][0], 
                                    raw_dict[eps[0]]['pyz'][0] - raw_dict[eps[1]]['pyz'][0], 
                                    raw_dict[eps[0]]['pxz'][0] - raw_dict[eps[1]]['pxz'][0], 
                                    raw_dict[eps[0]]['pxy'][0] - raw_dict[eps[1]]['pxy'][0] ])
        print np.array_str(delta_stress, precision=4, supress_small=True)
        cij[i] = delta_stress / delta_strain
        
        # Calculate error
        cij_std[i] = np.array([ raw_dict[eps[0]]['pxx'][1]**2 + raw_dict[eps[1]]['pxx'][1]**2,
                                raw_dict[eps[0]]['pyy'][1]**2 + raw_dict[eps[1]]['pyy'][1]**2,
                                raw_dict[eps[0]]['pzz'][1]**2 + raw_dict[eps[1]]['pzz'][1]**2,
                                raw_dict[eps[0]]['pyz'][1]**2 + raw_dict[eps[1]]['pyz'][1]**2,
                                raw_dict[eps[0]]['pxz'][1]**2 + raw_dict[eps[1]]['pxz'][1]**2,
                                raw_dict[eps[0]]['pxy'][1]**2 + raw_dict[eps[1]]['pxy'][1]**2 ])**0.5 / delta_strain

    print
    print np.array_str(cij, precision=4, suppress_small=True)
    print np.array_str(cij_std, precision=4, suppress_small=True)
    
    # Average symmetric terms
    for i in xrange(6):
        for j in xrange(i):
            cij[i,j] = cij[j,i] = (cij[i,j] + cij[j,i]) / 2
            cij_std[i,j] = cij_std[j,i] = (cij_std[i,j] + cij_std[j,i]) / 2
    print
    print np.array_str(cij, precision=4, suppress_small=True)
    print np.array_str(cij_std, precision=4, suppress_small=True)
            
    results_dict['C'] = am.ElasticConstants(Cij=cij)
    results_dict['cij_std'] = cij_std
    
    return results_dict
    
        
def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary
    input_dict = iprPy.tools.parseinput(f, allsingular=True)
    
    #set calculation UUID
    if UUID is not None: input_dict['calc_key'] = UUID
    else: input_dict['calc_key'] = input_dict.get('calc_key', str(uuid.uuid4()))
    
    #Verify required terms are defined
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    assert 'potential_file' in input_dict, 'potential_file value not supplied'
    assert 'load'           in input_dict, 'load value not supplied'
    
    #Assign default values to undefined terms
    iprPy.input.units(input_dict)
    
    input_dict['mpi_command'] =    input_dict.get('mpi_command',    None)
    input_dict['potential_dir'] =  input_dict.get('potential_dir',  '')
    
    input_dict['load_options'] =   input_dict.get('load_options',   None)
    input_dict['box_parameters'] = input_dict.get('box_parameters', None)
    input_dict['symbols'] =        input_dict.get('symbols',        None)
    
    iprPy.input.axes(input_dict)
    iprPy.input.atomshift(input_dict)
    
    input_dict['sizemults'] =      input_dict.get('sizemults',     '10 10 10')
    iprPy.input.sizemults(input_dict)
    
    #these are integer terms
    input_dict['runsteps'] =     int(input_dict.get('runsteps',     100000))
    input_dict['thermosteps'] =  int(input_dict.get('thermosteps',  input_dict['runsteps']//1000))
    if input_dict['thermosteps'] == 0 : input_dict['thermosteps'] = 1
    input_dict['dumpsteps'] =    int(input_dict.get('dumpsteps',    input_dict['runsteps']))
    input_dict['restartsteps'] = int(input_dict.get('restartsteps', input_dict['dumpsteps']))
    input_dict['equilsteps'] =   int(input_dict.get('equilsteps',   10000))
    input_dict['randomseed'] =   int(input_dict.get('randomseed',   random.randint(1, 900000000)))
    
    #these are unitless float terms
    input_dict['temperature'] = float(input_dict.get('temperature', 0.0))
    input_dict['strainrange'] = float(input_dict.get('strainrange', 1e-6))
    
    #these are string terms
    if 'integrator' not in input_dict:
        if input_dict['temperature'] == 0.0: 
            input_dict['integrator'] = 'nve+l'
        elif input_dict['temperature'] > 0:
            input_dict['integrator'] = 'nvt'
        else:
            raise ValueError('temperature cannot be < 0')
    
    return input_dict
    
def interpret_input(input_dict):
    with open(input_dict['potential_file']) as f:
        input_dict['potential'] = lmp.Potential(f, os.path.abspath(input_dict['potential_dir']))
        
    iprPy.input.system_family(input_dict)
    
    iprPy.input.ucell(input_dict)
    
    iprPy.input.initialsystem(input_dict)
        
def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-dynamic-elastic'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    calc['calculation'] = DM()
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
    
    run_params['load_options'] = input_dict['load_options']
    run_params['thermosteps'] = input_dict['thermosteps']
    run_params['runsteps'] = input_dict['runsteps']
    run_params['randomseed'] = input_dict['randomseed']
    run_params['integrator'] = input_dict['integrator']
    
    #Copy over potential data model info
    calc['potential'] = DM()
    calc['potential']['key'] = input_dict['potential'].key
    calc['potential']['id'] = input_dict['potential'].id
    
    #Save info on system file loaded
    system_load = input_dict['load'].split(' ')    
    calc['system-info'] = DM()
    calc['system-info']['artifact'] = DM()
    calc['system-info']['artifact']['file'] = os.path.basename(' '.join(system_load[1:]))
    calc['system-info']['artifact']['format'] = system_load[0]
    calc['system-info']['artifact']['family'] = input_dict['system_family']
    calc['system-info']['symbols'] = input_dict['symbols']
    
    
    #Save phase-state info
    calc['phase-state'] = DM()
    calc['phase-state']['temperature'] = DM()
    calc['phase-state']['temperature']['value'] = input_dict['temperature']
    calc['phase-state']['temperature']['unit'] = 'K'
    
    calc['phase-state']['pressure-xx'] = DM()
    calc['phase-state']['pressure-xx']['value'] = uc.get_in_units(input_dict['pressure_xx'],
                                                                  input_dict['pressure_unit'])
    calc['phase-state']['pressure-xx']['unit'] = input_dict['pressure_unit']
    
    calc['phase-state']['pressure-yy'] = DM()
    calc['phase-state']['pressure-yy']['value'] = uc.get_in_units(input_dict['pressure_yy'],
                                                                  input_dict['pressure_unit'])
    calc['phase-state']['pressure-yy']['unit'] = input_dict['pressure_unit']
    
    calc['phase-state']['pressure-zz'] = DM()
    calc['phase-state']['pressure-zz']['value'] = uc.get_in_units(input_dict['pressure_zz'],
                                                                  input_dict['pressure_unit'])
    calc['phase-state']['pressure-zz']['unit'] = input_dict['pressure_unit']

    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        
        calc['equilibrium-averages'] = avgs = DM()
        avgs['temperature'] = DM()
        avgs['temperature']['value'] = results_dict['temp'][0]
        avgs['temperature']['error'] = results_dict['temp'][1]
        avgs['temperature']['unit'] =  'K'
        
        avgs['pressure-xx'] = DM()
        avgs['pressure-xx']['value'] = uc.get_in_units(results_dict['pxx'][0], input_dict['pressure_unit'])
        avgs['pressure-xx']['error'] = uc.get_in_units(results_dict['pxx'][1], input_dict['pressure_unit'])
        avgs['pressure-xx']['unit'] =  input_dict['pressure_unit']
        
        avgs['pressure-yy'] = DM()
        avgs['pressure-yy']['value'] = uc.get_in_units(results_dict['pyy'][0], input_dict['pressure_unit'])
        avgs['pressure-yy']['error'] = uc.get_in_units(results_dict['pyy'][1], input_dict['pressure_unit'])
        avgs['pressure-yy']['unit'] =  input_dict['pressure_unit']

        avgs['pressure-zz'] = DM()
        avgs['pressure-zz']['value'] = uc.get_in_units(results_dict['pzz'][0], input_dict['pressure_unit'])
        avgs['pressure-zz']['error'] = uc.get_in_units(results_dict['pzz'][1], input_dict['pressure_unit'])
        avgs['pressure-zz']['unit'] =  input_dict['pressure_unit']

        avgs['cohesive-energy'] = DM()
        avgs['cohesive-energy']['value'] = uc.get_in_units(results_dict['E_coh'][0], input_dict['energy_unit'])
        avgs['cohesive-energy']['error'] = uc.get_in_units(results_dict['E_coh'][1], input_dict['energy_unit'])
        avgs['cohesive-energy']['unit'] =  input_dict['energy_unit']

        avgs['a'] = DM()
        avgs['a']['value'] = uc.get_in_units(results_dict['a'][0], input_dict['length_unit'])
        avgs['a']['error'] = uc.get_in_units(results_dict['a'][1], input_dict['length_unit'])
        avgs['a']['unit'] =  input_dict['length_unit']

        avgs['b'] = DM()
        avgs['b']['value'] = uc.get_in_units(results_dict['b'][0], input_dict['length_unit'])
        avgs['b']['error'] = uc.get_in_units(results_dict['b'][1], input_dict['length_unit'])
        avgs['b']['unit'] =  input_dict['length_unit']

        avgs['c'] = DM()
        avgs['c']['value'] = uc.get_in_units(results_dict['c'][0], input_dict['length_unit'])
        avgs['c']['error'] = uc.get_in_units(results_dict['c'][1], input_dict['length_unit'])
        avgs['c']['unit'] =  input_dict['length_unit']
        
    return output
    
if __name__ == '__main__':
    main(*sys.argv[1:])
