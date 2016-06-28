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
    output['calculation-system-equilibrium'] = calc = DM()
    
    #Assign uuid
    calc['calculation'] = DM()
    calc['calculation']['id'] = input_dict['uuid']
    calc['calculation']['script'] = __calc_name__
    
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['a-multiplyer'] = input_dict['a_mult']
    run_params['b-multiplyer'] = input_dict['b_mult']
    run_params['c-multiplyer'] = input_dict['c_mult']
    run_params['c-multiplyer'] = input_dict['c_mult']
    run_params['thermo_steps'] = input_dict['thermo_steps']
    run_params['pressure'] = input_dict['pressure']
    run_params['run_steps'] = input_dict['run_steps']
    run_params['random_seed'] = input_dict['random_seed']
    run_params['temperature'] = input_dict['temperature']
    
    
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
    
    
    #Save phase-state info
    calc['phase-state'] = DM()
    calc['phase-state']['temperature'] = DM([('value', input_dict['temperature']), ('unit', 'K')])
    calc['phase-state']['pressure'] = DM([('value', uc.get_in_units(input_dict['pressure'],
                                                                       input_dict['pressure_unit'])), 
                                                       ('unit', input_dict['pressure_unit'])])                                                     
    
    #Save data model of the initial ucell
    calc['as-constructed-atomic-system'] = input_dict['ucell'].model(symbols = input_dict['symbols'], 
                                                                     box_unit = input_dict['length_unit'])['atomic-system']
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        
        calc['results'] = results_dict
        
        #Update ucell to relaxed lattice parameters
        #relaxed_ucell = deepcopy(input_dict['ucell'])
        #relaxed_ucell.box_set(a = results_dict['cell_new'].box.a / input_dict['a_mult'],
        #                      b = results_dict['cell_new'].box.b / input_dict['b_mult'],
        #                      c = results_dict['cell_new'].box.c / input_dict['c_mult'],
        #                      scale = True)
        
        #Save data model of the relaxed ucell                      
        #calc['relaxed-atomic-system'] = relaxed_ucell.model(symbols = input_dict['symbols'], 
        #                                                    box_unit = input_dict['length_unit'])['atomic-system']
        
        #Save the final cohesive energy
        #calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['ecoh'], 
        #                                                                   input_dict['energy_unit'])), 
        #                                         ('unit', input_dict['energy_unit'])])
        
        #Save the final elastic constants
        #c_family = calc['relaxed-atomic-system']['cell'].keys()[0]
        #calc['elastic-constants'] = results_dict['C'].model(unit = input_dict['pressure_unit'], 
        #                                                    crystal_system = c_family)['elastic-constants']

    return output