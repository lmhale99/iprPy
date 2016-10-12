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
    output['calculation-point-defect-formation'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['size-multipliers'] = DM()

    run_params['size-multipliers']['a'] = list(input_dict['size_mults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['size_mults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['size_mults'][2])
    
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
    
    #Save data model of the initial ucell
    calc['point-defect-parameters'] = input_dict['point_defect_model']['point-defect-parameters']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['defect-free-system'] = DM()
        calc['defect-free-system']['artifact'] = DM()
        calc['defect-free-system']['artifact']['file'] = results_dict['dump_file_base']
        calc['defect-free-system']['artifact']['format'] = 'atom_dump'
        calc['defect-free-system']['symbols'] = input_dict['symbols']
        calc['defect-free-system']['potential-energy'] = DM([('value', uc.get_in_units(results_dict['E_total_base'], 
                                                                                        input_dict['energy_unit'])), 
                                                             ('unit', input_dict['energy_unit'])])
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = results_dict['dump_file_ptd']
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = input_dict['symbols']
        calc['defect-system']['potential-energy'] = DM([('value', uc.get_in_units(results_dict['E_total_ptd'], 
                                                                                  input_dict['energy_unit'])), 
                                                        ('unit', input_dict['energy_unit'])])
        
        #Save the calculation results
        calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['E_coh'], 
                                                                input_dict['energy_unit'])), 
                                      ('unit', input_dict['energy_unit'])])
        
        calc['number-of-atoms'] = results_dict['system_ptd'].natoms
        calc['defect-formation-energy'] = DM([('value', uc.get_in_units(results_dict['E_ptd_f'], 
                                                                        input_dict['energy_unit'])), 
                                              ('unit', input_dict['energy_unit'])])
        
        calc['reconfiguration-check'] = r_c = DM()
        r_c['has_reconfigured'] = results_dict['has_reconfigured']
        r_c['centrosummation'] = list(results_dict['centrosummation'])
        if 'position_shift' in results_dict:
            r_c['position_shift'] = list(results_dict['position_shift'])
        elif 'db_vect_shift' in results_dict:
            r_c['db_vect_shift'] = list(results_dict['db_vect_shift'])

    return output