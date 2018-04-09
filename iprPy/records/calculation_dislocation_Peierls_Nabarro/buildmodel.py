# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
import os

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# https://github.com/usnistgov/atomman
import atomman as am
import atomman.unitconvert as uc
from atomman.defect import pn_arctan_disregistry

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
    output['calculation-dislocation-Peierls-Nabarro'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    
    # Save calculation parameters
    calc['calculation'] = DM()
    calc['calculation']['iprPy-version'] = iprPy.__version__
    calc['calculation']['atomman-version'] = am.__version__
    
    calc['calculation']['script'] = script
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['halfwidth'] = uc.model(input_dict['halfwidth'], input_dict['length_unit'])
    
    x, idisreg = pn_arctan_disregistry(xmax=input_dict['xmax'], xnum=input_dict['xnum'], xstep=input_dict['xstep'])
    run_params['xmax'] = x.max()
    run_params['xnum'] = len(x)
    run_params['xstep'] = x[1]-x[0]
    
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
        disl['key'] = input_dict['dislocation_model']['key']
        disl['id'] = input_dict['dislocation_model']['id']
        disl['character'] = input_dict['dislocation_model']['character']
        disl['Burgers-vector'] = input_dict['dislocation_model']['Burgers-vector']
        disl['slip-plane'] = input_dict['dislocation_model']['slip-plane']
        disl['line-direction'] = input_dict['dislocation_model']['line-direction']
    
    disl['system-family'] = input_dict['system_family']
    disl['calculation-parameter'] = cp = DM()
    cp['x_axis'] = input_dict['x_axis']
    cp['y_axis'] = input_dict['y_axis']
    cp['z_axis'] = input_dict['z_axis']
    cp['atomshift'] = input_dict['atomshift']
    cp['burgersvector'] = input_dict['dislocation_burgersvector']
    
    calc['gamma-surface'] = DM()
    calc['gamma-surface']['calc_key'] = os.path.splitext(
                                         os.path.basename(
                                          input_dict['gammasurface_model']))[0]
    
    calc['stress-state'] = uc.model(input_dict['tau'], input_dict['pressure_unit'])
    
    if results_dict is None:
        calc['status'] = 'not calculated'
        
        # Fill in model input parameters
        calc['semi-discrete-Peierls-Nabarro'] = sdpn = DM()
        sdpn['parameter'] = params = DM()
        params['tau'] = uc.model(input_dict['tau'], input_dict['pressure_unit'])
        params['alpha'] = uc.model(input_dict['alpha'],
                            input_dict['pressure_unit']+'/'+input_dict['length_unit'])
        params['beta'] = uc.model(input_dict['beta'],
                            input_dict['pressure_unit']+'*'+input_dict['length_unit'])
        params['cdiffelastic'] = input_dict['cdiffelastic']
        params['cdiffgradient'] = input_dict['cdiffgradient']
        params['cdiffstress'] = input_dict['cdiffstress']
        params['cutofflongrange'] = uc.model(input_dict['cutofflongrange'], input_dict['length_unit'])
        params['fullstress'] = input_dict['fullstress']
        params['min_method'] = input_dict['minimize_style']
        params['min_options'] = input_dict['minimize_options']
    else:
        calc['elastic-constants'] = input_dict['C'].model(unit=input_dict['pressure_unit'])['elastic-constants']
        
        pnsolution = results_dict['SDPN_solution']
        calc['semi-discrete-Peierls-Nabarro'] = pnsolution.model(length_unit=input_dict['length_unit'],
                                                                 energy_unit=input_dict['energy_unit'],
                                                                 pressure_unit=input_dict['pressure_unit'],
                                                                 include_gamma=False)['semi-discrete-Peierls-Nabarro']
        
        e_per_l_unit = input_dict['energy_unit'] + '/' + input_dict['length_unit']
        calc['misfit-energy'] = uc.model(pnsolution.misfit_energy(), e_per_l_unit)
        calc['elastic-energy'] = uc.model(pnsolution.elastic_energy(), e_per_l_unit)
        calc['long-range-energy'] = uc.model(pnsolution.longrange_energy(), e_per_l_unit)
        calc['stress-energy'] = uc.model(pnsolution.stress_energy(), e_per_l_unit)
        calc['gradient-energy'] = uc.model(pnsolution.gradient_energy(), e_per_l_unit)
        calc['nonlocal-energy'] = uc.model(pnsolution.nonlocal_energy(), e_per_l_unit)
        calc['total-energy'] = uc.model(pnsolution.total_energy(), e_per_l_unit)
    
    return output