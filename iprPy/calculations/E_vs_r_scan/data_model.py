from DataModelDict import DataModelDict as DM
import os
import atomman.unitconvert as uc
from copy import deepcopy

#Automatically identify the calculation's directory and name
__calc_dir__ = os.path.dirname(os.path.realpath(__file__))   
__calc_type__ =  os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__

def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-cohesive-energy-relation'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['size-multipliers'] = DM()

    run_params['size-multipliers']['a'] = list(input_dict['size_mults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['size_mults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['size_mults'][2])
    run_params['minimum_r'] = input_dict['minimum_r']
    run_params['maximum_r'] = input_dict['maximum_r']
    run_params['number_of_steps_r'] = input_dict['number_of_steps_r']
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
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['cohesive-energy-relation'] = DM()
        calc['cohesive-energy-relation']['r'] = DM()
        calc['cohesive-energy-relation']['r']['value'] = list(uc.get_in_units(results_dict['r_values'], input_dict['length_unit']))
        calc['cohesive-energy-relation']['r']['unit'] = input_dict['length_unit']
        calc['cohesive-energy-relation']['a'] = DM()
        calc['cohesive-energy-relation']['a']['value'] = list(uc.get_in_units(results_dict['a_values'], input_dict['length_unit']))
        calc['cohesive-energy-relation']['a']['unit'] = input_dict['length_unit']
        calc['cohesive-energy-relation']['cohesive-energy'] = DM()
        calc['cohesive-energy-relation']['cohesive-energy']['value'] = list(uc.get_in_units(results_dict['Ecoh_values'], input_dict['energy_unit']))
        calc['cohesive-energy-relation']['cohesive-energy']['unit'] = input_dict['energy_unit']      

        if 'min_cell' in results_dict:
            for cell in results_dict.iteraslist('min_cell'):
                calc.append('minimum-atomic-system', cell.model(symbols = input_dict['symbols'], box_unit = input_dict['length_unit'])['atomic-system'])

    return output