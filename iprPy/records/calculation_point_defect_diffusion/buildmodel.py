from __future__ import division, absolute_import, print_function

import os

import atomman.unitconvert as uc

from DataModelDict import DataModelDict as DM

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
    output['calculation-point-defect-diffusion'] = calc = DM()
    
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
    
    run_params['thermosteps'] = input_dict['thermosteps']
    run_params['runsteps'] = input_dict['runsteps']
    run_params['randomseed'] = input_dict['randomseed']
    
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
    
    # Save defined phase-state info
    calc['phase-state'] = DM()
    calc['phase-state']['temperature'] = DM()
    calc['phase-state']['temperature']['value'] = input_dict['temperature']
    calc['phase-state']['temperature']['unit'] = 'K'
    
    if results_dict is None:
        calc['status'] = 'not calculated'
    else:
        calc['number-of-atoms'] = results_dict['natoms']
        
        # Save measured phase-state info
        calc['measured-phase-state'] = mps = DM()
        mps['temperature'] = DM()
        mps['temperature']['value'] = results_dict['temp']
        if 'temp_std' in results_dict:
            mps['temperature']['error'] = results_dict['temp_std']
        mps['temperature']['unit'] =  'K'
        
        mps['pressure-xx'] = DM()
        mps['pressure-xx']['value'] = uc.get_in_units(results_dict['pxx'],
                                                  input_dict['pressure_unit'])
        mps['pressure-xx']['error'] = uc.get_in_units(results_dict['pxx_std'],
                                                  input_dict['pressure_unit'])
        mps['pressure-xx']['unit'] = input_dict['pressure_unit']
        
        mps['pressure-yy'] = DM()
        mps['pressure-yy']['value'] = uc.get_in_units(results_dict['pyy'],
                                                  input_dict['pressure_unit'])
        mps['pressure-yy']['error'] = uc.get_in_units(results_dict['pyy_std'],
                                                  input_dict['pressure_unit'])
        mps['pressure-yy']['unit'] = input_dict['pressure_unit']

        mps['pressure-zz'] = DM()
        mps['pressure-zz']['value'] = uc.get_in_units(results_dict['pzz'],
                                                  input_dict['pressure_unit'])
        mps['pressure-zz']['error'] = uc.get_in_units(results_dict['pzz_std'],
                                                  input_dict['pressure_unit'])
        mps['pressure-zz']['unit'] = input_dict['pressure_unit']
        
        mps['potential-energy'] = DM()
        mps['potential-energy']['value'] = uc.get_in_units(results_dict['Epot'],
                                                       input_dict['energy_unit'])
        mps['potential-energy']['error'] = uc.get_in_units(results_dict['Epot_std'],
                                                       input_dict['energy_unit'])
        mps['potential-energy']['unit'] =  input_dict['energy_unit']
        
        #Save the diffusion rates
        calc['diffusion-rates'] = dr =DM()
        
        dr['x-direction'] = DM()
        dr['x-direction']['value'] = uc.get_in_units(results_dict['dx'],
                                                     'm^2/s')
        dr['x-direction']['unit'] = 'm^2/s'

        dr['y-direction'] = DM()
        dr['y-direction']['value'] = uc.get_in_units(results_dict['dy'],
                                                     'm^2/s')
        dr['y-direction']['unit'] = 'm^2/s'
        
        dr['z-direction'] = DM()
        dr['z-direction']['value'] = uc.get_in_units(results_dict['dz'],
                                                     'm^2/s')
        dr['z-direction']['unit'] = 'm^2/s'
        
        dr['total'] = DM()
        dr['total']['value'] = uc.get_in_units(results_dict['d'], 'm^2/s')
        dr['total']['unit'] = 'm^2/s'

    return output