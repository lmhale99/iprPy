from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-calculation-dislocation-monopole.xsd')

def todict(record, full=True):

    model = DM(record)

    calc = model['calculation-dislocation-monopole']
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
    
    params['annealtemperature'] = calc['calculation']['run-parameter']['annealtemperature']

    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    
    params['load'] =          '%s %s' % (calc['system-info']['artifact']['format'],
                                         calc['system-info']['artifact']['file'])
    params['prototype'] =     calc['system-info']['artifact']['family']
    params['symbols'] =       aslist(calc['system-info']['symbols'])
    
    params['dislocation_key'] = calc['dislocation-monopole']['key']
    params['dislocation_id'] =  calc['dislocation-monopole']['id']
    
    params['status'] = calc.get('status', 'finished')
    
    if full is True:
        if params['status'] == 'error':
            params['error'] = calc['error']
            params['C'] = np.nan
            params['preln'] = np.nan
            params['K_tensor'] = np.nan
                 
        
        elif params['status'] == 'not calculated':
            params['error'] = np.nan
            params['C'] = np.nan
            params['preln'] = np.nan
            params['K_tensor'] = np.nan
            
        else:
            params['error'] = np.nan
            params['C'] = am.ElasticConstants(model=model)
            params['preln'] = uc.value_unit(calc['Stroh-pre-ln-factor'])
            params['K_tensor'] = np.empty((3,3))
            
            for kterm in calc['Stroh-K-tensor']:
                i = int(kterm['ij'][0]) - 1
                j = int(kterm['ij'][2]) - 1
                params['K_tensor'][i,j] = uc.value_unit(kterm['coefficient'])
                params['K_tensor'][j,i] = uc.value_unit(kterm['coefficient'])

    return params 
    
