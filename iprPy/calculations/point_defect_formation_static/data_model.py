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
    run_params['a-multiplyer'] = input_dict['a_mult']
    run_params['b-multiplyer'] = input_dict['b_mult']
    run_params['c-multiplyer'] = input_dict['c_mult']
    run_params['c-multiplyer'] = input_dict['c_mult']
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
    calc['point-defect-parameters'] = input_dict['ptd_model']['point-defect-parameters']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['defect-free-system'] = DM()
        calc['defect-free-system']['artifact'] = DM()
        calc['defect-free-system']['artifact']['file'] = 'perfect.dump'
        calc['defect-free-system']['artifact']['format'] = 'atom_dump'
        calc['defect-free-system']['symbols'] = input_dict['symbols']
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = 'ptd.dump'
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = input_dict['symbols']

        
        #Save the final cohesive energy
        calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['e_coh'], 
                                                                input_dict['energy_unit'])), 
                                      ('unit', input_dict['energy_unit'])])
        calc['defect-formation-energy'] = DM([('value', uc.get_in_units(results_dict['e_ptd_f'], 
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