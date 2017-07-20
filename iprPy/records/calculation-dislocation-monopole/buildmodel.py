import os

import atomman.unitconvert as uc

from DataModelDict import DataModelDict as DM

import iprPy

def buildmodel(script, input_dict, results_dict=None):
    """Creates a DataModelDict containing the input and results data""" 
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-dislocation-monopole'] = calc = DM()
    
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
    
    run_params['dislocation_boundarywidth'] = input_dict['boundarywidth']
    run_params['dislocation_boundaryshape'] = input_dict['boundaryshape']
    
    run_params['annealtemperature'] = input_dict['annealtemperature']
    
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
    calc['dislocation-monopole'] = disl = DM()
    if input_dict['dislocation_model'] is not None:
        disl['key'] =            input_dict['dislocation_model']['key']
        disl['id'] =             input_dict['dislocation_model']['id']
        disl['character'] =      input_dict['dislocation_model']['character']
        disl['Burgers-vector'] = input_dict['dislocation_model']['Burgers-vector']
        disl['slip-plane'] =     input_dict['dislocation_model']['slip-plane']
        disl['line-direction'] = input_dict['dislocation_model']['line-direction']
    
    disl['system-family'] = input_dict['system_family']
    disl['calculation-parameter'] = cp = DM() 
    cp['x_axis'] = input_dict['x_axis']
    cp['y_axis'] = input_dict['y_axis']
    cp['z_axis'] = input_dict['z_axis']
    cp['atomshift'] = input_dict['atomshift']
    cp['burgersvector'] = input_dict['dislocation_burgersvector']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['elastic-constants'] = input_dict['C'].model(unit=input_dict['pressure_unit'])['elastic-constants']
    
        calc['base-system'] = DM()
        calc['base-system']['artifact'] = DM()
        calc['base-system']['artifact']['file'] = results_dict['dumpfile_base']
        calc['base-system']['artifact']['format'] = 'atom_dump'
        calc['base-system']['symbols'] = results_dict['symbols_base']
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = results_dict['dumpfile_disl']
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = results_dict['symbols_disl']
        calc['defect-system']['potential-energy'] = DM()
        calc['defect-system']['potential-energy']['value'] = uc.get_in_units(results_dict['E_total_disl'], 
                                                             input_dict['energy_unit'])
        calc['defect-system']['potential-energy']['unit'] =  input_dict['energy_unit']
                                                        
        calc['Stroh-pre-ln-factor'] = DM()
        calc['Stroh-pre-ln-factor']['value'] = uc.get_in_units(results_dict['Stroh_preln'], 
                                              input_dict['energy_unit']+'/'+input_dict['length_unit'])
        calc['Stroh-pre-ln-factor']['unit'] = input_dict['energy_unit']+'/'+input_dict['length_unit']
        
        calc['Stroh-K-tensor'] = []
        Kij = results_dict['Stroh_K_tensor']
        for i in xrange(3):
            for j in xrange(i,3):
                K = DM()
                K['coefficient'] = DM()
                K['coefficient']['value'] = uc.get_in_units(Kij[i,j], input_dict['pressure_unit'])
                K['coefficient']['unit'] = input_dict['pressure_unit']
                K['ij'] = '%i %i' % (i+1, j+1)
                calc['Stroh-K-tensor'].append(K)

    return output