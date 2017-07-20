from DataModelDict import DataModelDict as DM

import atomman.unitconvert as uc
import numpy as np
import pandas as pd

from iprPy.tools import aslist

def todict(record, full=True, flat=False):

    model = DM(record)

    calc = model['calculation-cohesive-energy-relation']
    params = {}
    params['calc_key'] =            calc['key']
    params['calc_script'] =         calc['calculation']['script']
    params['iprPy_version'] =       calc['calculation']['iprPy-version']
    params['LAMMPS_version'] =      calc['calculation']['LAMMPS-version']
    
    params['minimum_r'] =           uc.value_unit(calc['calculation']['run-parameter']['minimum_r'])
    params['maximum_r'] =           uc.value_unit(calc['calculation']['run-parameter']['maximum_r'])
    params['number_of_steps_r'] =   calc['calculation']['run-parameter']['number_of_steps_r']
    
    sizemults =                     calc['calculation']['run-parameter']['size-multipliers']
    
    params['potential_LAMMPS_key'] =    calc['potential-LAMMPS']['key']
    params['potential_LAMMPS_id'] =     calc['potential-LAMMPS']['id']
    params['potential_key'] =           calc['potential-LAMMPS']['potential']['key']
    params['potential_id'] =            calc['potential-LAMMPS']['potential']['id']
    
    params['load_file'] =       calc['system-info']['artifact']['file']
    params['load_style'] =      calc['system-info']['artifact']['format']
    params['load_options'] =    calc['system-info']['artifact']['load_options']
    params['family'] =          calc['system-info']['family']
    symbols =                   aslist(calc['system-info']['symbol'])
    
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
            params['number_min_states'] = 0
            
        elif params['status'] == 'not calculated':
            params['number_min_states'] = 1

        else:
            params['number_min_states'] = len(calc.aslist('minimum-atomic-system'))
            if flat is False:
                plot = calc['cohesive-energy-relation']
                params['e_vs_r_plot'] = pd.DataFrame({'r': uc.value_unit(plot['r']),
                                                      'a': uc.value_unit(plot['a']),
                                                      'E_coh': uc.value_unit(plot['cohesive-energy'])})
            
    return params 