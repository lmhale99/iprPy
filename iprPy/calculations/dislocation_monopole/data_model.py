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
    run_params['size-multipliers'] = DM()
    run_params['size-multipliers']['a'] = list(input_dict['size_mults'][0])
    run_params['size-multipliers']['b'] = list(input_dict['size_mults'][1])
    run_params['size-multipliers']['c'] = list(input_dict['size_mults'][2])
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
    
    #Save data model of the initial ucell
    if input_dict['dislocation_model'] is None:
        calc['dislocation-monopole-parameters'] = dmp = DM()
        dmp['system-family'] = input_dict['system_family']
        dmp['atomman-defect-Stroh-parameters'] = DM()
        dmp['atomman-defect-Stroh-parameters']['burgers'] = input_dict['burgers']
        dmp['atomman-defect-Stroh-parameters']['crystallographic-axes'] = DM()
        dmp['atomman-defect-Stroh-parameters']['crystallographic-axes']['x-axis'] = input_dict['x-axis']
        dmp['atomman-defect-Stroh-parameters']['crystallographic-axes']['y-axis'] = input_dict['y-axis']
        dmp['atomman-defect-Stroh-parameters']['crystallographic-axes']['z-axis'] = input_dict['z-axis']
        dmp['atomman-defect-Stroh-parameters']['shift'] = input_dict['atom_shift']
    else:
        calc['dislocation-monopole-parameters'] = input_dict['dislocation_model']['dislocation-monopole-parameters']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        if input_dict['elastic_constants_model'] is None:
            calc['elastic-constants'] = input_dict['C'].model(unit=input_dict['pressure_unit'])['elastic-constants']
        else:
            calc['elastic-constants'] = input_dict['elastic_constants_model']['elastic-constants']
    
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
        #calc['defect-system']['atomic-system'] = results_dict['defect_system'].model(symbols=input_dict['symbols'])['atomic-system']
        
        #Save the final cohesive energy
        calc['potential-energy'] = DM([('value', uc.get_in_units(results_dict['potential_energy'], 
                                                input_dict['energy_unit'])), 
                                       ('unit', input_dict['energy_unit'])])
        calc['pre-ln-factor'] = DM([('value', uc.get_in_units(results_dict['pre-ln_factor'], 
                                             input_dict['energy_unit']+'/'+input_dict['length_unit'])), 
                                    ('unit', input_dict['energy_unit']+'/'+input_dict['length_unit'])])

    return output