import os

import atomman.unitconvert as uc

from DataModelDict import DataModelDict as DM

import iprPy

def buildmodel(script, input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-point-defect-formation'] = calc = DM()
    
    #Assign uuid
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
    
    run_params['energytolerance'] = input_dict['energytolerance']
    run_params['forcetolerance'] = DM()
    run_params['forcetolerance']['value'] = uc.get_in_units(input_dict['forcetolerance'], 
                                            input_dict['energy_unit']+'/'+input_dict['length_unit'])
    run_params['forcetolerance']['unit'] =  input_dict['energy_unit']+'/'+input_dict['length_unit']
    run_params['maxiterations']  = input_dict['maxiterations']
    run_params['maxevaluations'] = input_dict['maxevaluations']
    run_params['maxatommotion']  = DM()
    run_params['maxatommotion']['value'] = uc.get_in_units(input_dict['maxatommotion'],
                                           input_dict['length_unit'])
    run_params['maxatommotion']['unit'] =  input_dict['length_unit']
    
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
    
    #Save defect parameters
    calc['point-defect'] = ptd = DM()
    if input_dict['pointdefect_model'] is not None:
        ptd['key'] = input_dict['pointdefect_model']['key']
        ptd['id'] =  input_dict['pointdefect_model']['id']
    
    ptd['system-family'] = input_dict['system_family']
    ptd['calculation-parameter'] = input_dict['calculation_params']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['defect-free-system'] = DM()
        calc['defect-free-system']['artifact'] = DM()
        calc['defect-free-system']['artifact']['file'] = results_dict['dumpfile_base']
        calc['defect-free-system']['artifact']['format'] = 'atom_dump'
        calc['defect-free-system']['symbols'] = input_dict['symbols']
        calc['defect-free-system']['potential-energy'] = DM()
        calc['defect-free-system']['potential-energy']['value'] = uc.get_in_units(results_dict['E_total_base'], 
                                                                  input_dict['energy_unit'])
        calc['defect-free-system']['potential-energy']['unit'] =  input_dict['energy_unit']
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = results_dict['dumpfile_ptd']
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = input_dict['symbols']
        calc['defect-system']['potential-energy'] = DM()
        calc['defect-system']['potential-energy']['value'] = uc.get_in_units(results_dict['E_total_ptd'], 
                                                             input_dict['energy_unit'])
        calc['defect-system']['potential-energy']['unit'] =  input_dict['energy_unit']
        
        #Save the calculation results
        # Save the cohesive energy
        calc['cohesive-energy'] = DM()
        calc['cohesive-energy']['value'] = uc.get_in_units(results_dict['E_coh'], 
                                           input_dict['energy_unit'])
        calc['cohesive-energy']['unit'] =  input_dict['energy_unit']
        
        calc['number-of-atoms'] = results_dict['system_ptd'].natoms
        
        # Save the defect formation energy
        calc['defect-formation-energy'] = DM()
        calc['defect-formation-energy']['value'] = uc.get_in_units(results_dict['E_ptd_f'], 
                                                   input_dict['energy_unit']) 
        calc['defect-formation-energy']['unit'] =  input_dict['energy_unit']
        
        # Save the reconfiguration checks
        calc['reconfiguration-check'] = r_c = DM()
        r_c['has_reconfigured'] = results_dict['has_reconfigured']
        r_c['centrosummation'] = list(results_dict['centrosummation'])
        if 'position_shift' in results_dict:
            r_c['position_shift'] = list(results_dict['position_shift'])
        elif 'db_vect_shift' in results_dict:
            r_c['db_vect_shift'] = list(results_dict['db_vect_shift'])

    return output