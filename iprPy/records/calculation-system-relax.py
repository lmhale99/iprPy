from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-calculation-system-relax.xsd')

def todict(record, full=True):

    model = DM(record)

    calc = model['calculation-system-relax']
    params = {}
    params['calc_key'] =     calc['key']
    params['calc_script'] =  calc['calculation']['script']
    params['strainrange'] =  calc['calculation']['run-parameter']['strain-range']
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
            params['initial_a'] = np.nan
            params['initial_b'] = np.nan
            params['initial_c'] = np.nan
            params['final_a'] = np.nan
            params['final_b'] = np.nan
            params['final_c'] = np.nan
            params['E_cohesive'] = np.nan
            params['C'] = np.nan
        
        elif 'status' in calc:
            params['status'] = calc['status']
            params['error'] = np.nan
            params['initial_a'] = np.nan
            params['initial_b'] = np.nan
            params['initial_c'] = np.nan
            params['final_a'] = np.nan
            params['final_b'] = np.nan
            params['final_c'] = np.nan
            params['E_cohesive'] = np.nan
            params['C'] = np.nan
            
        else:
            params['status'] = np.nan
            params['error'] = np.nan
            init = calc['as-constructed-atomic-system']
            params['initial_a'] = uc.value_unit(init.find('a'))
            try:    params['initial_b'] = uc.value_unit(init.find('b'))
            except: params['initial_b'] = params['initial_a']
            try:    params['initial_c'] = uc.value_unit(init.find('c'))
            except: params['initial_c'] = params['initial_a']
         
            final = calc['relaxed-atomic-system']
            params['final_a'] = uc.value_unit(final.find('a'))
            try:    params['final_b'] = uc.value_unit(final.find('b'))
            except: params['final_b'] = params['final_a']
            try:    params['final_c'] = uc.value_unit(final.find('c'))
            except: params['final_c'] = params['final_a']    
            params['E_cohesive'] = uc.value_unit(calc['cohesive-energy'])    
            params['C'] = am.ElasticConstants(model=calc)
        
    return params 