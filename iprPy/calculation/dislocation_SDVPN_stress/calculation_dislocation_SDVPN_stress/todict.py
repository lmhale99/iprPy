# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)
from collections import OrderedDict

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# http://www.numpy.org/
import numpy as np

# https://pandas.pydata.org/
import pandas as pd

# https://github.com/usnistgov/atomman
import atomman.unitconvert as uc

# iprPy imports
from iprPy.tools import aslist

def todict(record, full=True, flat=False):
    """
    Converts the XML content of a record to a dictionary.
    
    Parameters
    ----------
    record : iprPy.Record
        A record of the record style associated with this function.
    full : bool, optional
        Flag used by the calculation records.  A True value will include
        terms for both the calculation's input and results, while a value
        of False will only include input terms (Default is True).
    flat : bool, optional
        Flag affecting the format of the dictionary terms.  If True, the
        dictionary terms are limited to having only str, int, and float
        values, which is useful for comparisons.  If False, the term
        values can be of any data type, which is convenient for analysis.
        (Default is False).
    
    Returns
    -------
    dict
        A dictionary representation of the record's content.
    """
    model = DM(record)
    
    calc = model['calculation-dislocation-Peierls-Nabarro']
    params = {}
    params['calc_key'] = calc['key']
    params['calc_script'] = calc['calculation']['script']
    params['iprPy_version'] = calc['calculation']['iprPy-version']
    params['atomman_version'] = calc['calculation']['atomman-version']
    
    rp = calc['calculation']['run-parameter']
    params['delta_tau_xy'] = uc.value_unit(rp['delta_tau_xy'])
    params['delta_tau_yy'] = uc.value_unit(rp['delta_tau_yy'])
    params['delta_tau_yz'] = uc.value_unit(rp['delta_tau_yz'])
    params['tausteps'] = rp['tausteps']
    params['cdiffstress'] = rp['cdiffstress']
    params['fullstress'] = rp['fullstress']
    params['min_method'] = rp['minimize_style']
    params['min_options'] = rp['minimize_options']
    
    params['load_file'] = calc['system-info']['artifact']['file']
    params['load_style'] = calc['system-info']['artifact']['format']
    params['load_options'] = calc['system-info']['artifact']['load_options']
    params['family'] = calc['system-info']['family']
    symbols = aslist(calc['system-info']['symbol'])
    
    params['dislocation_key'] = calc['dislocation-monopole']['key']
    params['dislocation_id'] = calc['dislocation-monopole']['id']
    
    params['gammasurface_calc_key'] = calc['gamma-surface']['calc_key']
    params['peierlsnabarro_calc_key'] = calc['Peierls-Nabarro']['calc_key']
    
    if flat is True:
        params['symbols'] = ' '.join(symbols)
    else:
        params['symbols'] = symbols
    
    params['status'] = calc.get('status', 'finished')
    
    if full is True:
        if params['status'] == 'error':
            params['error'] = calc['error']
        
        elif params['status'] == 'not calculated':
            pass
        else:
            if flat is True:
                pass
            else:
                params['tau_xy'] = uc.value_unit(calc['tau-xy'])
                params['tau_yy'] = uc.value_unit(calc['tau-yy'])
                params['tau_yz'] = uc.value_unit(calc['tau-yz'])
                params['total_energy'] = uc.value_unit(calc['total-energy'])
    
    return params