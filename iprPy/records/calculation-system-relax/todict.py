from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def todict(record, full=True, flat=False):

    model = DM(record)

    calc = model['calculation-system-relax']
    params = {}
    params['calc_key'] =            calc['key']
    params['calc_script'] =         calc['calculation']['script']
    params['iprPy_version'] =       calc['calculation']['iprPy-version']
    params['LAMMPS_version'] =      calc['calculation']['LAMMPS-version']
    
    params['strainrange'] =  calc['calculation']['run-parameter']['strain-range']
    
    sizemults =              calc['calculation']['run-parameter']['size-multipliers']
    
    params['potential_LAMMPS_key'] =    calc['potential-LAMMPS']['key']
    params['potential_LAMMPS_id'] =     calc['potential-LAMMPS']['id']
    params['potential_key'] =           calc['potential-LAMMPS']['potential']['key']
    params['potential_id'] =            calc['potential-LAMMPS']['potential']['id']
    
    params['load_file'] =       calc['system-info']['artifact']['file']
    params['load_style'] =      calc['system-info']['artifact']['format']
    params['load_options'] =    calc['system-info']['artifact']['load_options']
    params['family'] =          calc['system-info']['family']
    symbols =                   aslist(calc['system-info']['symbol'])
    
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
            
            if flat is True:
                for C in calc['elastic-constants'].aslist('C'):
                    params['C'+str(C['ij'][0])+str(C['ij'][2])] = uc.value_unit(C['stiffness'])
            else:
                params['C'] = am.ElasticConstants(model=calc)
        
    return params 