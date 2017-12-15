from __future__ import division, absolute_import, print_function
from collections import OrderedDict

from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np
import pandas as pd

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
    params['halfwidth'] = uc.value_unit(rp['halfwidth'])
    params['xmax'] = uc.value_unit(rp['xmax'])
    params['xnum'] = rp['xnum']
    params['xstep'] = uc.value_unit(rp['xstep'])
    
    params['load_file'] = calc['system-info']['artifact']['file']
    params['load_style'] = calc['system-info']['artifact']['format']
    params['load_options'] = calc['system-info']['artifact']['load_options']
    params['family'] = calc['system-info']['family']
    symbols = aslist(calc['system-info']['symbol'])
    
    params['dislocation_key'] = calc['dislocation-monopole']['key']
    params['dislocation_id'] = calc['dislocation-monopole']['id']
    
    params['gammasurface_calc_key'] = calc['gamma-surface']['calc_key']
    
    pnp = calc['semi-discrete-Peierls-Nabarro']['parameter']
    try:
        K_tensor = uc.value_unit(pnp['K_tensor'])
    except:
        K_tensor = np.nan
    tau = uc.value_unit(pnp['tau'])
    alpha = uc.value_unit(pnp['alpha'])
    beta = uc.value_unit(pnp['beta'])
    params['cdiffelastic'] = pnp['cdiffelastic']
    params['cdiffgradient'] = pnp['cdiffgradient']
    params['cdiffstress'] = pnp['cdiffstress']
    params['cutofflongrange'] = uc.value_unit(pnp['cutofflongrange'])
    params['fullstress'] = pnp['fullstress']
    params['min_method'] = pnp['min_method']
    params['min_options'] = pnp['min_options']
    
    if flat is True:
        params['symbols'] = ' '.join(symbols)
        for i in range(3):
            for j in range(i,3):
                try:
                    params['K'+str(i+1)+str(j+1)] = K_tensor[i,j]
                except:
                    params['K'+str(i+1)+str(j+1)] = np.nan
                params['tau'+str(i+1)+str(j+1)] = tau[i,j]
                params['beta'+str(i+1)+str(j+1)] = beta[i,j]
        if not isinstance(alpha, list):
            alpha = [alpha]
        for i in range(len(alpha)):
            params['alpha'+str(i+1)] = alpha[i]
    else:
        params['symbols'] = symbols
        params['K_tensor'] = K_tensor
        params['tau'] = tau
        params['alpha'] = alpha
        params['beta'] = beta
    
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
                try:
                    params['C'] = am.ElasticConstants(model=model)
                except:
                    params['C'] = np.nan
                if True:
                    params['SDVPN_model'] = DM()
                    params['SDVPN_model']['semi-discrete-Peierls-Nabarro'] = model.find('semi-discrete-Peierls-Nabarro')
                else:
                    params['SDVPN_model'] = np.nan
    
    return params