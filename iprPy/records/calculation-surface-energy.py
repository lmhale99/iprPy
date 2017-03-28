from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-calculation-surface-energy.xsd')

def todict(record, full=True):

    model = DM(record)

    calc = model['calculation-surface-energy']
    params = {}
    params['calc_key'] =     calc['key']
    params['calc_script'] =  calc['calculation']['script']
    params['load_options'] = calc['calculation']['run-parameter']['load_options']
    params['sizemults'] =    calc['calculation']['run-parameter']['size-multipliers']
    params['sizemults'] =    np.array([params['sizemults']['a'], 
                                       params['sizemults']['b'], 
                                       params['sizemults']['c']])
    params['energytolerance']= calc['calculation']['run-parameter']['energytolerance']
    params['forcetolerance'] = calc['calculation']['run-parameter']['forcetolerance']
    params['maxiterations']  = calc['calculation']['run-parameter']['maxiterations']
    params['maxevaluations'] = calc['calculation']['run-parameter']['maxevaluations']
    params['maxatommotion']  = calc['calculation']['run-parameter']['maxatommotion']

    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    
    params['load'] =          '%s %s' % (calc['system-info']['artifact']['format'],
                                         calc['system-info']['artifact']['file'])
    params['prototype'] =     calc['system-info']['artifact']['family']
    params['symbols'] =       aslist(calc['system-info']['symbols'])
    
    params['surface_key'] = calc['free-surface']['key']
    params['surface_id'] =  calc['free-surface']['id']
    
    params['status'] = calc.get('status', 'finished')
    
    if full is True:
        if params['status'] == 'error':
            params['error'] = calc['error']
            params['E_coh'] = np.nan
            params['gamma_fs'] = np.nan
                 
        
        elif params['status'] == 'not calculated':
            params['error'] = np.nan
            params['E_coh'] = np.nan
            params['gamma_fs'] = np.nan
            
        else:
            params['error'] = np.nan
            params['E_coh'] = uc.value_unit(calc['cohesive-energy'])
            params['gamma_fs'] = uc.value_unit(calc['free-surface-energy'])
        
    return params 
    
