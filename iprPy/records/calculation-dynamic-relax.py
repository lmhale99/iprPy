from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-calculation-dynamic-relax.xsd')

def todict(record, full=True):

    model = DM(record)

    calc = model['calculation-dynamic-relax']
    params = {}
    params['calc_key'] =     calc['key']
    params['calc_script'] =  calc['calculation']['script']
    params['load_options'] = calc['calculation']['run-parameter']['load_options']
    params['sizemults'] =    calc['calculation']['run-parameter']['size-multipliers']
    params['sizemults'] =    np.array([params['sizemults']['a'], 
                                       params['sizemults']['b'], 
                                       params['sizemults']['c']])
    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    params['load'] =          '%s %s' % (calc['system-info']['artifact']['format'],
                                         calc['system-info']['artifact']['file'])
    params['prototype'] =     calc['system-info']['artifact']['family']
    params['symbols'] =       aslist(calc['system-info']['symbols'])
    params['temperature'] =   calc['phase-state']['temperature']['value']
    params['pressure_xx'] =   uc.value_unit(calc['phase-state']['pressure-xx'])
    params['pressure_yy'] =   uc.value_unit(calc['phase-state']['pressure-yy'])
    params['pressure_zz'] =   uc.value_unit(calc['phase-state']['pressure-zz'])
    
    if full is True:
        if 'error' in calc:
            params['status'] = calc['status']
            params['error'] = calc['error']
            params['a_mean'] = np.nan
            params['a_std'] = np.nan
            params['b_mean'] = np.nan
            params['b_std'] = np.nan
            params['c_mean'] = np.nan
            params['c_std'] = np.nan
            params['E_coh_mean'] = np.nan
            params['E_coh_std'] = np.nan
            params['T_mean'] = np.nan
            params['T_std'] = np.nan
            params['Pxx_mean'] = np.nan
            params['Pxx_std'] = np.nan
            params['Pyy_mean'] = np.nan
            params['Pyy_std'] = np.nan
            params['Pzz_mean'] = np.nan
            params['Pzz_std'] = np.nan            
        
        elif 'status' in calc:
            params['status'] = calc['status']
            params['error'] = np.nan
            params['a_mean'] = np.nan
            params['a_std'] = np.nan
            params['b_mean'] = np.nan
            params['b_std'] = np.nan
            params['c_mean'] = np.nan
            params['c_std'] = np.nan
            params['E_coh_mean'] = np.nan
            params['E_coh_std'] = np.nan
            params['T_mean'] = np.nan
            params['T_std'] = np.nan
            params['Pxx_mean'] = np.nan
            params['Pxx_std'] = np.nan
            params['Pyy_mean'] = np.nan
            params['Pyy_std'] = np.nan
            params['Pzz_mean'] = np.nan
            params['Pzz_std'] = np.nan   
            
        else:
            params['status'] = np.nan
            params['error'] = np.nan
            
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