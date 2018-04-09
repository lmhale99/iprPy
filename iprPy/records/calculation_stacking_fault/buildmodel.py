# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# iprPy imports
import iprPy

def buildmodel(script, input_dict, results_dict=None):
    """
    Builds a data model of the specified record style based on input (and
    results) parameters.
    
    Parameters
    ----------
    script : str
        The name of the calculation script used.
    input_dict : dict
        Dictionary of all input parameter terms.
    results_dict : dict, optional
        Dictionary containing any results produced by the calculation.
    
    Returns
    -------
    DataModelDict
        Data model consistent with the record's schema format.
    """
    
    #Create the root of the DataModelDict
    output = DM()
    output['calculation-stacking-fault'] = calc = DM()
    
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
    
    run_params['stackingfault_shiftfraction1'] = input_dict['stackingfault_shiftfraction1']
    run_params['stackingfault_shiftfraction2'] = input_dict['stackingfault_shiftfraction2']
    
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
    
    #Save defect model information
    calc['stacking-fault'] = sf = DM()
    
    if input_dict['stackingfault_model'] is not None:
        sf['key'] = input_dict['stackingfault_model']['key']
        sf['id'] =  input_dict['stackingfault_model']['id']
    else:
        sf['key'] = None
        sf['id'] =  None
    
    sf['system-family'] = input_dict['system_family']
    sf['calculation-parameter'] = cp = DM() 
    cp['x_axis'] = input_dict['x_axis']
    cp['y_axis'] = input_dict['y_axis']
    cp['z_axis'] = input_dict['z_axis'] 
    cp['atomshift'] =    input_dict['atomshift']
    cp['cutboxvector'] = input_dict['stackingfault_cutboxvector']
    cp['faultpos'] =     input_dict['stackingfault_faultpos']
    cp['shiftvector1'] = input_dict['stackingfault_shiftvector1']
    cp['shiftvector2'] = input_dict['stackingfault_shiftvector2']
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['defect-free-system'] = DM()
        calc['defect-free-system']['artifact'] = DM()
        calc['defect-free-system']['artifact']['file'] = results_dict['dumpfile_0']
        calc['defect-free-system']['artifact']['format'] = 'atom_dump'
        calc['defect-free-system']['symbols'] = input_dict['symbols']
        calc['defect-free-system']['potential-energy'] = DM()
        calc['defect-free-system']['potential-energy']['value'] = uc.get_in_units(results_dict['E_total_0'], 
                                                                  input_dict['energy_unit'])
        calc['defect-free-system']['potential-energy']['unit'] =  input_dict['energy_unit']
        
        calc['defect-system'] = DM()
        calc['defect-system']['artifact'] = DM()
        calc['defect-system']['artifact']['file'] = results_dict['dumpfile_sf']
        calc['defect-system']['artifact']['format'] = 'atom_dump'
        calc['defect-system']['symbols'] = input_dict['symbols']
        calc['defect-system']['potential-energy'] = DM()
        calc['defect-system']['potential-energy']['value'] = uc.get_in_units(results_dict['E_total_sf'], 
                                                             input_dict['energy_unit'])
        calc['defect-system']['potential-energy']['unit'] =  input_dict['energy_unit']
        
        # Save the stacking fault energy
        calc['stacking-fault-energy'] = DM()
        calc['stacking-fault-energy']['value'] = uc.get_in_units(results_dict['E_gsf'], 
                                                input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2')
        calc['stacking-fault-energy']['unit'] = input_dict['energy_unit']+'/'+input_dict['length_unit']+'^2'
        
        # Save the plane separation
        calc['plane-separation'] = DM()
        calc['plane-separation']['value'] = uc.get_in_units(results_dict['delta_disp'], 
                                            input_dict['length_unit'])
        calc['plane-separation']['unit'] =  input_dict['length_unit']
        
    return output