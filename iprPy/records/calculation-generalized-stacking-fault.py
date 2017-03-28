from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

import pandas as pd

from iprPy.tools import aslist

def schema():
    dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(dir, 'record-calculation-generalized-stacking-fault.xsd')

def todict(record, full=True):

    model = DM(record)

    calc = model['calculation-generalized-stacking-fault']
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
    params['numshifts1'] = calc['calculation']['run-parameter']['stackingfault_numshifts1']
    params['numshifts2'] = calc['calculation']['run-parameter']['stackingfault_numshifts2']

    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    
    params['load'] =          '%s %s' % (calc['system-info']['artifact']['format'],
                                         calc['system-info']['artifact']['file'])
    params['prototype'] =     calc['system-info']['artifact']['family']
    params['symbols'] =       aslist(calc['system-info']['symbols'])
    
    params['stackingfault_key'] = calc['stacking-fault']['key']
    params['stackingfault_id'] =  calc['stacking-fault']['id']
    params['shiftvector1'] = calc['stacking-fault']['atomman-stacking-fault-parameters']['shift-vector-1']
    params['shiftvector2'] = calc['stacking-fault']['atomman-stacking-fault-parameters']['shift-vector-2']
    
    params['status'] = calc.get('status', 'finished')
    
    if full is True:
        if params['status'] == 'error':
            params['gsf_plot'] = np.nan
                 
        
        elif params['status'] == 'not calculated':
            params['gsf_plot'] = np.nan
            
        else:
            params['error'] = np.nan
            plot = calc['stacking-fault-relation']
            params['gsf_plot'] = pd.DataFrame({'shift1': plot['shift-vector-1-fraction'],
                                               'shift2': plot['shift-vector-2-fraction'],
                                               'energy': uc.value_unit(plot['energy']),
                                               'separation': uc.value_unit(plot['plane-separation'])})
        
    return params 
    
