from __future__ import division, absolute_import, print_function

from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist
from iprPy.input import boolean

def todict(record, full=True, flat=True):
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
    
    calc = model['calculation-point-defect-diffusion']
    params = {}
    params['calc_key'] = calc['key']
    params['calc_script'] = calc['calculation']['script']
    params['iprPy_version'] = calc['calculation']['iprPy-version']
    params['LAMMPS_version'] = calc['calculation']['LAMMPS-version']
    
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
    
    params['pointdefect_key'] = calc['point-defect']['key']
    params['pointdefect_id'] = calc['point-defect']['id']
    
    params['temperature'] = calc['phase-state']['temperature']['value']
    
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
            params['natoms'] = calc['number-of-atoms']
            
            mps = calc['measured-phase-state']
            params['temp_mean'] = uc.value_unit(mps['temperature'])
            params['temp_std'] = uc.set_in_units(mps['temperature']['error'],
                                                 mps['temperature']['unit'])
            params['pxx_mean'] = uc.value_unit(mps['pressure-xx'])
            params['pxx_std'] = uc.set_in_units(mps['pressure-xx']['error'],
                                                mps['pressure-xx']['unit'])
            params['pyy_mean'] = uc.value_unit(mps['pressure-yy'])
            params['pyy_std'] = uc.set_in_units(mps['pressure-yy']['error'],
                                                mps['pressure-yy']['unit'])
            params['pzz_mean'] = uc.value_unit(mps['pressure-zz'])
            params['pzz_std'] = uc.set_in_units(mps['pressure-zz']['error'],
                                                mps['pressure-zz']['unit'])
            params['Epot_mean'] = uc.value_unit(mps['potential-energy'])
            params['Epot_std'] = uc.set_in_units(mps['potential-energy']['error'],
                                                 mps['potential-energy']['unit'])
            
            dr = calc['diffusion-rates']
            params['dx'] = uc.value_unit(dr['x-direction'])
            params['dy'] = uc.value_unit(dr['y-direction'])
            params['dz'] = uc.value_unit(dr['z-direction'])
            params['d'] = uc.value_unit(dr['total'])
    
    return params