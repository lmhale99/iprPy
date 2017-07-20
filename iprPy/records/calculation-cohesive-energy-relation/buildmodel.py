import os

import atomman.unitconvert as uc

from DataModelDict import DataModelDict as DM

import iprPy

def buildmodel(script, input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    # Create the root of the DataModelDict
    output = DM()
    output['calculation-cohesive-energy-relation'] = calc = DM()
    
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
    
    run_params['minimum_r'] = DM()
    run_params['minimum_r']['value'] = uc.get_in_units(input_dict['minimum_r'], input_dict['length_unit'])
    run_params['minimum_r']['unit'] = input_dict['length_unit']
    run_params['maximum_r'] = DM()
    run_params['maximum_r']['value'] = uc.get_in_units(input_dict['maximum_r'], input_dict['length_unit'])
    run_params['maximum_r']['unit'] = input_dict['length_unit']
    run_params['number_of_steps_r'] = input_dict['number_of_steps_r']
    
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
            for cell in results_dict['min_cell']:
                calc.append('minimum-atomic-system', cell.model(symbols = input_dict['symbols'], box_unit = input_dict['length_unit'])['atomic-system'])

    return output    