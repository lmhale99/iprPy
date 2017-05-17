from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def todict(record, full=True, flat=False):

    model = DM(record)

    calc = model['calculation-dynamic-relax']
    params = {}
    params['calc_key'] =        calc['key']
    params['calc_script'] =     calc['calculation']['script']
    
    params['load_options'] =    calc['calculation']['run-parameter']['load_options']
    sizemults =                 calc['calculation']['run-parameter']['size-multipliers']
    
    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    
    params['load'] =          '%s %s' % (calc['system-info']['artifact']['format'],
                                         calc['system-info']['artifact']['file'])
    params['prototype'] =     calc['system-info']['artifact']['family']
    symbols =                 aslist(calc['system-info']['symbols'])
    
    params['temperature'] =   calc['phase-state']['temperature']['value']
    params['pressure_xx'] =   uc.value_unit(calc['phase-state']['pressure-xx'])
    params['pressure_yy'] =   uc.value_unit(calc['phase-state']['pressure-yy'])
    params['pressure_zz'] =   uc.value_unit(calc['phase-state']['pressure-zz'])
    
    if flat is True:
        params['a_mult1'] = sizemults['a'][0]
        params['a_mult2'] = sizemults['a'][1]
        params['b_mult1'] = sizemults['b'][0]
        params['b_mult2'] = sizemults['b'][1]
        params['c_mult1'] = sizemults['c'][0]
        params['c_mult2'] = sizemults['c'][1]
        for i, symbol in enumerate(symbols):
            params['symbol'+str(i+1)] = symbol
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
            avgs = calc['equilibrium-averages']

            params['a_mean'] = uc.value_unit(avgs['a'])
            params['a_std'] = uc.set_in_units(avgs['a']['error'], avgs['a']['unit'])
            
            if 'b' in avgs:
                params['b_mean'] = uc.value_unit(avgs['b'])
                params['b_std'] = uc.set_in_units(avgs['b']['error'], avgs['b']['unit'])
            else: 
                params['b_mean'] = params['a_mean']
                params['b_std'] = params['a_std']

            if 'c' in avgs:
                params['c_mean'] = uc.value_unit(avgs['c'])
                params['c_std'] = uc.set_in_units(avgs['c']['error'], avgs['c']['unit'])
            else: 
                params['c_mean'] = params['a_mean']
                params['c_std'] = params['a_std']
            
            params['E_coh_mean'] = uc.value_unit(avgs['cohesive-energy'])
            params['E_coh_std'] = uc.set_in_units(avgs['cohesive-energy']['error'], avgs['cohesive-energy']['unit'])
            
            params['T_mean'] = uc.value_unit(avgs['temperature'])
            params['T_std'] = uc.set_in_units(avgs['temperature']['error'], avgs['temperature']['unit'])
            
            params['Pxx_mean'] = uc.value_unit(avgs['pressure-xx'])
            params['Pxx_std'] = uc.set_in_units(avgs['pressure-xx']['error'], avgs['pressure-xx']['unit'])
            params['Pyy_mean'] = uc.value_unit(avgs['pressure-yy'])
            params['Pyy_std'] = uc.set_in_units(avgs['pressure-yy']['error'], avgs['pressure-yy']['unit'])
            params['Pzz_mean'] = uc.value_unit(avgs['pressure-zz'])
            params['Pzz_std'] = uc.set_in_units(avgs['pressure-zz']['error'], avgs['pressure-zz']['unit'])
        
    return params 