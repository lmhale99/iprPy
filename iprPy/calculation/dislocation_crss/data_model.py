from DataModelDict import DataModelDict as DM
import os
import atomman.unitconvert as uc
import numpy as np

#Automatically identify the calculation's directory and name
__calc_dir__ = os.path.dirname(os.path.realpath(__file__))   
__calc_type__ =  os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__

def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-critical-resolved-shear-stress'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['chi_angle'] = input_dict['chi_angle']
    run_params['rss_steps'] = input_dict['rss_steps']
    run_params['sigma'] = DM([('value', uc.get_in_units(input_dict['sigma'], input_dict['pressure_unit'])), 
                              ('unit',  input_dict['pressure_unit'])])
    run_params['tau_1'] = DM([('value', uc.get_in_units(input_dict['tau_1'], input_dict['pressure_unit'])), 
                              ('unit',  input_dict['pressure_unit'])])                          
    run_params['tau_2'] = DM([('value', uc.get_in_units(input_dict['tau_2'], input_dict['pressure_unit'])), 
                              ('unit',  input_dict['pressure_unit'])])
    run_params['press'] = DM([('value', uc.get_in_units(input_dict['press'], input_dict['pressure_unit'])), 
                              ('unit',  input_dict['pressure_unit'])])                              
    run_params['energy_tolerance']    = input_dict['energy_tolerance']
    run_params['force_tolerance']     = input_dict['force_tolerance']
    run_params['maximum_iterations']  = input_dict['maximum_iterations']
    run_params['maximum_evaluations'] = input_dict['maximum_evaluations']
    
    #Copy over potential data model info
    calc['potential'] = input_dict['potential']['LAMMPS-potential']['potential']
    
    #Save info on system file loaded
    system_load = input_dict['load'].split(' ')    
    calc['system-info'] = DM()
    calc['system-info']['artifact'] = DM()
    calc['system-info']['artifact']['file'] = os.path.basename(' '.join(system_load[1:]))
    calc['system-info']['artifact']['format'] = system_load[0]
    calc['system-info']['artifact']['family'] = input_dict['system_family']
    calc['system-info']['symbols'] = input_dict['symbols']
    
    #Save crystal orientation
    calc['crystallographic-axes'] = DM()
    calc['crystallographic-axes']['x-axis'] = input_dict['x-axis']
    calc['crystallographic-axes']['y-axis'] = input_dict['y-axis']
    calc['crystallographic-axes']['z-axis'] = input_dict['z-axis']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        if input_dict['elastic_constants_model'] is None:
            calc['elastic-constants'] = input_dict['C'].model(unit=input_dict['pressure_unit'])['elastic-constants']
        else:
            calc['elastic-constants'] = input_dict['elastic_constants_model']['elastic-constants']
    
        calc['rss-energy-relation'] = DM()
        calc['rss-energy-relation']['lammps-step'] = list(results_dict['lammps_step'])
        calc['rss-energy-relation']['rss'] = DM([('value', list(uc.get_in_units(results_dict['rss'], 
                                                          input_dict['pressure_unit']))), 
                                                 ('unit', input_dict['pressure_unit'])])
        calc['rss-energy-relation']['potential-energy'] = DM([('value', list(uc.get_in_units(results_dict['E_total'], 
                                                                       input_dict['energy_unit']))), 
                                                              ('unit', input_dict['energy_unit'])])  

        calc['relaxation-indices'] = list(np.asarray(results_dict['relax_indices'], dtype=int))

    return output