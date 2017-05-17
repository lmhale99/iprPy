from DataModelDict import DataModelDict as DM

import atomman as am
import atomman.unitconvert as uc
import numpy as np

from iprPy.tools import aslist

def todict(record, full=True, flat=False):

    model = DM(record)

    calc = model['calculation-grain-boundary-search']
    params = {}
    params['calc_key'] =      calc['key']
    params['calc_script'] =   calc['calculation']['script']
    params['potential_key'] = calc['potential']['key']
    params['potential_id'] =  calc['potential']['id']
    params['symbols'] =       aslist(calc['system-info']['symbols'])
    params['x_axis_1'] =      calc['grain-1']['crystallographic-axes']['x-axis']
    params['y_axis_1'] =      calc['grain-1']['crystallographic-axes']['y-axis']
    params['z_axis_1'] =      calc['grain-1']['crystallographic-axes']['z-axis']
    params['x_axis_2'] =      calc['grain-2']['crystallographic-axes']['x-axis']
    params['y_axis_2'] =      calc['grain-2']['crystallographic-axes']['y-axis']
    params['z_axis_2'] =      calc['grain-2']['crystallographic-axes']['z-axis']
    
    params['status'] = calc.get('status', 'finished')
    
    if full is True:
        if params['status'] == 'error':
            params['error'] = calc['error']
        
        elif params['status'] == 'not calculated':
            pass
            
        else:
            params['E_gb'] = uc.value_unit(calc['lowest-energy']['E_gb'])
        
    return params 