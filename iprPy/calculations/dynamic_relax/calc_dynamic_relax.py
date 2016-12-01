#!/usr/bin/env python

#Standard library imports
import os
import sys
import uuid
import math
import random
from copy import deepcopy
import time

#http://www.numpy.org/
import numpy as np

#https://github.com/usnistgov/DataModelDict 
from DataModelDict import DataModelDict as DM

#https://github.com/usnistgov/atomman 
import atomman as am
import atomman.lammps as lmp
import atomman.unitconvert as uc

#https://github.com/usnistgov/iprPy
import iprPy

#https://github.com/choderalab/pymbar
import pymbar

__calc_name__ = os.path.splitext(os.path.basename(__file__))[0]
assert __calc_name__[:5] == 'calc_', 'Calculation file name must start with "calc_"'
__calc_type__ = __calc_name__[5:]

def main(*args):    
    """Main function for running calculation"""

    #Read in parameters from input file
    with open(args[0]) as f:
        input_dict = read_input(f, *args[1:])     

    #Run equilibrum to refine values
    thermo_results = full_relax(input_dict['lammps_command'],
                                input_dict['initial_system'], 
                                input_dict['potential'],
                                input_dict['symbols'],
                                mpi_command =  input_dict['mpi_command'],
                                p_xx =         input_dict['pressure_xx'], 
                                p_yy =         input_dict['pressure_yy'], 
                                p_zz =         input_dict['pressure_zz'],
                                temperature =  input_dict['temperature'],
                                run_steps =    input_dict['run_steps'],
                                integrator =   input_dict['integrator'],
                                thermo_steps = input_dict['thermo_steps'],
                                dump_steps =   input_dict['dump_steps'],
                                random_seed =  input_dict['random_seed'])

    #Process results
    results_dict = process_thermo(thermo_results, input_dict['initial_system'].natoms,
                                  size_mults=input_dict['size_mults'], 
                                  equil_steps=input_dict['equil_steps'])

    #Save data model of results 
    results = data_model(input_dict, results_dict)

    with open('results.json', 'w') as f:
        results.json(fp=f, indent=4)

    
def full_relax(lammps_command, system, potential, symbols, 
               mpi_command=None, p_xx=0.0, p_yy=0.0, p_zz=0.0, temperature=0.0,
               run_steps=100000, integrator=None, thermo_steps=None, dump_steps=None, 
               random_seed=None):
    """
    Performs a full dynamic relax on a given system at the given temperature 
    to the specified pressure state. 
    
    Arguments:
    lammps_command -- directory location for lammps executable
    system -- atomman.System to dynamically relax
    potential -- atomman.lammps.Potential representation of a LAMMPS implemented potential
    symbols -- list of element-model symbols for the Potential that correspond to the System's atypes
    
    Keyword Arguments:
    p_xx, p_yy, p_zz -- tensile pressures to equilibriate to.  Default value is 0.0 for all. 
    temperature -- temperature to relax at. Default value is 0.
    run_steps -- number of integration steps to perform. Default value is 100000.
    integrator -- string giving the integration method to use. Options are 'npt', 'nvt',
                  'nph', 'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
                  Default value is 'nph+l' for temperature = 0, and 'npt' otherwise.    
    thermo_steps -- output thermo values every this many steps. Default value is 
                    run_steps/1000.
    dump_steps -- output dump files every this many steps. Default value is run_steps
                  (only first and last steps are outputted as dump files).
    random_seed -- random number seed used by LAMMPS for velocity creation and Langevin
                   thermostat. Default value generates a new random integer every time.
    """
        
    #Get lammps units
    lammps_units = lmp.style.unit(potential.units)
    
    #Handle default values
    if thermo_steps is None: 
        if thermo_steps >= 1000: thermo_steps = run_steps/1000
        else:                    thermo_steps = 1
    if dump_steps is None:       dump_steps = run_steps
    
    #Define lammps variables
    lammps_variables = {}
    lammps_variables['atomman_system_info'] = lmp.atom_data.dump(system, 'init.dat', 
                                                                 units=potential.units, 
                                                                 atom_style=potential.atom_style)
    lammps_variables['atomman_pair_info'] = potential.pair_info(symbols)
    lammps_variables['integrator_info'] = integrator_info(integrator=integrator, 
                                                          p_xx=p_xx, p_yy=p_yy, p_zz=p_zz, 
                                                          temperature=temperature, 
                                                          random_seed=random_seed, 
                                                          units=potential.units)
    lammps_variables['thermo_steps'] = thermo_steps
    lammps_variables['run_steps'] = run_steps
    lammps_variables['dump_steps'] = dump_steps
    
    #Write lammps input script
    template_file = 'full_relax.template'
    lammps_script = 'full_relax.in'
    with open(template_file) as f:
        template = f.read()
    with open(lammps_script, 'w') as f:
        f.write('\n'.join(iprPy.tools.fill_template(template, lammps_variables, '<', '>')))
    
    #Run lammps 
    output = lmp.run(lammps_command, lammps_script, mpi_command)
    
    #Extract LAMMPS thermo data. 
    thermo = output.find('thermo')
    lx = uc.set_in_units(np.array(thermo['Lx']), lammps_units['length'])
    ly = uc.set_in_units(np.array(thermo['Ly']), lammps_units['length'])
    lz = uc.set_in_units(np.array(thermo['Lz']), lammps_units['length'])
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
    
    return {'step':step, 'lx':lx, 'ly':ly, 'lz':lz, 'pe':pe, 'temp':temp,
            'pxx':pxx, 'pyy':pyy, 'pzz':pzz, 'pxy':pxy, 'pxz':pxz, 'pyz':pyz}


