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
    output['calculation-generalized-planar-fault'] = calc = DM()
    
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
    run_params['stacking_fault_shift_amount'] = input_dict['stacking_fault_shift_amount']
    
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
    
    if input_dict['stacking_fault_model'] is None:
        calc['stacking-fault-parameters'] = sfp = DM()
        sfp['system-family'] = input_dict['system_family']
        sfp['atomman-generalized-fault-parameters'] = DM()
        sfp['atomman-generalized-fault-parameters']['crystallographic-axes'] = DM()
        sfp['atomman-generalized-fault-parameters']['crystallographic-axes']['x-axis'] = input_dict['x-axis']
        sfp['atomman-generalized-fault-parameters']['crystallographic-axes']['y-axis'] = input_dict['y-axis']
        sfp['atomman-generalized-fault-parameters']['crystallographic-axes']['z-axis'] = input_dict['z-axis']
        sfp['atomman-generalized-fault-parameters']['shift'] = input_dict['shift_amount']
        sfp['atomman-generalized-fault-parameters']['cutting-axis'] = input_dict['cutting_axis']
    else:
        calc['stacking-fault-parameters'] = input_dict['stacking_fault_model']['stacking_fault-parameters']
        
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:              
        #Save the cohesive energy
        calc['cohesive-energy'] = DM([('value', uc.get_in_units(results_dict['cohesive_energy'], 
                                                                input_dict['energy_unit'])), 
                                      ('unit', input_dict['energy_unit'])])
        
        #Specify the fault plane
        if input_dict['stacking_fault_model']['stacking_fault-parameters']['atomman-generalized-fault-parameters']['cutting-axis'] == 'x':
            calc['fault-plane'] = input_dict['x-axis']
        if input_dict['stacking_fault_model']['stacking_fault-parameters']['atomman-generalized-fault-parameters']['cutting-axis'] == 'y':
            calc['fault-plane'] = input_dict['y-axis']
        if input_dict['stacking_fault_model']['stacking_fault-parameters']['atomman-generalized-fault-parameters']['cutting-axis'] == 'z':
            calc['fault-plane'] = input_dict['z-axis']
        
        
        #Save the free surface energy
        calc['free-surface-energy'] = DM([('value', uc.get_in_units(results_dict['surface_energy'], 
                                                                    input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')), 
                                          ('unit', input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')])
        #Save the planar fault energy
        calc['planar-fault-energy'] = DM([('value', uc.get_in_units(results_dict['fault_energy'], 
                                                                    input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')), 
                                          ('unit', input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')])

    return output