from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-calculation-system-relax.xsd')

def todict(record):

    model = DM(record)

    calc = model['calculation-system-relax']
    params = {}
    params['calc_key'] =      calc['calculation']['id']
    params['calc_id'] =       calc['calculation']['script']
    params['strain_range'] =  calc['calculation']['run-parameter']['strain-range']
    params['load_options'] =  calc['calculation']['run-parameter']['load_options']
    params['size_mults'] =    calc['calculation']['run-parameter']['size-multipliers']
    params['size_mults'] =    np.array([params['size_mults']['a'], 
                                        params['size_mults']['b'], 
                                        params['size_mults']['c']])
    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    params['load'] =          '%s %s' % (calc['system-info']['artifact']['format'],
                                         calc['system-info']['artifact']['file'])
    params['prototype'] =     calc['system-info']['artifact']['family']
    params['symbols'] =       calc['system-info']['symbols']
    params['temperature'] =   calc['phase-state']['temperature']['value']
    params['pressure_xx'] =   uc.value_unit(calc['phase-state']['pressure-xx'])
    params['pressure_yy'] =   uc.value_unit(calc['phase-state']['pressure-yy'])
    params['pressure_zz'] =   uc.value_unit(calc['phase-state']['pressure-zz'])
    
    try:    init = calc['as-constructed-atomic-system']
    except: pass
    else:
        params['initial_a'] = uc.value_unit(init.find('a'))
        try:    params['initial_b'] = uc.value_unit(init.find('b'))
        except: params['initial_b'] = params['initial_a']
        try:    params['initial_c'] = uc.value_unit(init.find('c'))
        except: params['initial_c'] = params['initial_a']
            
    try:    final = calc['relaxed-atomic-system']
    except: pass
    else:
        params['final_a'] = uc.value_unit(final.find('a'))
        try:    params['final_b'] = uc.value_unit(final.find('b'))
        except: params['final_b'] = params['final_a']
        try:    params['final_c'] = uc.value_unit(final.find('c'))
        except: params['final_c'] = params['final_a']    
        params['E_cohesive'] = uc.value_unit(calc['cohesive-energy'])    
        params['C'] = am.ElasticConstants(model=calc)
        
    return params 