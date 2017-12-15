from __future__ import division, absolute_import, print_function

import os

import numpy as np

import atomman as am
import atomman.unitconvert as uc
from atomman.defect import peierlsnabarro_disregistry

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
    output['calculation-dislocation-Peierls-Nabarro'] = calc = DM()
    
    #Assign uuid
    calc['key'] = input_dict['calc_key']
    
    # Save calculation parameters
    calc['calculation'] = DM()
    calc['calculation']['iprPy-version'] = iprPy.__version__
    calc['calculation']['atomman-version'] = am.__version__
    
    calc['calculation']['script'] = script
    calc['calculation']['run-parameter'] = run_params = DM()
    run_params['delta_tau_xy'] = uc.model(input_dict['delta_tau_xy'],
                                          input_dict['pressure_unit'])
    run_params['delta_tau_yy'] = uc.model(input_dict['delta_tau_yy'],
                                          input_dict['pressure_unit'])
    run_params['delta_tau_yz'] = uc.model(input_dict['delta_tau_yz'],
                                          input_dict['pressure_unit'])
    run_params['tausteps'] = input_dict['tausteps']
    run_params['cdiffstress'] = input_dict['cdiffstress']
    run_params['fullstress'] = input_dict['fullstress']
    run_params['minimize_style'] = input_dict['minimize_style']
    run_params['minimize_options'] = input_dict['minimize_options']
    
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
    
    calc['gamma-surface'] = DM()
    calc['gamma-surface']['calc_key'] = os.path.splitext(
                                         os.path.basename(
                                          input_dict['gammasurface_model']))[0]
    
    calc['Peierls-Nabarro'] = DM()
    calc['Peierls-Nabarro']['calc_key'] = os.path.splitext(
                                         os.path.basename(
                                          input_dict['peierlsnabarro_model']))[0]
    
    if results_dict is None:
        calc['status'] = 'not calculated'
        
    else:
        epl_unit = input_dict['energy_unit']+'/'+input_dict['length_unit']
        calc['tau-xy'] = uc.model(results_dict['tau_xy'],
                                  input_dict['pressure_unit'])
        calc['tau-yy'] = uc.model(results_dict['tau_yy'],
                                  input_dict['pressure_unit'])
        calc['tau-yz'] = uc.model(results_dict['tau_yz'],
                                  input_dict['pressure_unit'])
        calc['total-energy'] = uc.model(results_dict['total_energy'],
                                        epl_unit)
    
    return output