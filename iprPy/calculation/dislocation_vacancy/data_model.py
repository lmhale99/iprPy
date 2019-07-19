from DataModelDict import DataModelDict as DM
import os
import atomman.unitconvert as uc

#Automatically identify the calculation's directory and name
__calc_dir__ = os.path.dirname(os.path.realpath(__file__))   
__calc_type__ =  os.path.basename(__calc_dir__)
__calc_name__ = 'calc_' + __calc_type__

def data_model(input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-dislocation-monopole'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['a-multiplyer'] = input_dict['a_mult']
    run_params['b-multiplyer'] = input_dict['b_mult']
    run_params['c-multiplyer'] = input_dict['c_mult']
    run_params['anneal_temperature'] = input_dict['anneal_temperature']
    run_params['boundary_width'] = input_dict['boundary_width']
    run_params['boundary_shape'] = input_dict['boundary_shape']
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
    
    calc['elastic-constants'] = input_dict['elastic_constants_model'].find('elastic-constants')
    
    #Save data model of the initial ucell
    calc['dislocation-monopole-parameters'] = input_dict['dislocation_model']['dislocation-monopole-parameters']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['defect-free-system'] = DM()
        calc['defect-free-system']['artifact'] = DM()
        calc['defect-free-system']['artifact']['file'] = 'base.dat'
        calc['defect-free-system']['artifact']['format'] = 'atom_data'
        old_symbols = input_dict['symbols'][:len(input_dict['symbols'])/2]
        if len(old_symbols) == 1: old_symbols = old_symbols[0]
        calc['defect-free-system']['symbols'] = old_symbols
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = 'disl.dump'
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = input_dict['symbols']

        
        #Save the final cohesive energy
        calc['potential-energy'] = DM([('value', uc.get_in_units(results_dict['potential_energy'], 
                                                input_dict['energy_unit'])), 
                                       ('unit', input_dict['energy_unit'])])
        calc['pre-ln-factor'] = DM([('value', uc.get_in_units(results_dict['pre-ln_factor'], 
                                             input_dict['energy_unit']+'/'+input_dict['length_unit'])), 
                                    ('unit', input_dict['energy_unit']+'/'+input_dict['length_unit'])])

    return output