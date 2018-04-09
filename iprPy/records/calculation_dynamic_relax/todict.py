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
    
    calc = model['calculation-dynamic-relax']
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
    
    params['temperature'] = calc['phase-state']['temperature']['value']
    params['pressure_xx'] = uc.value_unit(calc['phase-state']['pressure-xx'])
    params['pressure_yy'] = uc.value_unit(calc['phase-state']['pressure-yy'])
    params['pressure_zz'] = uc.value_unit(calc['phase-state']['pressure-zz'])
    
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
            init = calc['as-constructed-atomic-system']
            params['initial_a'] = uc.value_unit(init.find('a'))
            try:
                params['initial_b'] = uc.value_unit(init.find('b'))
            except:
                params['initial_b'] = params['initial_a']
            try:
                params['initial_c'] = uc.value_unit(init.find('c'))
            except:
                params['initial_c'] = params['initial_a']
            
            final = calc['relaxed-atomic-system']
            params['final_a'] = uc.value_unit(final.find('a'))
            params['final_a_std'] = uc.set_in_units(final.find('a')['error'],
                                                    final.find('a')['unit'])
            try:
                params['final_b'] = uc.value_unit(final.find('b'))
            except:
                params['final_b'] = params['final_a']
            else:
                params['final_b_std'] = uc.set_in_units(final.find('b')['error'],
                                                        final.find('b')['unit'])
            try:
                params['final_c'] = uc.value_unit(final.find('c'))
            except:
                params['final_c'] = params['final_a']
            else:
                params['final_c_std'] = uc.set_in_units(final.find('c')['error'], 
                                                        final.find('c')['unit'])
            
            params['E_cohesive'] = uc.value_unit(calc['cohesive-energy'])
            params['E_cohesive_std'] = uc.set_in_units(calc['cohesive-energy']['error'],
                                                       calc['cohesive-energy']['unit'])
    
    return params