# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os
from copy import deepcopy

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# iprPy imports
import iprPy

def buildmodel(script, input_dict, results_dict=None):
    """
    Builds a data model of the specified record style based on input (and
    results) parameters.
    
    Parameters
    ----------
    script : str
        The name of the calculation script used.
    input_dict : dict
        Dictionary of all input parameter terms.
    results_dict : dict, optional
        Dictionary containing any results produced by the calculation.
    
    Returns
    -------
    DataModelDict
        Data model consistent with the record's schema format.
    """
    
    # Create the root of the DataModelDict
    output = DM()
    output['calculation-dynamic-relax'] = calc = DM()
    
    # Assign uuid
    calc['key'] = input_dict['calc_key']
    
    # Save calculation parameters
    calc['calculation'] = DM()
    calc['calculation']['iprPy-version'] = iprPy.__version__
    calc['calculation']['LAMMPS-version'] = input_dict['lammps_version']
    
    calc['calculation']['script'] = script
    calc['calculation']['run-parameter'] = run_params = DM()
    
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['sizemults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['sizemults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['sizemults'][2])
    
    run_params['thermosteps'] = input_dict['thermosteps']
    run_params['runsteps'] = input_dict['runsteps']
    run_params['randomseed'] = input_dict['randomseed']
    run_params['integrator'] = input_dict['integrator']
    
    # Copy over potential data model info
    calc['potential-LAMMPS'] = DM()
    calc['potential-LAMMPS']['key'] = input_dict['potential'].key
    calc['potential-LAMMPS']['id'] = input_dict['potential'].id
    calc['potential-LAMMPS']['potential'] = DM()
    calc['potential-LAMMPS']['potential']['key'] = input_dict['potential'].potkey
    calc['potential-LAMMPS']['potential']['id'] = input_dict['potential'].potid
    
    # Save info on system file loaded
    calc['system-info'] = DM()
    calc['system-info']['family'] = input_dict['system_family']
    calc['system-info']['artifact'] = DM()
    calc['system-info']['artifact']['file'] = input_dict['load_file']
    calc['system-info']['artifact']['format'] = input_dict['load_style']
    calc['system-info']['artifact']['load_options'] = input_dict['load_options']
    calc['system-info']['symbol'] = input_dict['symbols']
    
    # Save defined phase-state info
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
        # Save data model of the initial ucell
        system_model = input_dict['ucell'].model(symbols = input_dict['symbols'],
                                                 box_unit = input_dict['length_unit'])
        calc['as-constructed-atomic-system'] = system_model['atomic-system']
        
        # Update ucell to relaxed lattice parameters
        relaxed_ucell = deepcopy(input_dict['ucell'])
        relaxed_ucell.box_set(a=results_dict['a_lat'], b=results_dict['b_lat'], c=results_dict['c_lat'], scale=True)
        
        # Save data model of the relaxed ucell
        system_model = relaxed_ucell.model(symbols = input_dict['symbols'],
                                           box_unit = input_dict['length_unit'],
                                           a_std = results_dict['a_lat_std'],
                                           b_std = results_dict['b_lat_std'],
                                           c_std = results_dict['c_lat_std'])
        calc['relaxed-atomic-system'] = system_model['atomic-system']
        
        calc['number-of-measurements'] = results_dict.get('nsamples', 1)
        
        # Save measured phase-state info
        calc['measured-phase-state'] = mps = DM()
        mps['temperature'] = DM()
        mps['temperature']['value'] = results_dict.get('temp', 0.0)
        if 'temp_std' in results_dict:
            mps['temperature']['error'] = results_dict['temp_std']
        mps['temperature']['unit'] =  'K'
        
        mps['pressure-xx'] = DM()
        mps['pressure-xx']['value'] = -uc.get_in_units(results_dict['stress'][0,0], input_dict['pressure_unit'])
        if 'stress_std' in results_dict:
            mps['pressure-xx']['error'] = -uc.get_in_units(results_dict['stress_std'][0,0], input_dict['pressure_unit'])
        mps['pressure-xx']['unit'] =  input_dict['pressure_unit']
        
        mps['pressure-yy'] = DM()
        mps['pressure-yy']['value'] = -uc.get_in_units(results_dict['stress'][1,1], input_dict['pressure_unit'])
        if 'stress_std' in results_dict:
            mps['pressure-yy']['error'] = -uc.get_in_units(results_dict['stress_std'][1,1], input_dict['pressure_unit'])
        mps['pressure-yy']['unit'] =  input_dict['pressure_unit']
        
        mps['pressure-zz'] = DM()
        mps['pressure-zz']['value'] = -uc.get_in_units(results_dict['stress'][2,2], input_dict['pressure_unit'])
        if 'stress_std' in results_dict:
            mps['pressure-zz']['error'] = -uc.get_in_units(results_dict['stress_std'][2,2], input_dict['pressure_unit'])
        mps['pressure-zz']['unit'] =  input_dict['pressure_unit']
        
        # Save the final cohesive energy
        calc['cohesive-energy'] = DM()
        calc['cohesive-energy']['value'] = uc.get_in_units(results_dict['E_coh'], input_dict['energy_unit'])
        if 'E_coh_std' in results_dict:
            calc['cohesive-energy']['error'] = uc.get_in_units(results_dict['E_coh_std'], input_dict['energy_unit'])
        calc['cohesive-energy']['unit'] =  input_dict['energy_unit']
        
        # Save the final elastic constants
        if 'C_elastic' in results_dict:
            c_family = calc['relaxed-atomic-system']['cell'].keys()[0]
            c_model = results_dict['C_elastic'].model(unit = input_dict['pressure_unit'],
                                                      crystal_system = c_family)
            calc['elastic-constants'] = c_model['elastic-constants']
    
    return output