def integrator_info(integrator=None, p_xx=0.0, p_yy=0.0, p_zz=0.0, 
                    temperature=0.0, random_seed=None, units='metal'):
    """
    Generates LAMMPS commands for velocity creation and fix integrators. 
    
    Keyword Arguments:
    integrator -- string giving the integration method to use. Options are 'npt', 'nvt',
                  'nph', 'nve', 'nve+l', 'nph+l'. The +l options use Langevin thermostat.
                  Default value is 'nph+l' for temperature = 0, and 'npt' otherwise. 
    p_xx, p_yy, p_zz -- tensile pressures to equilibriate to.  Default value is 0.0 for all. 
    temperature -- temperature to relax at. Default value is 0. 
    random_seed -- random number seed used by LAMMPS for velocity creation and Langevin
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
    
    #Set default random_seed
    if random_seed is None: random_seed = random.randint(1, 900000000)
    
    if   integrator == 'npt':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join(['velocity all create %f %i' % (start_temp, random_seed),
                              'fix npt all npt temp %f %f %f &' % (T, T, Tdamp),
                              '                x %f %f %f &' % (Px, Px, Pdamp),
                              '                y %f %f %f &' % (Py, Py, Pdamp),
                              '                z %f %f %f' % (Pz, Pz, Pdamp)])
    
    elif integrator == 'nvt':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        int_info = '\n'.join(['velocity all create %f %i' % (start_temp, random_seed),
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
        int_info = '\n'.join(['velocity all create %f %i' % (start_temp, random_seed),
                              'fix nve all nve',
                              'fix langevin all langevin %f %f %f %i' % (T, T, Tdamp, random_seed)])
                              
    elif integrator == 'nph+l':
        start_temp = T*2.+1
        Tdamp = 100 * lmp.style.timestep(units)
        Pdamp = 1000 * lmp.style.timestep(units)
        int_info = '\n'.join([#'velocity all create %f %i' % (start_temp, random_seed),
                              'fix nph all nph x %f %f %f &' % (Px, Px, Pdamp),
                              '                y %f %f %f &' % (Py, Py, Pdamp),
                              '                z %f %f %f' % (Pz, Pz, Pdamp),
                              'fix langevin all langevin %f %f %f %i' % (T, T, Tdamp, random_seed)])                              
    
    else:
        raise ValueError('Invalid integrator style')
    
    return int_info

def process_thermo(thermo_dict, natoms, size_mults=np.array([[0,1],[0,1],[0,1]]), equil_steps=0):
    """Reduce the thermo results down to mean and standard errors."""
    results = {}
    for key in thermo_dict:
        if key == 'step':
            continue
        elif key == 'lx':
            m = (size_mults[0][1]-size_mults[0][0])
            results['a'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equil_steps] / m)
        elif key == 'ly':
            m = (size_mults[1][1]-size_mults[1][0])
            results['b'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equil_steps] / m)
        elif key == 'lz':
            m = (size_mults[2][1]-size_mults[2][0])
            results['c'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equil_steps] / m)
        elif key == 'pe':
            results['E_coh'] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equil_steps] / natoms)
        else:
            results[key] = uncorrelated_mean(thermo_dict[key][thermo_dict['step'] >= equil_steps])
    
    return results
    
def uncorrelated_mean(array):
    mean = np.mean(array)
    g = pymbar.timeseries.statisticalInefficiency(array)
    std = np.std(array) * g**0.5
    
    return np.array([mean, std])    
    
def read_input(f, UUID=None):
    """Reads the calc_*.in input commands for this calculation."""
    
    #Read input file in as dictionary    
    input_dict = iprPy.input.file_to_dict(f)
    
    #set calculation UUID
    if UUID is not None: input_dict['uuid'] = UUID
    else: input_dict['uuid'] = input_dict.get('uuid', str(uuid.uuid4()))
    
    #Process command lines
    assert 'lammps_command' in input_dict, 'lammps_command value not supplied'
    input_dict['mpi_command'] = input_dict.get('mpi_command', None)
    
    #Process potential
    iprPy.input.lammps_potential(input_dict)
    
    #Process default units
    iprPy.input.units(input_dict)
    
    #Process system information
    iprPy.input.system_load(input_dict)
    
    #Process system manipulations
    if input_dict['ucell'] is not None:
        iprPy.input.system_manipulate(input_dict)
    
    #Process run parameters
    #these are string terms
    input_dict['integrator'] = input_dict.get('integrator', None)
    
    #these are integer terms
    input_dict['run_steps'] =    int(input_dict.get('run_steps',    100000))
    input_dict['thermo_steps'] = int(input_dict.get('thermo_steps', input_dict['run_steps']/1000))
    if input_dict['thermo_steps'] == 0 : input_dict['thermo_steps'] = 1
    input_dict['dump_steps'] =   int(input_dict.get('dump_steps',   input_dict['run_steps']))
    input_dict['equil_steps'] =  int(input_dict.get('equil_steps',  10000))
    input_dict['random_seed'] =  int(input_dict.get('random_seed',  
                                    random.randint(1, 900000000)))
    
    #these are unitless float terms
    input_dict['temperature'] = float(input_dict.get('temperature', 0.0))
    
    #these are terms with units
    input_dict['pressure_xx'] = iprPy.input.value_unit(input_dict, 'pressure_xx', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')
    input_dict['pressure_yy'] = iprPy.input.value_unit(input_dict, 'pressure_yy', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')
    input_dict['pressure_zz'] = iprPy.input.value_unit(input_dict, 'pressure_zz', 
                                    default_unit=input_dict['pressure_unit'], 
                                    default_term='0.0 GPa')
    
    return input_dict

def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-dynamic-relax'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['load_options'] = input_dict['load_options']
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['size_mults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['size_mults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['size_mults'][2])
    run_params['thermo_steps'] = input_dict['thermo_steps']
    run_params['run_steps'] = input_dict['run_steps']
    run_params['random_seed'] = input_dict['random_seed']
    run_params['integrator'] = input_dict['integrator']
    
    #Copy over potential data model info
    calc['potential'] = input_dict['potential_model']['LAMMPS-potential']['potential']
    
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

    #Save data model of the initial ucell
    #calc['as-constructed-atomic-system'] = input_dict['ucell'].model(symbols = input_dict['symbols'], 
     #                                                                box_unit = input_dict['length_unit'])['atomic-system']
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
