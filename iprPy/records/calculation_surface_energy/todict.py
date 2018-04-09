# Standard Python libraries
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

# https://github.com/usnistgov/DataModelDict
from DataModelDict import DataModelDict as DM

# http://www.numpy.org/
import numpy as np

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
    
    calc = model['calculation-surface-energy']
    params = {}
    params['calc_key'] = calc['key']
    params['calc_script'] = calc['calculation']['script']
    params['iprPy_version'] = calc['calculation']['iprPy-version']
    params['LAMMPS_version'] = calc['calculation']['LAMMPS-version']
    
    params['energytolerance']= calc['calculation']['run-parameter']['energytolerance']
    params['forcetolerance'] = calc['calculation']['run-parameter']['forcetolerance']
    params['maxiterations'] = calc['calculation']['run-parameter']['maxiterations']
    params['maxevaluations'] = calc['calculation']['run-parameter']['maxevaluations']
    params['maxatommotion'] = calc['calculation']['run-parameter']['maxatommotion']
    
    sizemults = calc['calculation']['run-parameter']['size-multipliers']
    
    params['potential_LAMMPS_key'] = calc['potential-LAMMPS']['key']
    params['potential_LAMMPS_id'] = calc['potential-LAMMPS']['id']
    params['potential_key'] = calc['potential-LAMMPS']['potential']['key']
    params['potential_id'] = calc['potential-LAMMPS']['potential']['id']
    
    params['load_file'] = calc['system-info']['artifact']['file']
    params['load_style'] = calc['system-info']['artifact']['format']
    params['load_options'] = calc['system-info']['artifact']['load_options']
    params['family'] = calc['system-info']['family']
    symbols = aslist(calc['system-info']['symbol'])
    
    params['surface_key'] = calc['free-surface']['key']
    params['surface_id'] = calc['free-surface']['id']
    
    if flat is True:
        params['a_mult1'] = sizemults['a'][0]
        params['a_mult2'] = sizemults['a'][1]
        params['b_mult1'] = sizemults['b'][0]
        params['b_mult2'] = sizemults['b'][1]
        params['c_mult1'] = sizemults['c'][0]
        params['c_mult2'] = sizemults['c'][1]
        params['symbols'] = ' '.join(symbols)
    else:
        params['sizemults'] = np.array([sizemults['a'], sizemults['b'], sizemults['c']])
        params['symbols'] = symbols
    
    params['status'] = calc.get('status', 'finished')
    
    if full is True:
        if params['status'] == 'error':
            params['error'] = calc['error']
        
        elif params['status'] == 'not calculated':
            pass
        
        else:
            params['E_coh'] = uc.value_unit(calc['cohesive-energy'])
            params['gamma_fs'] = uc.value_unit(calc['free-surface-energy'])
    
    return params